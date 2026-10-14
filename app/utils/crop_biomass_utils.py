"""
crop_biomass_utils.py
──────────────────────────────────────────────────────────────────────────────
Biomasse aérienne par culture, à partir des indices Sentinel-2 (cultures
annuelles + cacao) ou d'une équation allométrique (café).

| Culture | Formule                                      | Indice(s)     |
| ------- | -------------------------------------------- | ------------- |
| Maize   | 45.2 + 310.5 × NDVI                          | NDVI          |
| Rice    | 120.3 + 250.7 × EVI                          | EVI           |
| Wheat   | -80 + 400 × NDVI + 180 × SAVI                | NDVI + SAVI   |
| Cocoa   | 25 + 280 × NDVI + x × NDII                   | NDVI + NDII   |

Cultures pérennes — équations allométriques (kg de biomasse sèche par plant),
utilisées quand le diamètre (et la hauteur si requise) sont fournis :

| Culture          | Formule                                              | Source                              |
| ---------------- | ---------------------------------------------------- | ----------------------------------- |
| Coffee Robusta   | 0.2811 × D^2.0635                                    | Arifin 2001 (Sumberjaya, robusta)   |
| Coffee Arabica   | 10^(−1.15 + 1.66·log10(D15) + 0.54·log10(H))         | Segura, Kanninen & Suárez 2006      |
| Coffee Liberica  | Robusta (même genre, pas d'équation propre trouvée)  | —                                   |
| Coffee (inconnu) | 0.0673 × (ρ × D² × H)^0.976                          | Chave et al. 2014                   |
| Cocoa            | 0.1208 × D^1.98                                      | Yuliasmara et al. 2009              |
| Oil Palm         | (0.0976 × H + 0.0706) × 1000, H = hauteur du stipe   | ICRAF / Khasanah — à vérifier       |
| Rubber, Avocado, | 0.0673 × (ρ × D² × H)^0.976 avec ρ par espèce        | Chave et al. 2014 (pantropical)     |
| Macadamia        |                                                      |                                     |

Hypothèses (à confirmer / recalibrer localement) :
  - Les régressions indice → biomasse donnent une biomasse sèche en g/m²
    (1 g/m² = 0.01 t/ha). Résultat borné à 0 (pas de biomasse négative quand
    le NDVI est très bas, ex. wheat sur sol nu).
  - NDII = (B08 - B11) / (B08 + B11) : c'est exactement le NDMI déjà calculé
    par l'evalscript Sentinel (sentinel_utils.py), on le réutilise.
  - Café : D = diamètre de la tige (cm) ; arabica : D15 = diamètre à 15 cm du
    sol. Chave et al. (2014) reste le repli quand la variété est inconnue.
  - Pas d'équation publiée trouvée pour l'avocatier, le macadamia ni l'hévéa :
    Chave 2014 avec une densité de bois indicative par espèce, à recalibrer.
  - Cacao : le coefficient x du NDII n'a pas été fourni. COCOA_NDII_COEF vaut 0
    tant qu'il n'est pas calibré (la formule se réduit alors au terme NDVI).
"""

import math

from app.utils.tree_co2_utils import calculate_biomass_and_co2

G_M2_TO_T_HA = 0.01

# ⚠️ Coefficient "x" de la formule cacao, à renseigner dès qu'il est connu.
COCOA_NDII_COEF = 0.0

# Chave et al. (2014) : AGB = 0.0673 × (ρ D² H)^0.976
COFFEE_CHAVE_A   = 0.0673
COFFEE_CHAVE_EXP = 0.976
COFFEE_DEFAULT_WOOD_DENSITY = 0.6  # g/cm³, valeur indicative Coffea spp. — surcharger si mesurée

# Densités de bois indicatives (g/cm³) pour Chave 2014 — surcharger si mesurées.
DEFAULT_WOOD_DENSITY = {
    'rubber':    0.56,   # Hevea brasiliensis
    'avocado':   0.60,   # Persea americana
    'macadamia': 0.70,   # Macadamia integrifolia
}


def _maize(ix):
    return 45.2 + 310.5 * ix['ndvi']


def _rice(ix):
    return 120.3 + 250.7 * ix['evi']


def _wheat(ix):
    return -80 + 400 * ix['ndvi'] + 180 * ix['savi']


def _cocoa(ix):
    return 25 + 280 * ix['ndvi'] + COCOA_NDII_COEF * ix['ndmi']


# indices = clés des lignes Sentinel (_parse_response) ; 'ndmi' sert de NDII.
INDEX_MODELS = {
    'maize': {'indices': ('ndvi',),        'fn': _maize, 'formula': '45.2 + 310.5 × NDVI'},
    'rice':  {'indices': ('evi',),         'fn': _rice,  'formula': '120.3 + 250.7 × EVI'},
    'wheat': {'indices': ('ndvi', 'savi'), 'fn': _wheat, 'formula': '-80 + 400 × NDVI + 180 × SAVI'},
    'cocoa': {'indices': ('ndvi', 'ndmi'), 'fn': _cocoa,
              'formula': f'25 + 280 × NDVI + {COCOA_NDII_COEF} × NDII'},
}



def _chave(d_cm, h_m, rho):
    return COFFEE_CHAVE_A * (rho * d_cm ** 2 * h_m) ** COFFEE_CHAVE_EXP


def _robusta(d_cm, h_m, rho):
    return 0.2811 * d_cm ** 2.0635


def _arabica(d_cm, h_m, rho):
    return 10 ** (-1.15 + 1.66 * math.log10(d_cm) + 0.54 * math.log10(h_m))


# Équations allométriques (kg de biomasse sèche par plant).
# needs : mesures obligatoires ; rho : densité du bois par défaut (Chave).
ALLOMETRIC_MODELS = {
    'coffee_robusta': {
        'fn': _robusta, 'needs': ('dbh_cm',),
        'formula': '0.2811 × D^2.0635 (D = stem diameter, cm)',
        'source': 'Arifin (2001), robusta coffee, Sumberjaya, Indonesia',
    },
    'coffee_arabica': {
        'fn': _arabica, 'needs': ('dbh_cm', 'height_m'),
        'formula': '10^(−1.15 + 1.66·log10(D15) + 0.54·log10(H)) '
                   '(D15 = diameter 15 cm above ground, cm; H = height, m)',
        'source': 'Segura, Kanninen & Suárez (2006), Agroforestry Systems',
    },
    'coffee_liberica': {
        'fn': _robusta, 'needs': ('dbh_cm',),
        'formula': '0.2811 × D^2.0635 (robusta equation, no Liberica-specific model published)',
        'source': 'Arifin (2001), applied by analogy',
    },
    'coffee_mixed': {
        'fn': lambda d, h, rho: (_robusta(d, h, rho) + _arabica(d, h, rho)) / 2,
        'needs': ('dbh_cm', 'height_m'),
        'formula': 'mean of the Robusta and Arabica equations',
        'source': 'Arifin (2001) + Segura et al. (2006)',
    },
    'coffee': {
        'fn': _chave, 'needs': ('dbh_cm', 'height_m'), 'rho': COFFEE_DEFAULT_WOOD_DENSITY,
        'formula': f'{COFFEE_CHAVE_A} × (ρ × D² × H)^{COFFEE_CHAVE_EXP}',
        'source': 'Chave et al. (2014), pantropical',
    },
    'cocoa': {
        'fn': lambda d, h, rho: 0.1208 * d ** 1.98, 'needs': ('dbh_cm',),
        'formula': '0.1208 × D^1.98 (D = diameter at breast height, cm)',
        'source': 'Yuliasmara, Wibawa & Prawoto (2009), Coffee and Cocoa Research Journal',
    },
    'oil_palm': {
        'fn': lambda d, h, rho: (0.0976 * h + 0.0706) * 1000.0, 'needs': ('height_m',),
        'formula': '(0.0976 × H + 0.0706) Mg × 1000 (H = trunk height, m)',
        'source': 'ICRAF oil palm equation (Khasanah et al.), coefficients to be verified',
    },
    **{
        key: {
            'fn': _chave, 'needs': ('dbh_cm', 'height_m'), 'rho': rho,
            'formula': f'{COFFEE_CHAVE_A} × (ρ × D² × H)^{COFFEE_CHAVE_EXP}, ρ = {rho} g/cm³',
            'source': 'Chave et al. (2014), pantropical; no species-specific equation published',
        }
        for key, rho in DEFAULT_WOOD_DENSITY.items()
    },
}

SUPPORTED_CROPS = tuple(dict.fromkeys((*INDEX_MODELS, *ALLOMETRIC_MODELS)))

# Noms de Crop.name rencontrés (EN/FR, variétés) → clé de modèle. Le café est
# résolu à part (variété) avant les autres cultures.
_CROP_ALIASES = {
    'maize': ('maize', 'corn', 'maïs', 'mais'),
    'rice':  ('rice', 'paddy', 'riz'),
    'wheat': ('wheat', 'blé', 'ble'),
    'cocoa': ('cocoa', 'cacao'),
    'oil_palm': ('oil palm', 'palm oil', 'palmier', 'elaeis'),
    'rubber': ('rubber', 'hevea', 'hévéa', 'caoutchouc'),
    'avocado': ('avocado', 'avocat', 'persea'),
    'macadamia': ('macadamia', 'macademia'),
}
_COFFEE_ALIASES = ('coffee', 'café', 'cafe', 'arabica', 'robusta', 'liberica')


def _coffee_key(name):
    has_robusta, has_arabica = 'robusta' in name, 'arabica' in name
    if has_robusta and has_arabica:
        return 'coffee_mixed'
    if has_robusta:
        return 'coffee_robusta'
    if has_arabica:
        return 'coffee_arabica'
    if 'liberica' in name:
        return 'coffee_liberica'
    return 'coffee'


def is_coffee(crop_key):
    return bool(crop_key) and crop_key.startswith('coffee')


def resolve_crop_key(crop_name):
    """'Coffee Arabica' → 'coffee_arabica', 'Maïs' → 'maize'. None si culture non supportée."""
    if not crop_name:
        return None
    name = str(crop_name).strip().lower()
    if any(a in name for a in _COFFEE_ALIASES):
        return _coffee_key(name)
    for key, aliases in _CROP_ALIASES.items():
        if any(a in name for a in aliases):
            return key
    return None


def _index_value(row, idx):
    """Accepte les lignes brutes (float) et le format guest {value, raw, oob, tier}."""
    v = row.get(idx)
    return v.get('value') if isinstance(v, dict) else v


def biomass_from_indices(crop_key, row):
    """
    Biomasse (g/m²) d'une ligne d'indices pour une culture "indice". Renvoie
    None si un indice requis manque (nuages) — jamais d'exception sur une ligne.
    """
    model = INDEX_MODELS[crop_key]
    ix = {}
    for idx in model['indices']:
        val = _index_value(row, idx)
        if val is None:
            return None
        ix[idx] = float(val)
    return max(0.0, model['fn'](ix))


def coffee_agb_per_tree_kg(dbh_cm, height_m, wood_density=COFFEE_DEFAULT_WOOD_DENSITY):
    """AGB d'un caféier (kg) — Chave et al. (2014)."""
    return _chave(dbh_cm, height_m, wood_density)


def allometric_agb_per_plant_kg(crop_key, dbh_cm=None, height_m=None, wood_density=None):
    """AGB (kg) d'un plant avec l'équation de sa culture. ValueError si une mesure manque."""
    model = ALLOMETRIC_MODELS[crop_key]
    given = {'dbh_cm': dbh_cm, 'height_m': height_m}
    missing = [n for n in model['needs'] if not given[n] or given[n] <= 0]
    if missing:
        raise ValueError(', '.join(missing))
    return model['fn'](dbh_cm, height_m, wood_density or model.get('rho'))


def compute_crop_biomass(crop_name, history_rows, area_ha,
                         dbh_cm=None, height_m=None, wood_density=None, number_of_trees=None):
    """
    Point d'entrée : biomasse de la parcelle pour la culture donnée.

    history_rows : lignes Sentinel {date, ndvi, evi, savi, ndmi, ...} (brutes ou guest)
    area_ha      : surface de la parcelle (ha)
    Pérennes     : dbh_cm, height_m (selon l'équation), wood_density, number_of_trees

    Retourne (result_dict, error_message).
    """
    crop_key = resolve_crop_key(crop_name)
    if not crop_key:
        return None, (f"No biomass model for crop '{crop_name}'. "
                      f"Supported crops: {', '.join(SUPPORTED_CROPS)}.")
    if not area_ha or area_ha <= 0:
        return None, 'Could not compute parcel area'

    has_measures = dbh_cm not in (None, '') or height_m not in (None, '')
    if crop_key in ALLOMETRIC_MODELS and (crop_key not in INDEX_MODELS or has_measures):
        try:
            dbh_cm = float(dbh_cm) if dbh_cm not in (None, '') else None
            height_m = float(height_m) if height_m not in (None, '') else None
            wood_density = float(wood_density) if wood_density not in (None, '') else None
            number_of_trees = int(number_of_trees) if number_of_trees not in (None, '') else None
        except (TypeError, ValueError):
            return None, 'dbh_cm, height_m, wood_density and trees must be numbers.'
        model = ALLOMETRIC_MODELS[crop_key]
        try:
            per_tree_kg = allometric_agb_per_plant_kg(crop_key, dbh_cm, height_m, wood_density)
        except ValueError:
            labels = {'dbh_cm': 'dbh_cm (stem diameter, cm)', 'height_m': 'height_m (height, m)'}
            needed = ' and '.join(labels[n] for n in model['needs'])
            return None, f'{crop_name} biomass requires {needed}.'
        if not number_of_trees:
            return None, f'{crop_name} biomass requires the number of trees (FarmData.number_of_tree or ?trees=).'
        rho = wood_density or model.get('rho')
        agb_total_kg = per_tree_kg * number_of_trees
        result = calculate_biomass_and_co2(agb_total_kg)
        result.update({
            'crop':              crop_key,
            'crop_name':         crop_name,
            'method':            'allometric',
            'formula':           model['formula'],
            'source':            model['source'],
            'inputs':            {'wood_density': rho, 'dbh_cm': dbh_cm, 'height_m': height_m,
                                  'number_of_trees': number_of_trees},
            'agb_per_tree_kg':   round(per_tree_kg, 4),
            'area_ha':           round(area_ha, 4),
            'agb_t_per_ha':      round(agb_total_kg / 1000.0 / area_ha, 4),
        })
        return result, None

    model = INDEX_MODELS[crop_key]
    history = []
    for row in history_rows or []:
        g_m2 = biomass_from_indices(crop_key, row)
        if g_m2 is not None:
            history.append({
                'date':         row.get('date'),
                'biomass_g_m2': round(g_m2, 2),
                'agb_t_per_ha': round(g_m2 * G_M2_TO_T_HA, 4),
                **{idx: _index_value(row, idx) for idx in model['indices']},
            })
    if not history:
        needed = ' + '.join(i.upper() if i != 'ndmi' else 'NDII' for i in model['indices'])
        return None, f'No cloud-free {needed} reading available for this parcel'

    history.sort(key=lambda h: h['date'] or '')
    latest = history[-1]
    agb_total_kg = latest['agb_t_per_ha'] * area_ha * 1000.0
    result = calculate_biomass_and_co2(agb_total_kg)
    result.update({
        'crop':          crop_key,
        'crop_name':     crop_name,
        'method':        'satellite_index',
        'formula':       model['formula'],
        'indices_used':  {idx: latest[idx] for idx in model['indices']},
        'index_date':    latest['date'],
        'biomass_g_m2':  latest['biomass_g_m2'],
        'agb_t_per_ha':  latest['agb_t_per_ha'],
        'area_ha':       round(area_ha, 4),
        'history':       history,
    })
    if crop_key == 'cocoa' and COCOA_NDII_COEF == 0:
        result['warning'] = 'NDII coefficient (x) not calibrated yet: cocoa biomass uses the NDVI term only.'
    return result, None
