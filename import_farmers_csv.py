# ═══════════════════════════════════════════════════════════════════════════════
# Import des fermiers d'un export KoboToolbox (ex. « data-uganda-ALL FARMERS
# 19.9.23.csv ») : une ligne = une parcelle → Farm + Points (polygone) + FarmData.
#
#   python import_farmers_csv.py <fichier.csv>            (simulation)
#   python import_farmers_csv.py <fichier.csv> --commit   (écrit en base)
#
# Chaque coopérative reçoit son propre compte (User) qui possède ses fermes ;
# les fermiers sans coopérative ont aussi le leur. L'admin peut ensuite
# rattacher une coopérative à un autre compte (page Cooperatives).
# Identifiants des comptes créés : <fichier>_accounts.csv (SENSIBLE).
#
# Sans --commit, rien n'est écrit : le script produit seulement le rapport
# <fichier>_import_report.csv (une ligne par ligne du CSV : statut + motifs).
# Relancer le script est sans danger : une parcelle déjà importée (même
# fermier, même nom, même centroïde) est ignorée.
#
# Cas traités (constatés dans l'export du 19.9.23) :
#   - lignes décalées (texte multi-ligne mal échappé)      → rejetées
#   - consent = no                                          → ignorées
#   - farm_boundaries tronqué (limite de cellule Excel)     → polygone lu dans
#     field_geom (WKB complet), repli sur farm_boundaries puis sur le point GPS
#   - polygones auto-intersectés / points répétés           → réparés (make_valid)
#   - aucun district dans le CSV                            → déduit du centroïde
#     (limites geoBoundaries 2020, app/data/uganda_admin), sous-comté aussi
#   - farmer_id non unique (692 ids partagés par des personnes différentes),
#     ids détruits par Excel (6.164E+12)                    → le farmer_id n'est
#     PAS la clé : doublon = même personne + même parcelle
#   - téléphones sans 0 initial (9 chiffres), tronqués (8), « 0 », « 7 » → 256XXXXXXXXX ou vide
#   - national_id « NIL », « None », « CM », « UGANDAN »…   → vide
#   - coopératives écrites de 10 façons (Ltd/Limited, casse, ponctuation)
#                                                           → un FarmerGroup par nom normalisé
#   - cultures « Coffee », « COFFEE », « Coffe », « Coffee field »… → table crop ;
#     Robusta / Arabica selon l'altitude (option --arabica-above)
#   - tailles en notation scientifique / aberrantes         → surface du polygone
# ═══════════════════════════════════════════════════════════════════════════════

import argparse
import csv
import warnings
import json
import math
import os
import re
import sys
import unicodedata
import secrets
from collections import Counter, defaultdict
from datetime import datetime

from werkzeug.security import generate_password_hash
from shapely import wkb
from shapely.geometry import MultiPolygon, Point as ShpPoint, Polygon, shape
from shapely.ops import transform
from shapely.strtree import STRtree
from shapely.validation import make_valid

csv.field_size_limit(10 ** 9)
warnings.filterwarnings("ignore", category=DeprecationWarning)
THIS_YEAR = datetime.now().year

HERE = os.path.dirname(os.path.abspath(__file__))
ADMIN_DIR = os.path.join(HERE, 'app', 'data', 'uganda_admin')

NULLS = {'', 'null', 'none', 'nil', 'n/a', 'na', 'nan', '-', '0', 'not available',
         'not available for now', 'no', 'nothing'}
UGANDA_BBOX = (29.4, -1.6, 35.1, 4.4)          # lon_min, lat_min, lon_max, lat_max
MAX_DISTRICT_DISTANCE_KM = 10                  # centroïde hors de tout district (frontière, lac)
MIN_AREA_M2 = 20                               # en dessous : polygone inexploitable
MAX_AREA_HA = 500                              # au-dessus : saisie GPS aberrante
BATCH = 500

ACRE_TO_HA = 0.40468564224                    # total_farm_size est en acres (ratio constant 2.471)

GENDERS = {'male': 'Male', 'm': 'Male', 'female': 'Female', 'f': 'Female'}
NO_COOP_RE = re.compile(r'^(|0|n ?a|non|none|nil|null|no|nothing|private|self|single|alone|personal|myself|'
                        r'individual(ly)?( farmers?)?|independent|none of the above|not applicable|'
                        r'(not|non|none) ?(a )?member|no cooperative)$')
INDEPENDENT_GROUP = 'Independent farmers (no cooperative)'
OTHER_GROUP = 'Other cooperatives (fewer than {n} farmers)'
MIN_GROUP_SIZE = 5            # en dessous (après fusion des fautes de frappe) : groupe « Other »
FUZZY_RATIO = 0.88            # similarité pour rattacher une variante à une grande coopérative
# Variantes confirmées d'une même coopérative (trop éloignées pour la fusion floue).
COOP_ALIASES = [
    # Cawodisa = Cowadisa (confirmé) ; couvre COWDISA, KAWODISA, Cowadise, « CAWODISA PM »…
    (re.compile(r'^[ck][ao]w[aos]?dis\w*\b.*$'), 'cawodisa'),
]
# Exportateurs nationaux : toujours un compte et un groupe propres, même si un client
# (ex. zomboArabica en prod) a déjà créé un groupe du même nom pour ses fermiers.
OWN_ACCOUNT_GROUPS = {'kawacom', 'kyagalanyi', 'great lakes coffee company'}

# Noms geoBoundaries → noms de la table district.
DISTRICT_ALIASES = {'ssembabule': 'sembabule', 'kalanga': 'kalangala', 'kitagwenga': 'kitagwenda',
                    'rubirzi': 'rubirizi'}
NOT_DISTRICTS = {'Lake Victoria'}
# Districts récents absents de la table : région officielle pour la création.
NEW_DISTRICT_REGIONS = {
    'Buhweju': 'West', 'Kakumiro': 'West', 'Kazo': 'West', 'Kikuube': 'West', 'Rwampara': 'West',
    'Kassanda': 'Central', 'Omoro': 'North', 'Karenga': 'North', 'Madi Okollo': 'North',
    'Obongi': 'North', 'Pakwach': 'North', 'Terego': 'North', 'Nabilatuk': 'East',
}

# Variante → nom exact dans la table crop (le café est tranché par l'altitude).
CROP_PATTERNS = [
    (re.compile(r'robusta'), 'Coffee Robusta'),
    (re.compile(r'arabica'), 'Coffee Arabica'),
    (re.compile(r'c[ao]+f+e|kawa'), 'COFFEE'),
    (re.compile(r'cocoa|cacao'), 'Cocoa'),
    (re.compile(r'maize|corn'), 'Maize'),
    (re.compile(r'av[oa]c[ao]do|ovacado|avacado'), 'Hass Avocado'),
    (re.compile(r'macad[ae]mia'), 'Macademia'),
    (re.compile(r'sunflower'), 'Sunflower'),
    (re.compile(r'sweet ?potato'), 'Sweet Potato'),
    (re.compile(r'irish|potato'), 'Potato'),
    (re.compile(r'tomato'), 'Tomato'),
    (re.compile(r'millet'), 'Millet'),
    (re.compile(r'sorghum'), 'Sorghum'),
    (re.compile(r'g[\s-]?nut|groundnut|peanut'), 'Groundnut'),
    (re.compile(r'ginger'), 'Ginger'),
    (re.compile(r'pineapple'), 'Pineapple'),
    (re.compile(r'soy'), 'Soya Bean'),
]


# ── Nettoyage des champs ─────────────────────────────────────────────────────

def clean(v):
    """Supprime retours à la ligne, caractères de remplacement, espaces multiples."""
    if v is None:
        return ''
    v = unicodedata.normalize('NFKC', str(v)).replace('�', '')
    return re.sub(r'\s+', ' ', v).strip()


def is_null(v):
    return clean(v).lower() in NULLS


def title(v, keep_acronyms=False):
    """Casse « Nom Propre » ; keep_acronyms : UCDA, BCU restent en capitales."""
    v = clean(v)
    def fix(w):
        if keep_acronyms and w.isupper() and len(w) <= 5:
            return w
        return w[:1].upper() + w[1:].lower() if w.isupper() or w.islower() else w
    return ' '.join(fix(w) for w in v.split())


def person_name(d):
    parts = [title(re.sub(r'[^\w\s\'.-]', '', d.get(k, ''))) for k in ('first_name', 'surname')]
    parts = [p for p in parts if p and not is_null(p)]
    return ' '.join(parts)[:255]


def phone(v, warn):
    raw = clean(v)
    if is_null(raw):
        return None
    digits = re.sub(r'\D', '', raw.split('/')[0].split(',')[0])
    if digits.startswith('256') and len(digits) == 12:
        return digits
    if digits.startswith('0') and len(digits) == 10:
        return '256' + digits[1:]
    if len(digits) == 9 and digits[0] in '237':
        return '256' + digits
    warn.append(f'phone ignored ({raw})')
    return None


NIN_RE = re.compile(r'^C[MF][0-9A-Z]{10,14}$')


def national_id(v, farmer_id, warn):
    raw = re.sub(r'[\s.-]', '', clean(v)).upper()
    if is_null(raw) or raw in ('CM', 'CF', 'UGANDAN', 'UGANDA') or raw == farmer_id:
        return None
    if NIN_RE.match(raw):
        if len(raw) != 14:
            warn.append(f'NIN has {len(raw)} chars (14 expected)')
        return raw[:20]
    if len(raw) >= 6 and raw.isalnum():
        warn.append(f'non-standard ID kept ({raw})')
        return raw[:20]
    return None


def external_id(v, warn):
    raw = clean(v).upper()
    if is_null(raw):
        return None
    if re.match(r'^\d+(\.\d+)?E\+\d+$', raw):
        warn.append(f'farmer_id destroyed by Excel ({raw})')
        return None
    return raw[:100]


def parse_float(v):
    try:
        f = float(clean(v))
        return f if math.isfinite(f) else None
    except ValueError:
        return None


def parse_date(v):
    v = clean(v)
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y'):
        try:
            d = datetime.strptime(v[:10], fmt).date()
            return d if 1950 <= d.year <= THIS_YEAR else None
        except ValueError:
            continue
    return None


def coop_key(v):
    v = clean(v).lower()
    v = re.sub(r'\bco[\s-]?op(erative)?s?\b', 'cooperative', v)
    v = re.sub(r'\b(ltd|limited|ltd\.)\b', 'limited', v)
    v = re.sub(r'organis', 'organiz', v)
    v = re.sub(r'\bsoc\b', 'society', v)
    v = re.sub(r'[^a-z0-9 ]', ' ', v)
    v = re.sub(r'\s+', ' ', v).strip()
    for pattern, canonical in COOP_ALIASES:
        v = pattern.sub(canonical, v)
    return '' if NO_COOP_RE.match(v) else v


def resolve_groups(parcels):
    """
    Nom de groupe final de chaque parcelle :
      - pas de coopérative                   → INDEPENDENT_GROUP
      - faute de frappe d'une grande coop    → cette coop (similarité ≥ FUZZY_RATIO)
      - coop de moins de MIN_GROUP_SIZE      → OTHER_GROUP
    Libellé d'une coop = sa variante d'écriture la plus fréquente.
    """
    from difflib import SequenceMatcher
    counts, variants = Counter(), defaultdict(Counter)
    for p in parcels:
        k = p['farm']['coop_key']
        counts[k] += 1
        variants[k][p['farm']['coop_raw']] += 1
    big = [k for k, n in counts.most_common() if k and n >= 20]
    target = {}
    for k, n in counts.items():
        if not k:
            target[k] = INDEPENDENT_GROUP
            continue
        if n < 20:
            best = max(big, key=lambda b: SequenceMatcher(None, k, b).ratio(), default=None)
            if best and SequenceMatcher(None, k, best).ratio() >= FUZZY_RATIO:
                target[k] = best
                continue
        target[k] = k
    merged = Counter()
    for k, n in counts.items():
        merged[target[k]] += n
    labels = {}
    for k in counts:
        t = target[k]
        if t == INDEPENDENT_GROUP:
            labels[k] = INDEPENDENT_GROUP
        elif merged[t] < MIN_GROUP_SIZE:
            labels[k] = OTHER_GROUP.format(n=MIN_GROUP_SIZE)
        else:
            labels[k] = (variants[t].most_common(1)[0][0] or t.title())[:255]
    for p in parcels:
        p['farm']['group'] = labels[p['farm']['coop_key']]
        raw = p['farm']['coop_raw']
        if labels[p['farm']['coop_key']] != raw and raw and not is_null(raw):
            p['warn'].append(f'cooperative "{raw}" → "{p["farm"]["group"]}"')


# ── Géométrie ────────────────────────────────────────────────────────────────

def _largest_polygon(g):
    if g is None or g.is_empty:
        return None
    if not g.is_valid:
        g = make_valid(g)
    if isinstance(g, Polygon):
        return g
    polys = [p for p in getattr(g, 'geoms', []) if isinstance(p, Polygon)]
    polys += [q for p in getattr(g, 'geoms', []) if isinstance(p, MultiPolygon) for q in p.geoms]
    return max(polys, key=lambda p: p.area) if polys else None


def _from_wkb(hexstr):
    try:
        g = wkb.loads(bytes.fromhex(clean(hexstr)))
    except Exception:
        return None
    return _largest_polygon(transform(lambda x, y, z=None: (x, y), g))   # WKB = (lon, lat)


def _from_odk(text):
    """« lat lon alt précision, lat lon alt précision, ... » (format ODK geoshape)."""
    pts = []
    for chunk in clean(text).split(','):
        p = chunk.split()
        if len(p) >= 2:
            lat, lon = parse_float(p[0]), parse_float(p[1])
            if lat is not None and lon is not None and not (lat == 0 and lon == 0):
                pts.append((lon, lat))
    pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
    if len(set(pts)) < 3:
        return None
    return _largest_polygon(Polygon(pts))


def _in_uganda(lon, lat):
    x0, y0, x1, y1 = UGANDA_BBOX
    return x0 <= lon <= x1 and y0 <= lat <= y1


def area_ha(poly):
    """Surface (ha) en projection équivalente locale — suffisant pour une parcelle."""
    lat0 = math.radians(poly.centroid.y)
    k = 111_320.0
    proj = transform(lambda x, y, z=None: (x * k * math.cos(lat0), y * k), poly)
    return proj.area / 10_000


def parcel_geometry(d, warn):
    """(polygone ou None, (lon, lat), altitude m ou None) ; None si aucune position utilisable."""
    gps = clean(d.get('gps_location')).split()
    alt = parse_float(gps[2]) if len(gps) >= 3 else None
    for source, poly in (('field_geom', lambda: _from_wkb(d.get('field_geom', ''))),
                         ('farm_boundaries', lambda: _from_odk(d.get('farm_boundaries', '')))):
        p = poly()
        if p is None:
            continue
        c = p.centroid
        if not _in_uganda(c.x, c.y):
            warn.append(f'{source} outside Uganda, ignored')
            continue
        a = area_ha(p)
        if a * 10_000 < MIN_AREA_M2:
            warn.append(f'{source} too small ({a * 10_000:.0f} m²), ignored')
            continue
        if a > MAX_AREA_HA:
            warn.append(f'{source} too large ({a:.0f} ha), ignored')
            continue
        if source != 'field_geom':
            warn.append('polygon from farm_boundaries (field_geom unreadable)')
        return p, (c.x, c.y), alt
    if len(gps) >= 2:
        lat, lon = parse_float(gps[0]), parse_float(gps[1])
        if lat is not None and lon is not None and _in_uganda(lon, lat):
            warn.append('no usable polygon: GPS point only')
            return None, (lon, lat), alt
    return None, None, alt


def ring_points(poly):
    """Sommets [(lon, lat)] sans le point de fermeture (l'appli referme elle-même)."""
    coords = [(round(x, 8), round(y, 8)) for x, y, *_ in poly.exterior.coords]
    if len(coords) > 1 and coords[0] == coords[-1]:
        coords = coords[:-1]
    return [c for i, c in enumerate(coords) if i == 0 or c != coords[i - 1]]


# ── Districts / sous-comtés (point-in-polygon) ───────────────────────────────

class AdminLookup:
    def __init__(self, path, name_key='shapeName'):
        feats = [f for f in json.load(open(path, encoding='utf-8'))['features']
                 if f['properties'][name_key] not in NOT_DISTRICTS]
        self.geoms = [shape(f['geometry']) for f in feats]
        self.names = [f['properties'][name_key] for f in feats]
        self.tree = STRtree(self.geoms)

    def find(self, lon, lat, max_km=0):
        pt = ShpPoint(lon, lat)
        for i in self.tree.query(pt):
            if self.geoms[i].covers(pt):
                return self.names[i], 0.0
        if max_km:
            i = self.tree.nearest(pt)
            km = self.geoms[i].distance(pt) * 111.32
            if km <= max_km:
                return self.names[i], km
        return None, None


def norm_name(v):
    n = re.sub(r'[^a-z]', '', clean(v).lower().replace('district', ''))
    return DISTRICT_ALIASES.get(n, n)


# ── Lecture du CSV ───────────────────────────────────────────────────────────

def read_rows(path):
    with open(path, encoding='utf-8-sig', errors='replace', newline='') as fh:
        reader = csv.reader(fh)
        header = [clean(h) for h in next(reader)]
        cols = [(i, h) for i, h in enumerate(header) if h]
        for line_no, row in enumerate(reader, start=2):
            yield line_no, {h: (row[i] if i < len(row) else '') for i, h in cols}


def prepare(path, args, districts, subcounties, crops):
    """Analyse tout le CSV sans toucher la base : (parcelles valides, rapport)."""
    report, parcels = [], []
    seen = {}
    for line_no, d in read_rows(path):
        warn = []
        base = {'line': line_no, 'csv_id': clean(d.get('id')), 'farmer_id': clean(d.get('farmer_id')),
                'name': person_name(d)}

        def reject(reason, status='rejected'):
            report.append({**base, 'status': status, 'farm_id': '', 'reason': reason,
                           'warnings': '; '.join(warn)})

        if clean(d.get('country')).lower() != 'uganda' or not clean(d.get('id')).isdigit():
            reject('malformed row (shifted columns in the export)')
            continue
        if clean(d.get('consent')).lower() != 'yes':
            reject('farmer did not give consent', 'skipped_no_consent')
            continue

        ext_id = external_id(d.get('farmer_id'), warn)
        name = base['name'] or ext_id
        if not name:
            reject('no farmer name and no farmer_id')
            continue
        if not base['name']:
            warn.append('no name: farmer_id used as name')

        poly, centroid, alt = parcel_geometry(d, warn)
        if centroid is None:
            reject('no usable location (polygon and GPS point missing or outside Uganda)')
            continue
        lon, lat = centroid

        district_name, km = districts.find(lon, lat, MAX_DISTRICT_DISTANCE_KM)
        if not district_name:
            reject(f'location {lat:.5f}, {lon:.5f} is not inside a Uganda district')
            continue
        if km:
            warn.append(f'district = nearest ({district_name}, {km:.1f} km)')
        subcounty, _ = subcounties.find(lon, lat, 2)
        village = title(d.get('village'))
        subcounty = subcounty or (village if not is_null(village) else None) or 'Unknown'

        geolocation = f'{lat:.6f}, {lon:.6f}'
        dup_key = (norm_name(name), ext_id or '', geolocation)
        if dup_key in seen:
            reject(f'duplicate of CSV line {seen[dup_key]} (same farmer, same parcel)', 'skipped_duplicate')
            continue
        seen[dup_key] = line_no

        area = area_ha(poly) if poly is not None else None
        size = parse_float(d.get('total_farm_size'))          # acres
        size = size * ACRE_TO_HA if size else None
        if area is None and size and 0.001 <= size <= MAX_AREA_HA:
            area = size
        elif area is not None and size and not (0.5 <= size / area <= 2):
            warn.append(f'total_farm_size {size:.2f} ha ≠ polygon {area:.2f} ha: polygon kept')

        crop_raw = clean(d.get('main_crop')).lower()
        crop = None
        for rx, target in CROP_PATTERNS:
            if rx.search(crop_raw):
                crop = target
                break
        if crop == 'COFFEE':
            arabica = alt is not None and alt >= args.arabica_above
            crop = 'Coffee Arabica' if arabica else 'Coffee Robusta'
            warn.append(f'coffee type from altitude ({alt:.0f} m)' if alt is not None
                        else 'coffee type unknown (no altitude): Robusta assumed')
        if crop and crop not in crops:
            warn.append(f'crop {crop} missing from crop table')
            crop = None
        if not crop and crop_raw and not is_null(crop_raw):
            warn.append(f'main_crop "{clean(d.get("main_crop"))}" not in crop table: no FarmData')

        parcels.append({
            'line': line_no, 'base': base, 'warn': warn,
            'farm': {
                'name': name, 'subcounty': subcounty[:255], 'district': district_name,
                'coop_key': coop_key(d.get('cooperative_name')),
                'coop_raw': title(d.get('cooperative_name'), keep_acronyms=True),
                'geolocation': geolocation,
                'phonenumber': phone(d.get('phone_number'), warn),
                'gender': GENDERS.get(clean(d.get('gender')).lower()),
                'cin': national_id(d.get('national_id'), ext_id, warn),
                'government_id': ext_id,
                'country': 'Uganda',
            },
            'points': ring_points(poly) if poly is not None else [],
            'farmdata': crop and {
                'crop': crop,
                'land_type': (clean(d.get('land_use')).replace('_', ' ').capitalize() or None)
                             if not is_null(d.get('land_use')) else None,
                'tilled_land_size': round(area, 4) if area else None,
                'planting_date': parse_date(d.get('estimate_planting_date')),
                'expected_yield': parse_float(d.get('main_crop_yield')) if not is_null(d.get('main_crop_yield')) else None,
            },
        })
    return parcels, report


# ── Écriture en base ─────────────────────────────────────────────────────────

def next_farm_number(db, Farm, prefix):
    """Plus grand suffixe numérique existant (comparaison NUMÉRIQUE, pas texte)."""
    best = 0
    for (fid,) in db.session.query(Farm.farm_id).filter(Farm.farm_id.like(f'{prefix}%')):
        tail = fid[len(prefix):]
        if tail.isdigit():
            best = max(best, int(tail))
    return best + 1


ACCOUNT_EMAIL_DOMAIN = 'farmergroups.invalid'   # domaine réservé : jamais d'envoi réel


def slugify(v, max_len=60):
    s = re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', clean(v)).encode('ascii', 'ignore').decode().lower())
    return s.strip('-')[:max_len].strip('-') or 'group'


class Accounts:
    """
    Un compte (User) par coopérative ; un pour les fermiers sans coopérative,
    un pour les petites coopératives regroupées. Un groupe déjà en base et
    déjà rattaché à un compte non-admin garde ce compte.
    Identification stable entre deux lancements : l'email <slug>@farmergroups.invalid.
    """

    def __init__(self, db, User, commit, reset_passwords=False):
        self.db, self.User, self.commit = db, User, commit
        self.reset_passwords = reset_passwords
        self.used_usernames = {u for (u,) in db.session.query(User.username)}
        self.used_id_starts = {(i or '').upper() for (i,) in db.session.query(User.id_start)}
        self.by_label = {}
        self.created = []           # (user, mot de passe en clair, libellé)

    def _id_start(self, label):
        letters = re.sub(r'[^A-Z]', '', unicodedata.normalize('NFKD', label).upper())
        base = (letters or 'COOP')[:4].ljust(4, 'X')
        cand, n = base, 2
        while cand in self.used_id_starts:
            cand, n = f'{base}{n}', n + 1
        self.used_id_starts.add(cand)
        return cand

    def _username(self, slug):
        cand, n = slug, 2
        while cand in self.used_usernames:
            cand, n = f'{slug}-{n}', n + 1
        self.used_usernames.add(cand)
        return cand

    def for_group(self, label, group):
        if label in self.by_label:
            return self.by_label[label]
        User = self.User
        acc = None
        if group is not None and group.created_by:
            owner = User.query.get(group.created_by)
            if owner and not owner.is_admin and owner.id_start:
                acc = owner
                if self.reset_passwords and owner.email.endswith('@' + ACCOUNT_EMAIL_DOMAIN):
                    password = secrets.token_urlsafe(9)
                    if self.commit:
                        acc.password = generate_password_hash(password, method='pbkdf2:sha256')
                    self.created.append((acc, password, label))
        if acc is None:
            slug = slugify(label)
            email = f'{slug}@{ACCOUNT_EMAIL_DOMAIN}'
            acc = User.query.filter_by(email=email).first()
            if acc is not None and self.reset_passwords:
                password = secrets.token_urlsafe(9)
                if self.commit:
                    acc.password = generate_password_hash(password, method='pbkdf2:sha256')
                self.created.append((acc, password, label))
            elif acc is None:
                password = secrets.token_urlsafe(9)
                acc = User(username=self._username(slug), email=email,
                           password=generate_password_hash(password, method='pbkdf2:sha256'),
                           company_name=label[:255], user_type='farmer', is_admin=False,
                           id_start=self._id_start(label), permissions={})
                self.created.append((acc, password, label))
                if self.commit:
                    self.db.session.add(acc)
                    self.db.session.flush()
        self.by_label[label] = acc
        return acc


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('csv')
    ap.add_argument('--commit', action='store_true', help='write to the database (otherwise dry run)')
    ap.add_argument('--arabica-above', type=float, default=1600,
                    help='altitude (m) from which coffee is recorded as Arabica (default 1600)')
    ap.add_argument('--limit', type=int, help='import only the first N valid parcels (test)')
    ap.add_argument('--reset-passwords', action='store_true',
                    help='give a new password to cooperative accounts created by an earlier run '
                         '(use when their credentials file was lost)')
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    from app import create_app, db
    from app.models import Crop, District, Farm, FarmData, FarmerGroup, Point, User

    app = create_app()
    with app.app_context():
        crops = {c.name: c.id for c in Crop.query.all()}
        print('Reading boundaries…')
        districts = AdminLookup(os.path.join(ADMIN_DIR, 'districts.geojson'))
        subcounties = AdminLookup(os.path.join(ADMIN_DIR, 'subcounties.geojson'))
        print('Analysing CSV…')
        parcels, report = prepare(args.csv, args, districts, subcounties, crops)
        resolve_groups(parcels)          # sur tout le fichier, avant --limit
        if args.limit:
            parcels = parcels[:args.limit]

        # Districts : correspondance par nom normalisé, création des manquants.
        db_districts = {norm_name(x.name): x for x in District.query.all()}
        missing_districts = sorted({p['farm']['district'] for p in parcels
                                    if norm_name(p['farm']['district']) not in db_districts})

        # Coopératives : fautes de frappe fusionnées, groupes existants réutilisés.
        gkey = lambda name: coop_key(name) or clean(name).lower()
        db_groups = {}
        for g in FarmerGroup.query.order_by(FarmerGroup.id):
            if gkey(g.name) in OWN_ACCOUNT_GROUPS:
                owner = User.query.get(g.created_by) if g.created_by else None
                if not (owner and owner.email.endswith('@' + ACCOUNT_EMAIL_DOMAIN)):
                    continue        # groupe homonyme d'un client : on ne s'y rattache pas
            db_groups.setdefault(gkey(g.name), g)
        labels = sorted({p['farm']['group'] for p in parcels})
        missing_groups = [l for l in labels if gkey(l) not in db_groups]

        # Parcelles déjà en base (relance du script) : même nom + centroïde (+ farmer_id).
        existing = {(norm_name(n), g or '', geo) for n, g, geo in
                    db.session.query(Farm.name, Farm.government_id, Farm.geolocation)}
        todo = []
        for p in parcels:
            f = p['farm']
            if (norm_name(f['name']), f['government_id'] or '', f['geolocation']) in existing:
                report.append({**p['base'], 'status': 'skipped_existing', 'farm_id': '',
                               'reason': 'already in the database', 'warnings': '; '.join(p['warn'])})
            else:
                todo.append(p)

        # Un compte par coopérative (créé seulement avec --commit).
        accounts = Accounts(db, User, args.commit, reset_passwords=args.reset_passwords)
        group_account = {l: accounts.for_group(l, db_groups.get(gkey(l))) for l in labels}
        farms_per_group = Counter(p['farm']['group'] for p in parcels)
        acc_out = None

        def write_credentials():
            """Identifiants en clair (SENSIBLE, à ne pas commiter) : écrits dès que les
            comptes existent en base, pour ne pas les perdre si l'import s'arrête."""
            path = os.path.splitext(args.csv)[0] + f'_accounts_{datetime.now():%Y%m%d-%H%M%S}.csv'
            with open(path, 'w', encoding='utf-8-sig', newline='') as fh:
                w = csv.writer(fh)
                w.writerow(['cooperative', 'username', 'email', 'password', 'id_start', 'farms'])
                for acc, password, label in sorted(accounts.created, key=lambda x: -farms_per_group[x[2]]):
                    w.writerow([label, acc.username, acc.email, password if args.commit else '(dry run)',
                                acc.id_start, farms_per_group[label]])
            return path

        if not args.commit and accounts.created:
            acc_out = write_credentials()

        if args.commit:
            for name in missing_districts:
                d = District(name=name, region=NEW_DISTRICT_REGIONS.get(name, 'Unknown'))
                db.session.add(d)
                db_districts[norm_name(name)] = d
            for label in labels:
                acc = group_account[label]
                g = db_groups.get(gkey(label))
                if g is None:
                    g = FarmerGroup(name=label, description='Imported from KoboToolbox CSV')
                    db.session.add(g)
                    db_groups[gkey(label)] = g
                owner = User.query.get(g.created_by) if g.created_by else None
                if owner is None or owner.is_admin:
                    g.created_by = g.modified_by = acc.id
            db.session.commit()
            if accounts.created:
                acc_out = write_credentials()
                print(f'Credentials written: {acc_out}')

            numbers = {}
            now = datetime.utcnow()
            for start in range(0, len(todo), BATCH):
                chunk = todo[start:start + BATCH]
                try:
                    farms, points, datas = [], [], []
                    for p in chunk:
                        f = p['farm']
                        acc = group_account[f['group']]
                        uid = acc.id
                        prefix = f'{acc.id_start}FA'
                        if prefix not in numbers:
                            numbers[prefix] = next_farm_number(db, Farm, prefix)
                        farm_id = f'{prefix}{numbers[prefix]:04d}'
                        numbers[prefix] += 1
                        district_id = db_districts[norm_name(f['district'])].id
                        farms.append(dict(
                            farm_id=farm_id, name=f['name'], subcounty=f['subcounty'],
                            farmergroup_id=db_groups[gkey(f['group'])].id,
                            district_id=district_id, geolocation=f['geolocation'],
                            phonenumber=f['phonenumber'], gender=f['gender'], cin=f['cin'],
                            government_id=f['government_id'], country=f['country'],
                            created_by=uid, modified_by=uid, date_created=now, date_updated=now))
                        points += [dict(longitude=lon, latitude=lat, owner_type='farmer', owner_id=farm_id,
                                        district_id=district_id, created_by=uid, modified_by=uid,
                                        date_created=now, date_updated=now) for lon, lat in p['points']]
                        if p['farmdata']:
                            fd = p['farmdata']
                            datas.append(dict(farm_id=farm_id, crop_id=crops[fd['crop']],
                                              land_type=fd['land_type'], tilled_land_size=fd['tilled_land_size'],
                                              planting_date=fd['planting_date'], expected_yield=fd['expected_yield'],
                                              created_by=uid, modified_by=uid, date_created=now, date_updated=now))
                        p['farm_id'] = farm_id
                    db.session.bulk_insert_mappings(Farm, farms)
                    db.session.bulk_insert_mappings(Point, points)
                    db.session.bulk_insert_mappings(FarmData, datas)
                    db.session.commit()
                    for p in chunk:
                        report.append({**p['base'], 'status': 'created', 'farm_id': p['farm_id'],
                                       'reason': '', 'warnings': '; '.join(p['warn'])})
                except Exception as e:
                    db.session.rollback()
                    for p in chunk:
                        report.append({**p['base'], 'status': 'error', 'farm_id': '',
                                       'reason': f'database error, batch rolled back: {e}'[:500],
                                       'warnings': '; '.join(p['warn'])})
                print(f'  {min(start + BATCH, len(todo))}/{len(todo)}')
        else:
            for p in todo:
                report.append({**p['base'], 'status': 'would_create', 'farm_id': '',
                               'reason': '', 'warnings': '; '.join(p['warn'])})

        out = os.path.splitext(args.csv)[0] + '_import_report.csv'
        report.sort(key=lambda r: r['line'])
        with open(out, 'w', encoding='utf-8-sig', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=['line', 'csv_id', 'farmer_id', 'name', 'status',
                                               'farm_id', 'reason', 'warnings'])
            w.writeheader()
            w.writerows(report)

        print('\n── Summary ' + ('(written to the database)' if args.commit else '(DRY RUN, nothing written)'))
        for status, n in Counter(r['status'] for r in report).most_common():
            print(f'  {status:20s} {n}')
        print(f'  polygons              {sum(1 for p in todo if p["points"])} '
              f'({sum(len(p["points"]) for p in todo)} points)')
        print(f'  FarmData              {sum(1 for p in todo if p["farmdata"])} '
              f'{dict(Counter(p["farmdata"]["crop"] for p in todo if p["farmdata"]))}')
        print(f'  districts to create   {len(missing_districts)} {missing_districts}')
        print(f'  farmer groups to create {len(missing_groups)}')
        print(f'  accounts to create    {len(accounts.created)}'
              + (f' (credentials: {acc_out})' if accounts.created else ''))
        print('  top groups', Counter(p['farm']['group'] for p in todo).most_common(12))
        warn_kinds = Counter(re.sub(r'\(.*?\)|"[^"]*"|\d+(\.\d+)?', '…', w).strip()
                             for p in todo for w in p['warn'])
        print('  warnings:')
        for k, n in warn_kinds.most_common(25):
            print(f'    {n:6d}  {k}')
        print(f'\nReport: {out}')


if __name__ == '__main__':
    main()
