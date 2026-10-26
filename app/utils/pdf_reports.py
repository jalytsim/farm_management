"""
pdf_reports.py
──────────────────────────────────────────────────────────────────────────────
Génération 100 % backend des rapports PDF avec ReportLab.
Aucune dépendance navigateur, aucun HTML à parser.

Rapports disponibles :
  • build_eudr_farm_pdf(farm_id, farm_info, gfw_data)   → bytes
  • build_eudr_forest_pdf(forest_id, forest_info, gfw_data) → bytes
  • build_carbon_farm_pdf(farm_id, farm_info, carbon, coords)     → bytes
  • build_carbon_forest_pdf(forest_id, forest_info, carbon, coords) → bytes
  • build_sat_index_pdf(report_id, farm_info, data, coords)         → bytes
    (carbon = carbon_index_utils.compute_carbon_from_indices, Sentinel-2)

Dépendances Python :
  reportlab  matplotlib  shapely  requests
"""

import io
import os
import base64
import requests
import matplotlib
matplotlib.use('Agg')                     # pas de GUI
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from datetime import datetime
# Alias: reportlab.graphics.shapes.Polygon (importé plus bas) écrasait celui de shapely,
# ce qui faisait échouer le calcul de surface du PDF (Project Area "Not available").
from shapely.geometry import Polygon as ShapelyPolygon

from reportlab.lib              import colors
from reportlab.lib.pagesizes    import A4
from reportlab.lib.units        import mm
from reportlab.lib.styles       import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums        import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus         import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, HRFlowable, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, String, Circle, PolyLine, Polygon
from reportlab.pdfbase          import pdfmetrics
from reportlab.pdfgen.canvas    import Canvas

# ── Palette ───────────────────────────────────────────────────────────────────
GREEN       = colors.HexColor('#2d7a2d')
GREEN_LIGHT = colors.HexColor('#e8f5e9')
GREEN_MED   = colors.HexColor('#a5d6a7')
RED         = colors.HexColor('#c62828')
RED_LIGHT   = colors.HexColor('#ffebee')
ORANGE      = colors.HexColor('#e65100')
ORANGE_LIGHT= colors.HexColor('#fff3e0')
GRAY_BG     = colors.HexColor('#f5f5f5')
GRAY_BORDER = colors.HexColor('#d0e8d0')
BLACK       = colors.HexColor('#1a1a1a')
MUTED       = colors.HexColor('#666666')
WHITE       = colors.white

PAGE_W, PAGE_H = A4
MARGIN         = 18 * mm
CONTENT_W      = PAGE_W - 2 * MARGIN

MAPBOX_TOKEN = (
    'pk.eyJ1IjoidHNpbWlqYWx5IiwiYSI6ImNsejdjNXpqdDA1ZzMybHM1YnU4aWpyaDcifQ'
    '.CSQsCZwMF2CYgE-idCz08Q'
)

DRIVER_MAP = {
    1: 'Commodity driven deforestation',
    2: 'Shifting Agriculture',
    3: 'Forestry',
    4: 'Wildfire',
    5: 'Urbanization',
}


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _styles():
    """Retourne un dict de styles Paragraph réutilisables."""
    base = getSampleStyleSheet()
    def ps(name, **kw):
        kw.setdefault('fontName', 'Helvetica')
        kw.setdefault('textColor', BLACK)
        return ParagraphStyle(name, parent=base['Normal'], **kw)

    return {
        'title'    : ps('title',    fontName='Helvetica-Bold', fontSize=18,
                        alignment=TA_CENTER, spaceAfter=2, textColor=BLACK),
        'subtitle' : ps('subtitle', fontSize=9,  alignment=TA_CENTER, textColor=MUTED),
        'section'  : ps('section',  fontName='Helvetica-Bold', fontSize=10,
                        textColor=GREEN, spaceBefore=6, spaceAfter=4,
                        textTransform='uppercase'),
        'body'     : ps('body',     fontSize=9,  leading=13, spaceAfter=3),
        'body_bold': ps('body_bold',fontName='Helvetica-Bold', fontSize=9),
        'small'    : ps('small',    fontSize=8,  textColor=MUTED),
        'badge_ok' : ps('badge_ok', fontName='Helvetica-Bold', fontSize=10,
                        textColor=colors.HexColor('#1b5e20')),
        'badge_warn':ps('badge_warn',fontName='Helvetica-Bold', fontSize=10,
                        textColor=ORANGE),
        'badge_err' :ps('badge_err', fontName='Helvetica-Bold', fontSize=10,
                        textColor=RED),
    }


def _logo_image(path: str, w=18*mm, h=18*mm):
    """
    Charge un logo PNG/JPG depuis app/static/.
    SVG non supporté par ReportLab — convertir en PNG au préalable.
    """
    if not path:
        return None
    if not os.path.exists(path):
        print(f"[Logo] ABSENT : {path}")
        return None
    try:
        img = Image(path, width=w, height=h)
        img.hAlign = 'CENTER'
        return img
    except Exception as e:
        print(f"[Logo] Erreur : {path} — {e}")
        return None


def _mapbox_image(coordinates: list, width_px=580):
    """
    Télécharge la carte Mapbox satellite (PNG) et la retourne en Image ReportLab.
    coordinates : liste de [lon, lat] (format GeoJSON, pas [lat, lon]).

    Fix encodage : json.dumps → true/false + guillemets doubles corrects.
    """
    import json as _json
    import urllib.parse

    if not coordinates or len(coordinates) < 3:
        print("[Mapbox] Pas de coordonnées valides")
        return None

    try:
        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates],
                },
                "properties": {
                    "stroke":         "#00FF00",
                    "stroke-width":   4,
                    "stroke-opacity": 1,
                    "fill":           "#00FF00",
                    "fill-opacity":   0.15,
                },
            }],
        }

        geojson_str = _json.dumps(geojson, separators=(',', ':'), ensure_ascii=True)
        encoded     = urllib.parse.quote(geojson_str, safe='')

        url = (
            f"https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/static/"
            f"geojson({encoded})/auto/{width_px}x340"
            f"?padding=40"
            f"&access_token={MAPBOX_TOKEN}"
        )

        print(f"[Mapbox] Requête ({len(coordinates)} points)…")
        resp = requests.get(url, timeout=30)
        print(f"[Mapbox] Status : {resp.status_code} | Size : {len(resp.content)} bytes")

        if resp.status_code == 200 and resp.headers.get('content-type', '').startswith('image'):
            buf   = io.BytesIO(resp.content)
            img_w = CONTENT_W
            img_h = img_w * 340 / width_px
            img   = Image(buf, width=img_w, height=img_h)
            return img

        print(f"[Mapbox] Erreur réponse : {resp.text[:400]}")

    except Exception as e:
        print(f"[Mapbox] Exception : {e}")

    return None


def _header_table(logo_left_path, logo_right_path, title: str, subtitle: str) -> Table:
    """
    En-tête du rapport :  logo parrot  |  TITRE  |  logo Agriyields
    Reproduit exactement le header de l'écran (image 1).
    Si un logo est absent, la cellule reste vide (pas d'erreur).
    """
    left  = _logo_image(logo_left_path,  22*mm, 22*mm)
    right = _logo_image(logo_right_path, 22*mm, 22*mm)

    st = _styles()

    # 🟢 MODIFICATION : On crée un style personnalisé pour le titre pour ajouter de l'espace en dessous
    custom_title_style = ParagraphStyle(
        'HeaderTitleCustom',
        parent=st['title'],          # Conserve les propriétés d'origine (couleur, police, taille)
        spaceAfter=6 * mm,           # ⚡ AJOUTÉ : Crée un espace de 6mm entre le titre et le sous-titre
        leading=st['title'].fontSize + 4  # Assure une bonne hauteur de ligne pour éviter les chevauchements
    )

    # Cellule gauche
    left_cell  = left  if left  is not None else Paragraph('', st['body'])
    right_cell = right if right is not None else Paragraph('', st['body'])

    # Cellule centrale : titre + sous-titre
    center_cell = [
        Paragraph(title,    custom_title_style), # 🟢 Utilise le nouveau style avec espace après
        Paragraph(subtitle, st['subtitle']),
    ]

    col_logo   = 28 * mm
    col_center = CONTENT_W - 2 * col_logo

    t = Table(
        [[left_cell, center_cell, right_cell]],
        colWidths=[col_logo, col_center, col_logo],
    )
    t.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',        (0, 0), (0,  0),  'LEFT'),
        ('ALIGN',        (1, 0), (1,  0),  'CENTER'),
        ('ALIGN',        (2, 0), (2,  0),  'RIGHT'),
        ('LINEBELOW',    (0, 0), (-1, -1), 2, GREEN),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 10),
        ('TOPPADDING',   (0, 0), (-1, -1), 6),
    ]))
    return t


def _pie_chart_image(data: dict, size=55*mm) -> Image:
    """
    Génère un pie chart matplotlib et retourne une Image ReportLab.
    data : { 'label': value, ... }
    """
    COLORS = ['#e53935', '#43a047', '#fb8c00', '#00acc1',
              '#8e24aa', '#039be5', '#f4511e', '#00897b']

    labels = list(data.keys())
    values = [abs(v) for v in data.values()]
    total  = sum(values)
    if total == 0:
        values = [1] * len(values)

    fig, ax = plt.subplots(figsize=(4, 3.5), facecolor='white')
    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        colors=COLORS[:len(values)],
        autopct=lambda p: f'{p:.1f}%' if p > 3 else '',
        startangle=140,
        pctdistance=0.75,
        wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'},
    )
    for at in autotexts:
        at.set_fontsize(7)
        at.set_color('white')
        at.set_fontweight('bold')

    legend_patches = [
        mpatches.Patch(color=COLORS[i], label=labels[i])
        for i in range(len(labels))
    ]
    ax.legend(
        handles=legend_patches,
        loc='lower center',
        bbox_to_anchor=(0.5, -0.22),
        ncol=2,
        fontsize=7,
        frameon=False,
    )
    ax.set_aspect('equal')
    plt.tight_layout(pad=0.3)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor='white', transparent=False)
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=size, height=size * 3.5 / 4)


def _section_bar(title: str, styles: dict) -> list:
    """Retourne [HRFlowable, Paragraph] pour un titre de section."""
    return [
        HRFlowable(width=CONTENT_W, thickness=2, color=GREEN,
                   spaceAfter=3, spaceBefore=8),
        Paragraph(title, styles['section']),
    ]


def _info_table(rows: list[tuple], col_w=(55*mm, None)) -> Table:
    """
    Table deux colonnes label / valeur.
    rows : [(label, value), ...]
    """
    cw1 = col_w[0]
    cw2 = col_w[1] or (CONTENT_W - cw1)
    data = [[Paragraph(f'<b>{l}</b>', _styles()['small']),
             Paragraph(str(v) if v else 'N/A', _styles()['body'])]
            for l, v in rows]
    t = Table(data, colWidths=[cw1, cw2])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (0, -1), GREEN_LIGHT),
        ('BACKGROUND',   (1, 0), (1, -1), WHITE),
        ('GRID',         (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
        ('LEFTPADDING',  (0, 0), (-1, -1), 6),
    ]))
    return t


def _compliance_badge_table(status: str, description: str) -> Table:
    """Retourne une table avec le badge de conformité coloré (icône vectorielle + texte)."""
    if status == '100% Compliant':
        bg, fc, icon = GREEN_LIGHT, colors.HexColor('#1b5e20'), _icon_ok()
    elif status == 'Compliant':
        # No forest cover, but tree cover loss detected — compliant, shade-tree planting recommended
        fc = colors.HexColor('#2e7d32')
        bg, icon = GREEN_LIGHT, _icon_ok(color=fc)
    elif status == 'Not Compliant':
        bg, fc, icon = RED_LIGHT, RED, _icon_bad()
    else:
        bg, fc, icon = GRAY_BG, MUTED, _icon_warn(color=MUTED)

    badge_row = _icon_text_row(icon, status, ParagraphStyle(
        'badge', fontName='Helvetica-Bold', fontSize=13, textColor=fc, alignment=TA_LEFT,
    ))
    rows = [[badge_row]]
    if description:
        rows.append([Paragraph(description, _styles()['small'])])
    t = Table(rows, colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (0, -1), bg),
        ('BOX',          (0, 0), (-1, -1), 1, GRAY_BORDER),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ('LEFTPADDING',  (0, 0), (-1, -1), 12),
        ('ROUNDEDCORNERS', [5]),
    ]))
    return t


# ── Icônes vectorielles ──────────────────────────────────────────────────────
# ⚠ NOTE : les glyphes Unicode ✓ ✗ ⚠ et le "2" en indice (₂) ne font PAS partie
# de l'encodage WinAnsi utilisé par les polices Core (Helvetica). ReportLab les
# rend silencieusement invisibles (aucune exception, mais rien ne s'imprime) —
# c'était la cause principale des badges/textes "vides" dans les PDF générés.
# On dessine donc ces icônes en vectoriel (indépendant des polices), et on
# remplace "CO₂" par le tag Paragraph <sub>2</sub> qui produit un vrai indice.

def _icon_ok(size=4.6 * mm, color=None) -> Drawing:
    c = color or colors.HexColor('#1b5e20')
    d = Drawing(size, size)
    d.add(Circle(size / 2, size / 2, size / 2, fillColor=c, strokeColor=None))
    w = max(1.0, size * 0.14)
    d.add(PolyLine(
        points=[size * 0.26, size * 0.52, size * 0.44, size * 0.32, size * 0.76, size * 0.70],
        strokeColor=WHITE, strokeWidth=w, strokeLineCap=1, strokeLineJoin=1,
    ))
    return d


def _icon_bad(size=4.6 * mm, color=None) -> Drawing:
    c = color or RED
    d = Drawing(size, size)
    d.add(Circle(size / 2, size / 2, size / 2, fillColor=c, strokeColor=None))
    w = max(1.0, size * 0.14)
    d.add(PolyLine(points=[size * 0.28, size * 0.28, size * 0.72, size * 0.72],
                    strokeColor=WHITE, strokeWidth=w, strokeLineCap=1))
    d.add(PolyLine(points=[size * 0.72, size * 0.28, size * 0.28, size * 0.72],
                    strokeColor=WHITE, strokeWidth=w, strokeLineCap=1))
    return d


def _icon_warn(size=4.6 * mm, color=None) -> Drawing:
    c = color or ORANGE
    d = Drawing(size, size)
    d.add(Polygon(points=[size * 0.5, size * 0.95, size * 0.03, size * 0.06, size * 0.97, size * 0.06],
                  fillColor=c, strokeColor=None))
    d.add(String(size * 0.5, size * 0.14, '!', fontName='Helvetica-Bold',
                 fontSize=size * 0.5, fillColor=WHITE, textAnchor='middle'))
    return d


def _icon_text_row(icon: Drawing, text: str, text_style: ParagraphStyle, icon_col=9 * mm) -> Table:
    """Ligne icône vectorielle + texte en gras, utilisée par les bannières de statut."""
    row = Table(
        [[icon, Paragraph(f'<b>{text}</b>', text_style)]],
        colWidths=[icon_col, CONTENT_W - icon_col - 28],
    )
    row.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',   (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
    ]))
    return row



def _footer_canvas(canvas, doc):
    """Footer sur chaque page."""
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)
    footer = '© 2025 Agriyields  •  nkusu@agriyields.com  •  Regulation (EU) 2023/1115'
    canvas.drawCentredString(PAGE_W / 2, 10 * mm, footer)
    canvas.setStrokeColor(GRAY_BORDER)
    canvas.line(MARGIN, 14 * mm, PAGE_W - MARGIN, 14 * mm)
    canvas.restoreState()


class _NumberedCanvas(Canvas):
    """Canvas ajoutant 'Page X of Y' en bas de chaque page.

    SimpleDocTemplate ne connaît pas le nombre total de pages tant que le
    document n'est pas entièrement construit : on capture donc l'état de
    chaque page à la volée (showPage), puis on rejoue chaque état une fois
    le total connu, juste avant l'impression finale (save).
    """

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_number(total_pages)
            Canvas.showPage(self)
        Canvas.save(self)

    def _draw_page_number(self, total_pages):
        self.setFont('Helvetica', 8)
        self.setFillColor(MUTED)
        self.drawRightString(PAGE_W - MARGIN, 10 * mm, f'Page {self._pageNumber} of {total_pages}')


# ══════════════════════════════════════════════════════════════════════════════
# CALCULS  (équivalent des calculs JS dans EudrReportSection)
# ══════════════════════════════════════════════════════════════════════════════

def _calc_area_ha(coordinates: list) -> tuple[float, float]:
    """Calcule la superficie en m² et ha depuis des coordonnées GeoJSON."""
    try:
        from shapely.geometry import Polygon
        from shapely.ops import transform
        import pyproj

        poly  = Polygon(coordinates)
        # Projection UTM approximative via pyproj
        try:
            from pyproj import Transformer
            lon_c = sum(c[0] for c in coordinates) / len(coordinates)
            lat_c = sum(c[1] for c in coordinates) / len(coordinates)
            utm_zone = int((lon_c + 180) / 6) + 1
            hemi = 'north' if lat_c >= 0 else 'south'
            proj = f'+proj=utm +zone={utm_zone} +{hemi} +ellps=WGS84'
            transformer = Transformer.from_crs('epsg:4326', proj, always_xy=True)
            poly_utm = transform(transformer.transform, poly)
            area_m2 = poly_utm.area
        except Exception:
            # Fallback : formule de Haversine approximative
            area_m2 = abs(poly.area) * (111_320 ** 2)

        return area_m2, area_m2 / 10_000
    except Exception as e:
        print(f"[_calc_area_ha] échec calcul de surface : {e}")
        return 0.0, 0.0


def _calc_area_ha_simple(coordinates: list) -> tuple[float, float]:
    """Calcul d'aire simplifié sans pyproj (shapely seul, degrés → m² approx)."""
    try:
        poly = ShapelyPolygon(coordinates)
        # Correction latitude : 1 degré lat ≈ 111 320 m, 1 degré lon ≈ 111 320 * cos(lat) m
        import math
        lat_c = sum(c[1] for c in coordinates) / len(coordinates)
        scale = 111_320 * 111_320 * math.cos(math.radians(lat_c))
        area_m2 = abs(poly.area) * scale
        return area_m2, area_m2 / 10_000
    except Exception as e:
        # ⚠ FIX (diagnostic "Project Area 0.00 ha") : cette exception était avalée
        # silencieusement, rendant impossible de savoir pourquoi une surface valide
        # retombait à 0 (anneau non fermé, <3 points, géométrie dégénérée...).
        print(f"[_calc_area_ha_simple] échec calcul de surface sur {len(coordinates) if isinstance(coordinates, list) else '?'} points : {e}")
        return 0.0, 0.0


def _compliance_status(tree_cover_loss: float, has_forest: bool, is_in_protected_area: bool = False) -> dict:
    """
    Règles (ordre de priorité strict) :
    1) Forest cover detected (JRC 2020)                    -> Not Compliant
    2) No forest cover BUT protected area (WDPA/IUCN 1-2)  -> Not Compliant (EUDR Article 10)
    3) No forest cover, not protected, no tree cover loss  -> 100% Compliant
    4) No forest cover, not protected, tree cover loss     -> Compliant
    Le rapport n'affiche que le statut (demande utilisateur) : pas de description.
    """
    if has_forest or is_in_protected_area:
        status = 'Not Compliant'
    elif tree_cover_loss == 0:
        status = '100% Compliant'
    else:
        status = 'Compliant'
    return {'status': status, 'description': ''}


def _get_array_depth(arr):
    depth = 0
    cur = arr
    while isinstance(cur, list):
        depth += 1
        cur = cur[0] if cur else None
    return depth


def _as_float_lists(coords):
    """Tuples → listes, Decimal → float. Les fermes en base arrivent en
    [(Decimal lon, Decimal lat), ...] (map.get_coordinates) : _get_array_depth
    s'arrêtait au tuple, l'anneau était mal détecté et la surface valait 0
    → "declared farm size" ou "Not available" au lieu de la surface GPS."""
    if isinstance(coords, (list, tuple)):
        return [_as_float_lists(c) for c in coords]
    try:
        return float(coords)
    except (TypeError, ValueError):
        return coords


def _get_outer_rings(coords):
    """Anneaux extérieurs, que la géométrie soit Polygon (1 anneau) ou
    MultiPolygon (N anneaux) — miroir de getOuterRings() côté frontend
    (EudrReportSection.jsx). Les trous internes sont ignorés."""
    coords = _as_float_lists(coords)
    if not isinstance(coords, list) or not coords:
        return []
    depth = _get_array_depth(coords)
    if depth == 4:
        return [poly[0] for poly in coords if isinstance(poly, list) and poly]
    if depth == 3:
        return [coords[0]] if coords else []
    if depth == 2:
        return [coords]
    return []

def _extract_eudr_metrics(gfw_data: dict) -> dict:
    """
    Extrait et calcule toutes les métriques EUDR depuis les données GFW brutes.
    gfw_data : dict groupé par dataset (format retourné par /report)
    """
    m = {}

    # Coordonnées
    raw_coords = (
        gfw_data.get('jrc global forest cover', [{}])[0].get('coordinates')
        or gfw_data.get('tree cover loss', [{}])[0].get('coordinates')
        or gfw_data.get('soil carbon', [{}])[0].get('coordinates')
    )
    # ✅ FIX (MultiPolygon) : même logique que getOuterRings() côté frontend —
    # un anneau simple pour l'affichage de la carte, la somme de tous les
    # anneaux pour la surface totale.
    outer_rings = _get_outer_rings(raw_coords)
    m['coordinates'] = outer_rings[0] if outer_rings else []
    if not outer_rings:
        # ⚠ FIX (diagnostic "Project Area 0.00 ha") : sans ce print, un
        # `raw_coords` manquant/mal formé (clé de dataset absente, géométrie
        # vide...) se traduisait silencieusement par une surface à 0.
        print(f"[_extract_eudr_metrics] aucune coordonnée exploitable — raw_coords={raw_coords!r}")

    total_m2 = 0.0
    for ring in outer_rings:
        ring_m2, _ = _calc_area_ha_simple(ring)
        total_m2 += ring_m2
    m['area_m2'] = total_m2
    m['area_ha'] = total_m2 / 10_000

    # Tree cover loss
    tcl = gfw_data.get('tree cover loss', [{}])[0].get('data_fields', {})
    raw_tcl_ha = tcl.get('area__ha', 0) or 0

    # ✅ FIX (annotation PDF) : la perte de couverture ne peut pas dépasser la surface
    # totale de la parcelle. On plafonne et on calcule le ratio (%) une seule fois ici,
    # pour l'afficher sur la ligne "Tree Cover Loss" plutôt que sur "Country Deforestation Risk".
    m['tree_cover_loss_capped'] = False
    if m['area_ha'] > 0 and raw_tcl_ha > m['area_ha']:
        print(
            f"[EUDR] ⚠ Tree cover loss ({raw_tcl_ha} ha) exceeds plot area "
            f"({m['area_ha']:.2f} ha). Capping to plot area — verify upstream data."
        )
        m['tree_cover_loss_ha'] = m['area_ha']
        m['tree_cover_loss_capped'] = True
    else:
        m['tree_cover_loss_ha'] = raw_tcl_ha

    m['tree_cover_loss_ratio'] = (
        min(m['tree_cover_loss_ha'] / m['area_ha'] * 100, 100) if m['area_ha'] else 0
    )

    # JRC Forest cover
    jrc = gfw_data.get('jrc global forest cover', [{}])[0].get('data_fields', {})
    forest_ha = jrc.get('area__ha', 0) or 0
    m['has_forest']      = forest_ha > 0
    m['forest_cover_ha'] = forest_ha
    m['forest_cover_text'] = (
        f'Forest cover detected: {forest_ha:.2f} ha'
        if forest_ha > 0 else 'No forest cover detected'
    )

    # RADD alerts
    radd = gfw_data.get('wur radd alerts', [{}])[0].get('data_fields', {})
    m['radd_ha'] = radd.get('area__ha', 0) or 0

    # WRI average cover
    wri = gfw_data.get('wri tropical tree cover', [{}])[0].get('data_fields', {})
    m['avg_cover'] = wri.get('avg_cover', 0) or 0

    # TSC drivers
    drivers_arr = gfw_data.get('tsc tree cover loss drivers', [{}])
    freq = {}
    for item in drivers_arr:
        df = item.get('data_fields', [])
        if isinstance(df, list):
            for f in df:
                d = f.get('tsc_tree_cover_loss_drivers__driver')
                c = f.get('count', 1)
                if d:
                    freq[d] = freq.get(d, 0) + c
        elif isinstance(df, dict):
            d = df.get('tsc_tree_cover_loss_drivers__driver')
            if d:
                freq[d] = freq.get(d, 0) + 1
    m['driver_freq']    = freq
    m['primary_driver'] = max(freq, key=freq.get) if freq else None
    m['primary_driver_label'] = DRIVER_MAP.get(m['primary_driver'], str(m['primary_driver']) if m['primary_driver'] else 'Unknown')

    # Protected areas
    prot_arr = gfw_data.get('soil carbon', [{}])
    prot_counts = {}
    total_prot  = 0
    for item in prot_arr:
        df = item.get('data_fields', [])
        # ✅ FIX : sans GROUP BY (cf. map.py), un polygone à un seul pixel
        # renvoie un dict unique au lieu d'une liste — géré ici comme les
        # autres blocs (drivers) plus haut dans cette fonction.
        if isinstance(df, dict):
            df = [df]
        if isinstance(df, list):
            for f in df:
                cat   = f.get('wdpa_protected_areas__iucn_cat', 'Unknown')
                count = f.get('count', 1)
                prot_counts[cat] = prot_counts.get(cat, 0) + count
                total_prot      += count
    prot_pct = {}
    if total_prot:
        for k, v in prot_counts.items():
            label = {'0': 'Not in protected area', '1': 'In WDPA protected area',
                     '2': 'In IUCN vulnerable area'}.get(str(k), f'Category {k}')
            prot_pct[label] = f'{v / total_prot * 100:.1f}%'
    m['protected_pct'] = prot_pct or {'Protected area data': 'Not available'}
    # Catégories WDPA/IUCN 1 (in WDPA protected area) et 2 (in IUCN vulnerable
    # area) — cf. label mapping ci-dessus. Utilisé par _compliance_status().
    m['is_in_protected_area'] = any(
        str(k) in ('1', '2') and v > 0 for k, v in prot_counts.items()
    )

    # Cover extent
    extent_arr = gfw_data.get('wri tropical tree cover extent', [])
    grouped    = next((i for i in extent_arr
                       if isinstance(i.get('pixel'), str) and 'grouped' in i['pixel']
                       and isinstance(i.get('data_fields'), list)), None)
    non_zero = 0
    total_pts = 0
    val_counts = []
    if grouped:
        for f in grouped['data_fields']:
            dec   = f.get('wri_tropical_tree_cover_extent__decile', 0)
            count = f.get('count', 0)
            total_pts += count
            if dec and dec != 0:
                non_zero += count
            val_counts.append({'decile': dec, 'count': count})
    m['cover_pct']   = (non_zero / total_pts * 100) if total_pts else 0
    m['cover_count'] = non_zero
    m['val_counts']  = val_counts

    # Indigenous lands
    indig = gfw_data.get('landmark indigenous and community lands', [{}])[0].get('data_fields', [])
    if not indig:
        m['indigenous'] = 'Not known, land is not gazetted'
    else:
        has_land = any(f.get('name') or f.get('value') == 1 for f in (indig if isinstance(indig, list) else []))
        m['indigenous'] = ('Presence of indigenous and community lands'
                           if has_land else 'No presence of indigenous and community lands')

    # Compliance
    m['compliance'] = _compliance_status(m['tree_cover_loss_ha'], m['has_forest'], m['is_in_protected_area'])

    return m


# ══════════════════════════════════════════════════════════════════════════════
# EUDR COMPLIANCE TABLE  (ReportLab)
# ══════════════════════════════════════════════════════════════════════════════

def _farm_area_text(m: dict, farm_info: dict | None = None) -> str:
    """
    Surface de la ferme : polygone GPS en priorité, sinon surface déclarée
    (FarmData.tilled_land_size, en ha) — même règle que dashboard_utils.get_farm_area_ha.
    """
    if m.get('area_ha'):
        return f"{m['area_ha']:.2f} ha  ({m['area_m2']:.0f} m²)"
    info = farm_info or {}
    declared = info.get('farm_size_ha') or info.get('area_ha') or next(
        (c.get('tilled_land_size') for c in (info.get('crops') or []) if c.get('tilled_land_size')), None)
    try:
        declared = float(declared) if declared else None
    except (TypeError, ValueError):
        declared = None
    if declared:
        return f"{declared:.2f} ha  ({declared * 10_000:.0f} m²), declared farm size"
    return 'Not available'


def _eudr_compliance_table(m: dict, farm_info: dict | None = None) -> Table:
    st = _styles()

    def cell(text, bold=False, color=BLACK):
        fn = 'Helvetica-Bold' if bold else 'Helvetica'
        return Paragraph(f'<font name="{fn}">{text}</font>',
                         ParagraphStyle('c', fontName=fn, fontSize=8,
                                        textColor=color, leading=11))

    radd_color = GREEN if m['radd_ha'] == 0 else RED
    cs         = m['compliance']
    cs_color   = (colors.HexColor('#1b5e20') if cs['status'] == '100% Compliant'
                  else colors.HexColor('#2e7d32') if cs['status'] == 'Compliant' else RED)
    fc_color   = ORANGE if m['has_forest'] else GREEN

    # ✅ FIX (rendu PDF) : Paragraph n'interprète pas "\n" comme un retour à la
    # ligne (contrairement à un <br/>) — le texte s'affichait donc écrasé sur
    # une seule ligne. On utilise la balise Paragraph correcte.
    prot_text  = '<br/>'.join(f'{k}: {v}' for k, v in m['protected_pct'].items())
    prot_color = RED if m.get('is_in_protected_area') else GREEN
    vc_text   = ', '.join(
        f'Decile {r["decile"]}: {r["count"]}'
        for r in m['val_counts'] if r['count'] > 0
    ) or 'No data'

    rows = [
        # Header
        [cell('Metric', bold=True), cell('Value / Assessment', bold=True)],
        # Data rows
        [cell('Project Area'),
         cell(_farm_area_text(m, farm_info))],

        [cell('Country Deforestation Risk'),
         cell('STANDARD')],

        [cell('RADD Alert'),
         cell(f"{m['radd_ha']} ha, {'No alert' if m['radd_ha']==0 else 'Alert detected'}",
              color=radd_color)],

        [cell('Forest Cover (JRC 2020)'),
         cell(m['forest_cover_text'], color=fc_color)],

        [cell('EUDR Compliance'),
         cell(cs['status'], bold=True, color=cs_color)],

        [cell('Protected Area Status'),
         cell(prot_text, color=prot_color)],

        [cell('Tree Cover Extent'),
         cell(f"Coverage: {m['cover_pct']:.1f}%, Non-zero pts: {m['cover_count']}<br/>{vc_text}")],

        [cell('Primary Deforestation Driver'),
         cell(m['primary_driver_label'])],

        [cell('Average Tree Cover'),
         cell(f"{m['avg_cover']:.1f}%")],

        [cell('Indigenous & Community Lands'),
         cell(m['indigenous'])],
    ]

    col1 = 55 * mm
    col2 = CONTENT_W - col1
    t    = Table(rows, colWidths=[col1, col2], repeatRows=1)

    style = [
        # Header row
        ('BACKGROUND',   (0, 0), (-1, 0),   GREEN),
        ('TEXTCOLOR',    (0, 0), (-1, 0),   WHITE),
        ('FONTNAME',     (0, 0), (-1, 0),   'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0),   9),
        # Label column
        ('BACKGROUND',   (0, 1), (0, -1),   GREEN_LIGHT),
        # Grid
        ('GRID',         (0, 0), (-1, -1),  0.5, GRAY_BORDER),
        # Padding
        ('TOPPADDING',   (0, 0), (-1, -1),  5),
        ('BOTTOMPADDING',(0, 0), (-1, -1),  5),
        ('LEFTPADDING',  (0, 0), (-1, -1),  6),
        ('VALIGN',       (0, 0), (-1, -1),  'TOP'),
        # Alternate rows
        *[('BACKGROUND', (1, i), (1, i), colors.HexColor('#fafafa'))
          for i in range(2, len(rows), 2)],
    ]
    t.setStyle(TableStyle(style))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# BUILD EUDR FARM PDF
# ══════════════════════════════════════════════════════════════════════════════
def build_eudr_farm_pdf(
    farm_id           : str,
    farm_info         : dict,
    gfw_data          : dict,
    logo_parrot       : str | None = None,
    logo_agri         : str | None = None,
    forest_map_base64 : str | None = None,  # <-- AJOUTÉ : Pour recevoir l'image de la 2ème carte du front
) -> bytes:
    """
    Génère le rapport EUDR pour une ferme.
    Retourne les bytes du PDF.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=22 * mm,
        title=f'EUDR Compliance Report {farm_id}',
        author='Agriyields',
    )
    st   = _styles()
    today = datetime.now().strftime('%d %B %Y')
    m     = _extract_eudr_metrics(gfw_data)
    
    elems = []

    # ── En-tête ──────────────────────────────────────────────────────────────
    subtitle_text = "Report generated based on the Regulation (EU) 2023/1115 on deforestation-free products."
    
    elems.append(_header_table(
        logo_parrot, logo_agri,
        'EUDR COMPLIANCE REPORT',
        subtitle_text
    ))
    elems.append(Spacer(1, 6 * mm))

    # ── Description Dynamique (Header Description) ───────────────────────────
    # 1. Extraction propre des variables
    farm_id_val = farm_info.get('farm_id') or farm_id
    owner_name = farm_info.get('name')
    geolocation = farm_info.get('geolocation')
    
    # Correction de la localisation pour correspondre au format de vos données
    subcounty = farm_info.get('subcounty', '').strip()
    district = farm_info.get('district_name', '').strip()
    location_val = f"{subcounty}, {district}".strip(', ')

    # Extraction de la culture et du type de terrain depuis la liste 'crops'
    crop_name = None
    land_type = None
    if farm_info.get('crops') and len(farm_info['crops']) > 0:
        crop_name = farm_info['crops'][0].get('crop')
        land_type = farm_info['crops'][0].get('land_type')

    # 2. Logique conditionnelle de l'en-tête
    if owner_name and geolocation:
        intro_text = (
            f"This report provides an overview of Farm ID {farm_id_val}, owned by {owner_name}, "
            f"located in {location_val if location_val else 'N/A'}. The farm plays a "
            f"significant role in the local agricultural landscape. With geolocation "
            f"coordinates {geolocation}, the farm specializes in {crop_name if crop_name else 'N/A'} "
            f"and operates within a region characterized by Landtype: {land_type if land_type else 'N/A'}. "
            f"This report outlines the farm's activities, challenges, and opportunities to support "
            f"its continued growth and sustainability."
        )
    else:
        # Texte de repli (Fallback) si les informations de la ferme sont incomplètes
        intro_text = "This report outlines the farm's activities, challenges, natural disaster and opportunities to support its continued growth and sustainability."

    # 3. Ajout au flux ReportLab
    elems.append(Paragraph(intro_text, st['body']))
    elems.append(Spacer(1, 5 * mm))

    # ── Bannière conformité ───────────────────────────────────────────────────
    elems.append(_compliance_badge_table(
        m['compliance']['status'],
        m['compliance']['description'],
    ))
    elems.append(Spacer(1, 5 * mm))

    # ── Farm information ──────────────────────────────────────────────────────
    if farm_info:
        elems += _section_bar('Farm Information', st)
        rows = [
            ('Farm ID',       farm_info.get('farm_id', farm_id)),
            ('Owner',         farm_info.get('name')),
            ('Location',      location_val),
            ('Geolocation',   farm_info.get('geolocation')),
            ('Report Date',   today),
        ]
        if farm_info.get('crops'):
            rows.append(('Primary Crop', farm_info['crops'][0].get('crop', 'N/A')))
            rows.append(('Land Type',    farm_info['crops'][0].get('land_type', 'N/A')))
        rows.append(('Farm Area', _farm_area_text(m, farm_info)))
        elems.append(_info_table(rows))
        elems.append(Spacer(1, 5 * mm))

    # ── Regulatory framework ──────────────────────────────────────────────────
    # Même liste et mêmes textes que le rapport écran (EudrReportSection.jsx) —
    # "Tree Cover Loss" n'y figure plus (demande utilisateur).
    elems += _section_bar('Regulatory Framework (EU) 2023/1115', st)
    elems.append(Paragraph(
        'This report provides a compliance assessment under the European Union Regulation 2023/1115, '
        'which governs the import and export of products associated with deforestation and degradation.',
        st['body']))
    elems.append(Spacer(1, 3 * mm))
    articles = [
        ('1. RADD Alert (Article 2)',
         'Applicable to most parts of Uganda, only parts of Lake Albert region neighbouring DR Congo.'),
        ('2. Forest Cover (Article 2)',
         'EU Joint Research Centre Geostore for checking existence or not of forest cover as of 2020.<br/>'
         '<b>None detected:</b> Plot/Farm is fully compliant with EUDR Law.<br/>'
         '<b>Forest detected:</b> Farm is NOT compliant with EUDR Law, regardless of other indicators.'),
        ('3. Tree Cover Extent (Article 2)',
         'Analysis of tree cover, expressed in deciles (ranging from 0-100), to evaluate forest coverage.'),
        ('4. Tree Cover Loss Drivers (Article 10)',
         'Identifies the primary causes of deforestation or degradation.'),
        ('5. Protected Area (Article 10)',
         'Indicates if the plot is located in a gazetted protected area (national park, wetland, etc.).'),
        ('6. Indigenous and Community Lands (Article 10)',
         'Determines whether the land overlaps with recognized indigenous or community land.'),
    ]
    art_data = [[Paragraph(f'<b>{t}</b>', ParagraphStyle('at', fontName='Helvetica-Bold',
                 fontSize=8, textColor=GREEN, spaceAfter=2)),
                 Paragraph(d, ParagraphStyle('ad', fontName='Helvetica', fontSize=8,
                 textColor=BLACK, leading=11))]
                for t, d in articles]
    art_t = Table(art_data, colWidths=[50 * mm, CONTENT_W - 50 * mm])
    art_t.setStyle(TableStyle([
        ('GRID',          (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ('BACKGROUND',    (0, 0), (0, -1),  GREEN_LIGHT),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
    ]))
    elems.append(art_t)
    elems.append(Spacer(1, 5 * mm))

    # ── Summary compliance table ──────────────────────────────────────────────
    elems += _section_bar('Summary Compliance Table', st)
    elems.append(_eudr_compliance_table(m, farm_info))
    elems.append(Spacer(1, 5 * mm))

    # ── Risk assessment breakdown ─────────────────────────────────────────────
    elems += _section_bar('Risk Assessment Breakdown', st)
    risk_rows = [
        ('Farm Area',               _farm_area_text(m, farm_info)),
        ('Average Tree Cover',      f"{m['avg_cover']:.1f}%"),
        ('RADD Alerts',             f"{m['radd_ha']} ha"),
        ('Primary Driver',          m['primary_driver_label']),
        ('Compliance Status',       m['compliance']['status']),
    ]
    elems.append(_info_table(risk_rows))
    elems.append(Spacer(1, 5 * mm))

    # ── Satellite map (Première carte) ────────────────────────────────────────
    if m['coordinates']:
        map_img = _mapbox_image(m['coordinates'])
        if map_img:
            elems += _section_bar('Plot Map: Satellite View', st)
            elems.append(map_img)
            elems.append(Spacer(1, 5 * mm))

    # ── Forest Heatmap Map (Deuxième carte reçue du frontend) ──────────────────
    if forest_map_base64:
        try:
            if "," in forest_map_base64:
                forest_map_base64 = forest_map_base64.split(",")[1]
            
            img_data = base64.b64decode(forest_map_base64)
            buf_img = io.BytesIO(img_data)
            
            # Intégration propre de la carte générée par StaticForestMap.jsx
            forest_img = Image(buf_img, width=CONTENT_W, height=110 * mm)
            forest_img.hAlign = 'CENTER'
            
            elems += _section_bar('Tree Cover Spatial Analysis: Heatmap View', st)
            elems.append(forest_img)
            elems.append(Spacer(1, 3 * mm))
        except Exception as e:
            print(f"Erreur d'intégration de la carte forestière : {e}")

    doc.build(elems, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas, canvasmaker=_NumberedCanvas)
    return buf.getvalue()



def build_eudr_forest_pdf(
    forest_id  : int | str,
    forest_info: dict,
    gfw_data   : dict,
    logo_parrot: str | None = None,
    logo_agri  : str | None = None,
) -> bytes:
    """Génère le rapport EUDR pour une forêt."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=22 * mm,
        title=f'EUDR Compliance Report Forest {forest_id}',
        author='Agriyields',
    )
    st    = _styles()
    today = datetime.now().strftime('%d %B %Y')
    m     = _extract_eudr_metrics(gfw_data)
    elems = []

    elems.append(_header_table(
        logo_parrot, logo_agri,
        'EUDR COMPLIANCE REPORT FOREST',
        f'Generated on {today}  •  Regulation (EU) 2023/1115',
    ))
    elems.append(Spacer(1, 6 * mm))
    elems.append(_compliance_badge_table(
        m['compliance']['status'], m['compliance']['description'],
    ))
    elems.append(Spacer(1, 5 * mm))

    elems += _section_bar('Forest Information', st)
    rows = [
        ('Forest Name',  forest_info.get('name')),
        ('Tree Type',    forest_info.get('tree_type', 'N/A')),
        ('Date Created', forest_info.get('date_created', 'N/A')),
        ('Last Updated', forest_info.get('date_updated', 'N/A')),
        ('Report Date',  today),
    ]
    if m['area_ha']:
        rows.append(('Forest Area', f"{m['area_ha']:.2f} ha  ({m['area_m2']:.0f} m²)"))
    elems.append(_info_table(rows))
    elems.append(Spacer(1, 5 * mm))

    elems += _section_bar('Summary Compliance Table', st)
    elems.append(_eudr_compliance_table(m))
    elems.append(Spacer(1, 5 * mm))

    if m['coordinates']:
        map_img = _mapbox_image(m['coordinates'])
        if map_img:
            elems += _section_bar('Plot Map: Satellite View', st)
            elems.append(map_img)

    doc.build(elems, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas, canvasmaker=_NumberedCanvas)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# BUILD CARBON FARM PDF
# ══════════════════════════════════════════════════════════════════════════════

def _carbon_table(vals: dict, width: float = CONTENT_W) -> Table:
    """Table des valeurs carbone."""
    BADGE_COLORS = {
        'emissions': colors.HexColor('#e53935'),
        'removals':  colors.HexColor('#43a047'),
        'net_pos':   colors.HexColor('#e53935'),
        'net_neg':   colors.HexColor('#43a047'),
    }

    def badge_cell(val, color):
        return Paragraph(
            f'<font color="white"><b>{val:.4f}</b></font>',
            ParagraphStyle('badge', fontName='Helvetica-Bold', fontSize=9,
                           backColor=color, textColor=WHITE,
                           borderPadding=4, alignment=TA_CENTER)
        )

    def c_and_co2e(c, bold=False):
        b0, b1 = ('<b>', '</b>') if bold else ('', '')
        return [Paragraph(f'{b0}{c:.4f}{b1}', _styles()['body']),
                Paragraph(f'{b0}{c * CO2_PER_C:.4f}{b1}', _styles()['body'])]

    net_c = vals['net_c']
    rows = [
        [Paragraph('<b>Category</b>',                 _styles()['body_bold']),
         Paragraph('<b>Mg C</b>',                     _styles()['body_bold']),
         Paragraph('<b>Mg CO<sub>2</sub>e</b>',       _styles()['body_bold'])],
        [Paragraph('Carbon Emissions (per year)',     _styles()['body']),
         badge_cell(vals['emissions_c'], BADGE_COLORS['emissions']),
         Paragraph(f"{vals['emissions']:.4f}", _styles()['body'])],
        [Paragraph('Carbon Absorption (per year)',    _styles()['body']),
         badge_cell(vals['removals_c'], BADGE_COLORS['removals']),
         Paragraph(f"{vals['removals']:.4f}", _styles()['body'])],
        [Paragraph(f"Carbon Net Emissions (per year): {_sink_label(net_c)}", _styles()['body']),
         badge_cell(net_c, BADGE_COLORS['net_pos'] if net_c >= 0 else BADGE_COLORS['net_neg']),
         Paragraph(f"{vals['net']:.4f}", _styles()['body'])],
        [Paragraph('Carbon Stock (Aboveground)', _styles()['body']), *c_and_co2e(vals['stock_above_c'])],
        [Paragraph('Carbon Stock (Belowground)', _styles()['body']), *c_and_co2e(vals['stock_below_c'])],
    ]
    if vals.get('stock_soc_c') is not None:
        rows.append([Paragraph(f"Soil Organic Carbon ({(vals.get('soc') or {}).get('depth', '0-30cm')})",
                               _styles()['body']), *c_and_co2e(vals['stock_soc_c'])])
    if vals.get('stock_total_c') is not None:
        rows.append([Paragraph('<b>Total Carbon Stock</b>', _styles()['body']),
                     *c_and_co2e(vals['stock_total_c'], bold=True)])

    t = Table(rows, colWidths=[width * 0.52, width * 0.24, width * 0.24])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0),   GREEN),
        ('TEXTCOLOR',    (0, 0), (-1, 0),   WHITE),
        ('GRID',         (0, 0), (-1, -1),  0.5, GRAY_BORDER),
        ('BACKGROUND',   (0, 1), (0, -1),   GRAY_BG),
        ('VALIGN',       (0, 0), (-1, -1),  'MIDDLE'),
        ('TOPPADDING',   (0, 0), (-1, -1),  6),
        ('BOTTOMPADDING',(0, 0), (-1, -1),  6),
        ('LEFTPADDING',  (0, 0), (-1, -1),  8),
        *[('BACKGROUND', (0, i), (0, i), WHITE) for i in range(2, len(rows), 2)],
    ]))
    return t


# Mg CO2e = Mg C × 3.67 (44/12) — même facteur que la chaîne de calcul (tree_co2_utils)
from app.utils.tree_co2_utils import CO2_C_RATIO as CO2_PER_C


def _sink_label(net) -> str:
    """Convention du rapport : net négatif = puits, positif = source."""
    return 'Carbon Source' if net > 0 else 'Carbon Sink' if net < 0 else 'Neutral'


def _carbon_status_badge(carbon: dict) -> Table:
    """Bannière stock total (Mg CO2e) + statut puits / source du flux net —
    factorisée car identique entre le rapport ferme et le rapport forêt."""
    net_c = carbon['net_c']
    net_positive = net_c > 0
    total_co2e = carbon.get('stock_total_co2e_mg') or 0
    total_c = carbon.get('stock_total_c') or 0
    bg    = RED_LIGHT if net_positive else GREEN_LIGHT
    color = RED if net_positive else colors.HexColor('#1b5e20')
    icon  = _icon_warn(color=RED) if net_positive else _icon_ok(color=colors.HexColor('#1b5e20'))

    header = _icon_text_row(icon, f'Total Carbon: {total_co2e:,.2f} Mg CO2e', ParagraphStyle(
        'nb', fontName='Helvetica-Bold', fontSize=12, textColor=color,
    ))
    sub = Paragraph(
        f"{total_c:,.2f} Mg C stored (biomass + soil). Net flux over the last 12 months: "
        f"<b>{net_c:+.4f} Mg C</b> ({carbon['net']:+.4f} Mg CO<sub>2</sub>e), "
        f"<b>{_sink_label(net_c)}</b> (negative = sink, positive = source).",
        ParagraphStyle('nbs', fontName='Helvetica', fontSize=8.5, textColor=BLACK, leading=11))
    t = Table([[header], [sub]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), bg),
        ('BOX',          (0, 0), (-1, -1), 1, GRAY_BORDER),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ('LEFTPADDING',  (0, 0), (-1, -1), 14),
    ]))
    return t


def _carbon_indices_table(carbon: dict) -> Table:
    """Indices Sentinel-2 (dernière lecture) + formule de chaque indice."""
    labels = {'ndvi': 'NDVI', 'evi': 'EVI', 'savi': 'SAVI', 'ndre': 'NDRE'}
    rows = [[Paragraph('<b>Index</b>',   _styles()['body_bold']),
             Paragraph('<b>Formula</b>', _styles()['body_bold']),
             Paragraph(f"<b>Value ({carbon.get('end_date') or 'N/A'})</b>", _styles()['body_bold'])]]
    for key, label in labels.items():
        val = (carbon.get('indices') or {}).get(key)
        rows.append([
            Paragraph(label, _styles()['body']),
            Paragraph((carbon.get('index_formulas') or {}).get(key, ''), _styles()['body']),
            Paragraph('N/A' if val is None else f'{float(val):.4f}', _styles()['body']),
        ])
    t = Table(rows, colWidths=[25 * mm, CONTENT_W - 60 * mm, 35 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0),  GREEN),
        ('TEXTCOLOR',    (0, 0), (-1, 0),  WHITE),
        ('GRID',         (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',   (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
        ('LEFTPADDING',  (0, 0), (-1, -1), 6),
    ]))
    return t


def _conversion_note(st: dict) -> Paragraph:
    return Paragraph('Unit conversion: Mg CO<sub>2</sub>e = Mg C × 3.67 (44/12); '
                     'Mg C = Mg CO<sub>2</sub>e ÷ 3.67. 1 Mg = 1 tonne.', st['small'])


def _carbon_summary_elems(carbon: dict, st: dict) -> list:
    """Tableau émissions / absorptions / net / stock, en Mg C et Mg CO2e."""
    elems = []
    elems += _section_bar('Carbon Assessment Summary', st)
    elems.append(_carbon_table(carbon))
    elems.append(Spacer(1, 2 * mm))
    elems.append(_conversion_note(st))
    elems.append(Spacer(1, 5 * mm))
    return elems


def _flux_bar_chart(months, values, title, color, signed=False):
    """Barres mensuelles en Mg C ; signed : rouge > 0 (source), vert < 0 (puits)."""
    x = [datetime.strptime(m, '%Y-%m') for m in months]
    fig, ax = plt.subplots(figsize=(3.7, 2.3), facecolor='white')
    bar_colors = [('#e53935' if v > 0 else '#43a047') for v in values] if signed else color
    ax.bar(x, values, width=20, color=bar_colors, alpha=0.85)
    if signed:
        ax.axhline(0, color='#555555', linewidth=0.8)
    ax.set_title(title, fontsize=8, fontweight='bold')
    ax.set_ylabel('Mg C', fontsize=7)
    ax.tick_params(labelsize=6)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    ax.grid(alpha=0.3, axis='y')
    fig.tight_layout()
    return _line_chart_image(fig, width=CONTENT_W / 2 - 2 * mm, ratio=2.3 / 3.7)


def _cumulative_chart(months, net_values):
    """Bilan net cumulé sur l'année (Mg C) : sous zéro = carbone absorbé."""
    x = [datetime.strptime(m, '%Y-%m') for m in months]
    cum, total = [], 0.0
    for v in net_values:
        total += v
        cum.append(total)
    fig, ax = plt.subplots(figsize=(3.7, 2.3), facecolor='white')
    ax.plot(x, cum, color='#2d7a2d', marker='o', markersize=3, linewidth=1.5)
    ax.fill_between(x, cum, 0, where=[c < 0 for c in cum], color='#43a047', alpha=0.2, interpolate=True)
    ax.fill_between(x, cum, 0, where=[c > 0 for c in cum], color='#e53935', alpha=0.2, interpolate=True)
    ax.axhline(0, color='#555555', linewidth=0.8)
    ax.set_title('Cumulative Net Balance (− = absorbed)', fontsize=8, fontweight='bold')
    ax.set_ylabel('Mg C', fontsize=7)
    ax.tick_params(labelsize=6)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return _line_chart_image(fig, width=CONTENT_W / 2 - 2 * mm, ratio=2.3 / 3.7)


def _annual_flux_tiles(carbon: dict) -> Table:
    """Chiffres annuels : émissions, absorption, net (Mg C, Mg CO2e en dessous)."""
    def tile(label, c, co2e, color, extra='', sign=''):
        return Paragraph(
            f'<font size="8" color="#666666">{label}</font><br/>'
            f'<font size="14" color="{color}"><b>{c:{sign}.4f} Mg C</b></font><br/>'
            f'<font size="8">{co2e:{sign}.4f} Mg CO<sub>2</sub>e{extra}</font>',
            ParagraphStyle('tile', fontName='Helvetica', fontSize=9, leading=16, alignment=TA_CENTER))
    net_c = carbon['net_c']
    net_color = '#e53935' if net_c > 0 else '#2e7d32'
    t = Table([[
        tile('Emissions (12 months)', carbon['emissions_c'], carbon['emissions'], '#e53935'),
        tile('Absorption (12 months)', carbon['removals_c'], carbon['removals'], '#2e7d32'),
        tile('Net Emissions (12 months)', net_c, carbon['net'], net_color,
             f'<br/><b>{_sink_label(net_c)}</b>', sign='+'),
    ]], colWidths=[CONTENT_W / 3] * 3)
    t.setStyle(TableStyle([
        ('BOX',          (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ('INNERGRID',    (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ('BACKGROUND',   (0, 0), (-1, -1), GRAY_BG),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',   (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 6),
    ]))
    return t


def _carbon_flux_elems(carbon: dict, st: dict) -> list:
    """Bilan des 12 derniers mois : chiffres annuels, un graphique par
    paramètre (émissions, absorption, net) + bilan cumulé, tableau mensuel."""
    monthly = carbon.get('monthly_flux') or []
    elems = [KeepTogether(_section_bar('Carbon Balance: Last 12 Months', st)
                          + [_annual_flux_tiles(carbon)])]
    elems.append(Spacer(1, 3 * mm))
    if not monthly:
        elems.append(Paragraph('Monthly detail unavailable: less than 13 months of satellite '
                               'readings for this parcel.', st['small']))
        elems.append(Spacer(1, 5 * mm))
        return elems

    months = [m['month'] for m in monthly]
    charts = [
        _flux_bar_chart(months, [m['emissions_c'] for m in monthly], 'Carbon Emissions', '#e53935'),
        _flux_bar_chart(months, [m['removals_c'] for m in monthly], 'Carbon Absorption', '#43a047'),
        _flux_bar_chart(months, [m['net_c'] for m in monthly],
                        'Carbon Net Emissions (+ source / − sink)', None, signed=True),
        _cumulative_chart(months, [m['net_c'] for m in monthly]),
    ]
    grid = Table([charts[:2], charts[2:]], colWidths=[CONTENT_W / 2] * 2)
    grid.setStyle(TableStyle([('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0)]))
    elems.append(grid)
    elems.append(Spacer(1, 3 * mm))

    # 12 mois couverts : les totaux annuels SONT la somme des mois. Sinon la
    # ligne de total additionne les mois affichés et le dit.
    complete = len(monthly) == 12
    total = {k: sum(m[k] for m in monthly) for k in ('emissions_c', 'removals_c', 'net_c', 'net_co2e')}
    total_label = '<b>Year</b>' if complete else f'<b>Total ({len(monthly)} months)</b>'
    w = CONTENT_W / 6
    elems.append(_simple_table(
        ['Month', 'Emissions (Mg C)', 'Absorption (Mg C)', 'Net (Mg C)', 'Net (Mg CO2e)', 'Status'],
        [[m['month'] + ('*' if m.get('interpolated') else ''), _fmt(m['emissions_c'], 4),
          _fmt(m['removals_c'], 4), _fmt(m['net_c'], 4, signed=True),
          _fmt(m['net_co2e'], 4, signed=True), _sink_label(m['net_c'])]
         for m in monthly]
        + [[total_label, f"<b>{total['emissions_c']:.4f}</b>", f"<b>{total['removals_c']:.4f}</b>",
            f"<b>{total['net_c']:+.4f}</b>", f"<b>{total['net_co2e']:+.4f}</b>",
            f"<b>{_sink_label(total['net_c'])}</b>"]],
        [w * 0.8, w * 1.05, w * 1.05, w, w * 1.05, w * 1.05]))
    elems.append(Spacer(1, 2 * mm))
    notes = ("Each month counts 1/12 of its change over one year (that month's stock minus the same month "
             'a year earlier), which removes the seasonal swing; the 12 months add up to the yearly figure.')
    if any(m.get('interpolated') for m in monthly):
        notes += (' * Cloudy month without a usable reading (this month or the same month a year '
                  'earlier): stock interpolated between the neighbouring months.')
    if not complete:
        notes += (f' Only {len(monthly)} of the last 12 months could be computed (longer cloudy gaps): '
                  'the yearly figures above compare the mean stock of the last 12 months with the '
                  'previous 12 instead.')
    elems.append(Paragraph(notes, st['small']))
    elems.append(_conversion_note(st))
    elems.append(Spacer(1, 5 * mm))
    return elems


def _carbon_assessment_elems(carbon: dict, st: dict) -> list:
    """Résumé carbone, bilan 12 mois, indices, historique et méthode."""
    net = carbon['net']
    net_positive = net >= 0
    elems = []

    elems += _carbon_summary_elems(carbon, st)
    elems += _carbon_flux_elems(carbon, st)

    elems.append(KeepTogether(_section_bar('Vegetation Indices (Sentinel-2)', st)
                              + [_carbon_indices_table(carbon)]))
    elems.append(Spacer(1, 5 * mm))

    elems += _carbon_history_elems(carbon, st)

    elems += _section_bar('Methodology & Interpretation', st)
    period = f"{carbon.get('start_date') or 'N/A'} → {carbon.get('end_date') or 'N/A'}"
    interp = [
        ('<b>Biomass (AGB)</b>',  f"{carbon['agb_formula']}, computed for each monthly Sentinel-2 reading."),
        ('<b>Biomass Stock</b>',  'AGB × area, + BGB (20 % of AGB) × 72.5 % dry matter × 50 % carbon × 3.67 (CO<sub>2</sub>/C). '
                                  f"Start: {carbon['stock_start_co2e_mg']:.4f}, end: {carbon['stock_end_co2e_mg']:.4f} Mg CO<sub>2</sub>e."),
        ('<b>Soil Organic Carbon</b>', _soc_method_text(carbon)),
        ('<b>Total Carbon Stock</b>', 'AGB carbon + BGB carbon + SOC (IPCC pools, dead wood and litter excluded); '
                                      'CO<sub>2</sub>e = C × 44/12.'),
        ('<b>Stock Change (ΔStock)</b>',
         f"{carbon.get('stock_change_co2e_mg', 0):.4f} Mg CO<sub>2</sub>e: "
         f"{carbon.get('stock_change_method') or period}. Comparing yearly means removes the seasonal "
         'swing (leaf flush, dry season) and the noise of a single cloudy reading.'),
    ]
    growth = carbon.get('forest_growth')
    if growth:
        interp += [
            ('<b>Gross Removals</b>',
             'IPCC gain-loss method: a standing forest keeps absorbing CO<sub>2</sub> even when its stock '
             f"falls. Default growth {growth['source']}; × area × (1 + 20 % BGB) × 50 % carbon × 3.67 = "
             f"{growth['gross_growth_co2e_mg']:.4f} Mg CO<sub>2</sub>e/yr (or ΔStock when the observed "
             'gain is larger).'),
            ('<b>Gross Emissions</b>',
             'Removals − ΔStock: the biomass lost to harvest, degradation or disturbance over the year '
             '(0 when the stock grew at least as fast as the default growth).'),
        ]
    else:
        interp += [
            ('<b>Gross Emissions</b>', f'Loss of biomass carbon stock over the year, {period} (max(−ΔStock, 0)).'),
            ('<b>Gross Removals</b>',  f'Gain of biomass carbon stock over the year, {period} (max(ΔStock, 0)).'),
        ]
    sar = carbon.get('sar_filled_months') or []
    if sar:
        interp.append(('<b>Cloudy Months</b>',
                       f'{len(sar)} cloudy month(s) filled with Sentinel-1 radar (sees through clouds), '
                       'using a per-parcel regression of each index on Sentinel-1 VH backscatter and RVI.'))
    interp += [
        ('<b>Net Flux</b>',        f'Emissions − Removals: {"positive (net source)" if net_positive else "negative (net sink)"}. '
                                   f"Current value: {carbon['net_c']:.4f} Mg C = {net:.4f} Mg CO<sub>2</sub>e."),
        ('<b>Units</b>',           'Charts are in Mg C (tonnes of carbon). Mg CO<sub>2</sub>e = Mg C × 3.67 (44/12).'),
    ]
    for w in carbon.get('warnings') or []:
        interp.append(('<b>Note</b>', w))
    interp_t = Table([
        [Paragraph(t, ParagraphStyle('ik', fontName='Helvetica-Bold', fontSize=8, textColor=GREEN)),
         Paragraph(d, ParagraphStyle('id', fontName='Helvetica', fontSize=8, textColor=BLACK, leading=11))]
        for t, d in interp
    ], colWidths=[42 * mm, CONTENT_W - 42 * mm])
    interp_t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), GRAY_BG),
        ('GRID',         (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING',   (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
        ('LEFTPADDING',  (0, 0), (-1, -1), 6),
    ]))
    elems.append(interp_t)
    elems.append(Spacer(1, 5 * mm))
    return elems


def _soc_method_text(carbon: dict) -> str:
    soc = carbon.get('soc')
    if not soc:
        return 'Not available for this report (ISRIC SoilGrids did not answer).'
    return (f"ISRIC SoilGrids v2.0 organic carbon stock, {soc.get('depth', '0-30cm')} "
            f"(IPCC default depth for mineral soils): {soc['ocs_t_c_ha']:.2f} t C/ha at "
            f"{soc.get('lat')}, {soc.get('lon')} × area. Static map: counted in the total stock, "
            'not in emissions/removals.')


def _line_chart_image(fig, width=CONTENT_W, ratio=0.42) -> Image:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width, height=width * ratio)


def _simple_table(header: list, rows: list, col_widths: list) -> Table:
    data = [[Paragraph(f'<b>{h}</b>', _styles()['body_bold']) for h in header]]
    data += [[Paragraph(str(c), _styles()['body']) for c in r] for r in rows]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0),  GREEN),
        ('TEXTCOLOR',    (0, 0), (-1, 0),  WHITE),
        ('GRID',         (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
        ('LEFTPADDING',  (0, 0), (-1, -1), 6),
    ]))
    return t


def _fmt(v, digits=2, signed=False):
    if v is None:
        return 'N/A'
    return f'{v:+.{digits}f}' if signed else f'{v:.{digits}f}'


def _carbon_history_elems(carbon: dict, st: dict) -> list:
    """Stock carbone sur 5 ans : courbe mensuelle + moyennes annuelles."""
    history = [h for h in carbon.get('history') or [] if h.get('date')]
    yearly = carbon.get('history_yearly') or []
    if len(history) < 2:
        return []
    soc_c = carbon.get('stock_soc_c') or 0

    dates = [datetime.strptime(h['date'][:10], '%Y-%m-%d') for h in history]
    biomass = [h['stock_co2e_mg'] / CO2_PER_C for h in history]
    fig, ax = plt.subplots(figsize=(7.5, 3.1), facecolor='white')
    ax.plot(dates, biomass, color='#2d7a2d', linewidth=1.4, marker='o', markersize=2.5,
            label='Biomass stock (AGB + BGB)')
    if soc_c:
        ax.plot(dates, [b + soc_c for b in biomass], color='#8d6e63', linewidth=1.4,
                label='Total stock (biomass + SOC)')
    for y in yearly:
        ax.hlines(y['biomass_stock_co2e_mg'] / CO2_PER_C, datetime(y['year'], 1, 1), datetime(y['year'], 12, 31),
                  colors='#fb8c00', linestyles='dashed', linewidth=1)
    ax.plot([], [], color='#fb8c00', linestyle='dashed', label='Yearly mean (biomass)')
    ax.set_ylabel('Mg C', fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, frameon=False, loc='upper left')
    fig.tight_layout()

    elems = [KeepTogether(_section_bar('Carbon Stock: 5-Year History', st) + [_line_chart_image(fig)])]
    trend = carbon.get('trend_co2e_mg_per_year')
    if trend is not None:
        direction = 'increasing (sink)' if trend > 0 else 'decreasing (source)' if trend < 0 else 'stable'
        elems.append(Paragraph(
            f"Trend {carbon.get('history_from')} → {carbon.get('history_to')}: "
            f"<b>{trend / CO2_PER_C:+.4f} Mg C / year</b> ({trend:+.4f} Mg CO<sub>2</sub>e / year), "
            f"{direction}.", st['body']))
    elems.append(Spacer(1, 3 * mm))
    if yearly:
        def c(v, signed=False):
            return _fmt(None if v is None else v / CO2_PER_C, 4, signed)
        w = CONTENT_W / 6
        elems.append(_simple_table(
            ['Year', 'Readings', 'Biomass stock (Mg C)', 'Change vs previous year (Mg C)',
             'Total incl. SOC (Mg C)', 'Total incl. SOC (Mg CO2e)'],
            [[y['year'], y['readings'], c(y['biomass_stock_co2e_mg']),
              c(y.get('change_co2e_mg'), signed=True), c(y['total_stock_co2e_mg']),
              _fmt(y['total_stock_co2e_mg'], 4)]
             for y in yearly],
            [w * 0.6, w * 0.7, w * 1.1, w * 1.3, w * 1.1, w * 1.2]))
        elems.append(Spacer(1, 2 * mm))
        elems.append(_conversion_note(st))
    elems.append(Spacer(1, 5 * mm))
    return elems


def _forest_area_elems(area: dict, st: dict) -> list:
    """Surface boisée mois par mois : courbe + barres de variation + tableau."""
    if not area:
        return []
    months = [m for m in area.get('months') or [] if m.get('forest_area_ha') is not None]
    if not months:
        return []

    x = [datetime.strptime(m['month'], '%Y-%m') for m in months]
    fig, ax = plt.subplots(figsize=(7.5, 3.1), facecolor='white')
    changes = [m['change_ha'] or 0 for m in months]
    ax.bar(x, changes, width=20, color=['#c62828' if c < 0 else '#43a047' for c in changes],
           alpha=0.55, label='Monthly change (ha)')
    ax.set_ylabel('Change (ha)', fontsize=8)
    ax2 = ax.twinx()
    ax2.plot(x, [m['forest_area_ha'] for m in months], color='#2d7a2d', marker='o',
             markersize=3, linewidth=1.5, label='Forest area (ha)')
    ax2.set_ylabel('Forest area (ha)', fontsize=8)
    for a in (ax, ax2):
        a.tick_params(labelsize=7)
    ax.grid(alpha=0.3)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7, frameon=False, loc='lower left')
    fig.tight_layout()

    elems = [KeepTogether(_section_bar('Monthly Forest Area Change (Degradation & Deforestation)', st)
                          + [_line_chart_image(fig)])]
    net = area.get('net_change_ha')
    elems.append(Paragraph(
        f"{area['period_from']} → {area['period_to']}: forest area "
        f"<b>{area['current_forest_area_ha']:.2f} ha</b> of {area['area_ha']:.2f} ha, "
        f"net change <b>{_fmt(net, 2, signed=True)} ha</b> ({_fmt(area.get('net_change_pct'), 2, signed=True)} %). "
        f"{area['method']} Cloudy months (less than half of the forest visible) are skipped.",
        st['body']))
    elems.append(Spacer(1, 3 * mm))
    w = CONTENT_W / 4
    elems.append(_simple_table(
        ['Month', 'Forest area (ha)', 'Change (ha)', 'Change (%)'],
        [[m['month'],
          'cloudy' if m.get('forest_area_ha') is None else _fmt(m['forest_area_ha']),
          _fmt(m.get('change_ha'), 2, signed=True), _fmt(m.get('change_pct'), 2, signed=True)]
         for m in area.get('months') or []],
        [w] * 4))
    elems.append(Spacer(1, 5 * mm))
    return elems


def build_carbon_farm_pdf(
    farm_id    : str,
    farm_info  : dict,
    carbon     : dict,
    coords     : list | None = None,
    logo_parrot: str | None = None,
    logo_agri  : str | None = None,
) -> bytes:
    """Génère le rapport Carbon pour une ferme (indices Sentinel-2)."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=22 * mm,
        title=f'Farmland Carbon Assessment {farm_id}',
        author='Agriyields',
    )
    st    = _styles()
    today = datetime.now().strftime('%d %B %Y')
    elems = []
    area_ha = carbon.get('area_ha') or 0

    # ── En-tête ──────────────────────────────────────────────────────────────
    elems.append(_header_table(
        logo_parrot, logo_agri,
        'FARMLAND CARBON ASSESSMENT',
        f'Generated on {today}  •  Regulation (EU) 2023/1115',
    ))
    elems.append(Spacer(1, 5 * mm))

    # ── Net status badge ──────────────────────────────────────────────────────
    elems.append(_carbon_status_badge(carbon))
    elems.append(Spacer(1, 5 * mm))

    # ── Farm info ─────────────────────────────────────────────────────────────
    elems += _section_bar('Farm Information', st)
    rows = [
        ('Farm ID',      farm_info.get('farm_id', farm_id)),
        ('Owner',        farm_info.get('name')),
        ('Geolocation',  farm_info.get('geolocation')),
    ]
    if carbon.get('crop'):
        rows.append(('Crop', carbon['crop']))
    if farm_info.get('crops'):
        rows.append(('Land Type', farm_info['crops'][-1].get('land_type', 'N/A')))
    if area_ha:
        rows.append(('Project Area', f"{area_ha * 10_000:.2f} m²  ({area_ha:.2f} ha)"))
    elems.append(_info_table(rows))
    elems.append(Spacer(1, 5 * mm))

    elems += _carbon_assessment_elems(carbon, st)

    # ── Satellite map ─────────────────────────────────────────────────────────
    if coords:
        map_img = _mapbox_image(coords)
        if map_img:
            elems += _section_bar('Plot Map: Satellite View', st)
            elems.append(map_img)

    doc.build(elems, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas, canvasmaker=_NumberedCanvas)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# BUILD CARBON FOREST PDF
# ══════════════════════════════════════════════════════════════════════════════

def build_carbon_forest_pdf(
    forest_id  : int | str,
    forest_info: dict,
    carbon     : dict,
    area_change: dict | None = None,
    coords     : list | None = None,
    logo_parrot: str | None = None,
    logo_agri  : str | None = None,
) -> bytes:
    """Génère le rapport Carbon pour une forêt — même structure que farm."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=22 * mm,
        title=f'Forest Carbon Assessment {forest_id}',
        author='Agriyields',
    )
    st    = _styles()
    today = datetime.now().strftime('%d %B %Y')
    elems = []
    area_ha = carbon.get('area_ha') or 0

    elems.append(_header_table(
        logo_parrot, logo_agri,
        'FOREST CARBON ASSESSMENT',
        f'Generated on {today}  •  Regulation (EU) 2023/1115',
    ))
    elems.append(Spacer(1, 5 * mm))

    elems.append(_carbon_status_badge(carbon))
    elems.append(Spacer(1, 5 * mm))

    elems += _section_bar('Forest Information', st)
    rows = [
        ('Forest Name',  forest_info.get('name')),
        ('Tree Type',    forest_info.get('tree_type', 'N/A')),
        ('Date Created', forest_info.get('date_created', 'N/A')),
        ('Last Updated', forest_info.get('date_updated', 'N/A')),
    ]
    if area_ha:
        rows.append(('Project Area', f"{area_ha * 10_000:.2f} m²  ({area_ha:.2f} ha)"))
    elems.append(_info_table(rows))
    elems.append(Spacer(1, 5 * mm))

    elems += _carbon_assessment_elems(carbon, st)
    elems += _forest_area_elems(area_change, st)

    if coords:
        map_img = _mapbox_image(coords)
        if map_img:
            elems += _section_bar('Plot Map: Satellite View', st)
            elems.append(map_img)

    doc.build(elems, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas, canvasmaker=_NumberedCanvas)
    return buf.getvalue()

def _tree_co2_table(trees_data: list) -> Table:
    """Table détail par arbre : mesures, AGB/CO2 mesuré, taux sigmoid."""
    header = [
        Paragraph('<b>Tree</b>',       _styles()['body_bold']),
        Paragraph('<b>Species</b>',    _styles()['body_bold']),
        Paragraph('<b>Age (yr)</b>',   _styles()['body_bold']),
        Paragraph('<b>CO2 Total (kg)</b>',      _styles()['body_bold']),
        Paragraph('<b>CO2/yr avg (kg)</b>',     _styles()['body_bold']),
        Paragraph('<b>CO2/yr sigmoid (kg)</b>', _styles()['body_bold']),
    ]
    rows = [header]
    for t in trees_data:
        rows.append([
            Paragraph(t['name'] or f"#{t['tree_id']}", _styles()['body']),
            Paragraph(t['species'] or 'N/A',            _styles()['body']),
            Paragraph(f"{t['age_years']:.1f}",           _styles()['body']),
            Paragraph(f"{t['co2_sequestered_kg']:.2f}",  _styles()['body']),
            Paragraph(f"{t['co2_annual_avg_kg']:.2f}",   _styles()['body']),
            Paragraph(f"{t['co2_annual_rate_sigmoid_kg']:.2f}", _styles()['body']),
        ])
 
    t_widths = [CONTENT_W * w for w in (0.20, 0.20, 0.12, 0.18, 0.15, 0.15)]
    table = Table(rows, colWidths=t_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0),   GREEN),
        ('TEXTCOLOR',    (0, 0), (-1, 0),   WHITE),
        ('GRID',         (0, 0), (-1, -1),  0.5, GRAY_BORDER),
        ('VALIGN',       (0, 0), (-1, -1),  'MIDDLE'),
        ('TOPPADDING',   (0, 0), (-1, -1),  5),
        ('BOTTOMPADDING',(0, 0), (-1, -1),  5),
        ('LEFTPADDING',  (0, 0), (-1, -1),  6),
        *[('BACKGROUND', (0, i), (-1, i), GRAY_BG) for i in range(2, len(rows), 2)],
    ]))
    return table
 
 
def build_tree_co2_pdf(
    forest_id  : int | str,
    forest_info: dict,
    co2_report : dict,   # sortie de compute_forest_co2_summary()
    logo_parrot: str | None = None,
    logo_agri  : str | None = None,
) -> bytes:
    """Génère le rapport de séquestration CO2 par arbre pour une forêt."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=22 * mm,
        title=f'Tree CO2 Sequestration Report Forest {forest_id}',
        author='Agriyields',
    )
    st    = _styles()
    today = datetime.now().strftime('%d %B %Y')
    elems = []
 
    trees_data = co2_report.get('trees', [])
    totals     = co2_report.get('totals', {})
 
    # ── En-tête ──────────────────────────────────────────────────────────────
    elems.append(_header_table(
        logo_parrot, logo_agri,
        'TREE CO2 SEQUESTRATION REPORT',
        f'Generated on {today}  •  AGB formula + sigmoid growth model',
    ))
    elems.append(Spacer(1, 5 * mm))
 
    # ── Forest info ──────────────────────────────────────────────────────────
    elems += _section_bar('Forest Information', st)
    rows = [
        ('Forest Name',  forest_info.get('name')),
        ('Tree Type',    forest_info.get('tree_type', 'N/A')),
        ('Tree Count',   totals.get('tree_count', 0)),
    ]
    elems.append(_info_table(rows))
    elems.append(Spacer(1, 5 * mm))
 
    # ── Totaux ───────────────────────────────────────────────────────────────
    elems += _section_bar('CO2 Sequestration Summary', st)
    def mg_c(kg_co2, per_year=False):
        unit = ' / yr' if per_year else ''
        return (f"{kg_co2 / 1000 / CO2_PER_C:.4f} Mg C{unit}  "
                f"({kg_co2 / 1000:.4f} Mg CO2e{unit} = {kg_co2:.2f} kg CO2)")
    totals_rows = [
        ('Total Carbon Stored (lifetime)',       mg_c(totals.get('total_co2_sequestered_kg', 0))),
        ('Carbon Absorbed / year (measured avg)', mg_c(totals.get('total_co2_annual_avg_kg', 0), True)),
        ('Carbon Absorbed / year (sigmoid model)', mg_c(totals.get('total_co2_annual_sigmoid_kg', 0), True)),
    ]
    elems.append(_info_table(totals_rows))
    elems.append(Spacer(1, 2 * mm))
    elems.append(_conversion_note(st))
    elems.append(Spacer(1, 5 * mm))
 
    # ── Détail par arbre ─────────────────────────────────────────────────────
    if trees_data:
        elems += _section_bar('Per-Tree Detail', st)
        elems.append(_tree_co2_table(trees_data))
        elems.append(Spacer(1, 5 * mm))
 
    # ── Note méthodologique ──────────────────────────────────────────────────
    elems += _section_bar('Methodology', st)
    note = (
        'AGB = 0.25 × D² × H (D: diameter, H: height). Total biomass = 1.2 × AGB '
        '(20% belowground). Dry weight = 72.5% of biomass, carbon = 50% of dry '
        'weight, CO2 = carbon × 3.67. The "avg" annual rate divides lifetime CO2 '
        'by tree age; the "sigmoid" rate uses the species logistic growth curve '
        '(Km, t½, Mmax) to estimate biomass increment for the current year.'
    )
    elems.append(Paragraph(note, ParagraphStyle(
        'note', fontName='Helvetica', fontSize=8, textColor=MUTED, leading=11,
    )))

    doc.build(elems, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas, canvasmaker=_NumberedCanvas)
    return buf.getvalue()


def build_forest_biomass_index_pdf(
    forest_id  : int | str,
    forest_name: str,
    area_ha    : float,
    biomass    : dict,   # sortie de compute_forest_biomass_from_index()
    tree_type  : str | None = None,
    logo_parrot: str | None = None,
    logo_agri  : str | None = None,
) -> bytes:
    """AGB/BGB/CO2 de forêt estimés depuis le NDVI Sentinel-2 (sans inventaire
    arbre par arbre) — remplace la vue GFW pré-calculée pour /reportcarbonforest."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=22 * mm,
        title=f'Forest Biomass (Satellite Index) Report Forest {forest_id}',
        author='Agriyields',
    )
    st    = _styles()
    today = datetime.now().strftime('%d %B %Y')
    elems = []

    elems.append(_header_table(
        logo_parrot, logo_agri,
        'FOREST CARBON ASSESSMENT: SATELLITE INDEX MODEL',
        f'Generated on {today}  •  AGB/BGB estimated from Sentinel-2 NDVI',
    ))
    elems.append(Spacer(1, 5 * mm))

    elems += _section_bar('Forest Information', st)
    elems.append(_info_table([
        ('Forest Name', forest_name),
        ('Tree Type', tree_type or 'N/A'),
        ('Project Area', f"{area_ha:.2f} ha"),
        ('NDVI Used', biomass.get('ndvi_used')),
        ('NDVI Date', biomass.get('ndvi_date')),
    ]))
    elems.append(Spacer(1, 5 * mm))

    elems += _section_bar('Biomass & Carbon Summary', st)
    elems.append(_info_table([
        ('Above-Ground Biomass (AGB)', f"{biomass.get('agb_kg', 0) / 1000:.2f} Mg  ({biomass.get('agb_per_ha_mg', 0):.2f} Mg/ha)"),
        ('Below-Ground Biomass (BGB)', f"{biomass.get('bgb_kg', 0) / 1000:.2f} Mg"),
        ('Total Biomass',              f"{biomass.get('total_biomass_kg', 0) / 1000:.2f} Mg"),
        ('Total Carbon',               f"{biomass.get('total_carbon_kg', 0) / 1000:.2f} Mg C"),
        ('CO2 Equivalent',             f"{biomass.get('co2_sequestered_kg', 0) / 1000:.2f} Mg CO2e"),
    ]))
    elems.append(Spacer(1, 5 * mm))

    elems += _section_bar('Methodology', st)
    note2 = (
        f"{biomass.get('model', '')}. Total biomass = 1.2 x AGB (20% belowground). "
        'Dry weight = 72.5% of biomass, carbon = 50% of dry weight, CO2 = carbon x 3.67 '
        '(same conversion chain as the per-tree measured report). This satellite-index '
        'estimate is a generic approximation for forests without a full tree inventory: '
        'it is NOT calibrated on local field plots and should not replace ground '
        'measurements for regulatory submissions without local validation.'
    )
    elems.append(Paragraph(note2, ParagraphStyle(
        'note2', fontName='Helvetica', fontSize=8, textColor=MUTED, leading=11,
    )))

    doc.build(elems, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas, canvasmaker=_NumberedCanvas)
    return buf.getvalue()

# ══════════════════════════════════════════════════════════════════════════════
# BUILD SATELLITE INDEX PDF (rapport « indices satellite », ferme / invité)
# ══════════════════════════════════════════════════════════════════════════════

SAT_INDICES = [
    # clé, libellé, ce que l'indice mesure, formule Sentinel-2
    ('ndvi', 'NDVI', 'Vegetation health',        '(B08 − B04) / (B08 + B04)'),
    ('evi',  'EVI',  'Enhanced vegetation',      '2.5 × (B08 − B04) / (B08 + 6·B04 − 7.5·B02 + 1)'),
    ('savi', 'SAVI', 'Soil-adjusted vegetation', '1.5 × (B08 − B04) / (B08 + B04 + 0.5)'),
    ('ndmi', 'NDMI', 'Canopy moisture',          '(B08 − B11) / (B08 + B11)'),
    ('ndwi', 'NDWI', 'Water content',            '(B03 − B08) / (B03 + B08)'),
    ('nmdi', 'NMDI', 'Soil drought',             '(B08 − (B11 − B12)) / (B08 + (B11 − B12))'),
    ('nbr',  'NBR',  'Burn ratio',               '(B08 − B12) / (B08 + B12)'),
    ('bsi',  'BSI',  'Bare soil',                '((B11 + B04) − (B08 + B02)) / ((B11 + B04) + (B08 + B02))'),
]
SAT_CHART_INDICES = [('ndvi', '#16a34a'), ('evi', '#0d9488'), ('ndmi', '#0284c7'), ('nmdi', '#f97316')]
# Plage physique habituelle de chaque indice (axe Y des courbes), comme l'écran.
SAT_INDEX_RANGE = {
    'ndvi': (-0.2, 0.9), 'evi': (-0.2, 0.8), 'savi': (-0.2, 0.8), 'ndmi': (-0.5, 0.6),
    'ndwi': (-0.5, 0.5), 'nmdi': (0.0, 1.2), 'nbr': (-0.5, 0.8), 'bsi': (-0.5, 0.5),
}


def _sat_val(row, idx):
    v = (row or {}).get(idx)
    return (v.get('value'), v.get('tier') or {}) if isinstance(v, dict) else (v, {})


def _quarter_label(date_str):
    """'2026-07-18' → '2026-Q3 (from 18 Jul)' : les trimestres partent de la date de début du rapport."""
    try:
        d = datetime.strptime(date_str[:10], '%Y-%m-%d')
    except (TypeError, ValueError):
        return date_str or 'N/A'
    return f"{d.year}-Q{(d.month - 1) // 3 + 1} (from {d.strftime('%d %b')})"


def _sat_status_badge(ndvi, last_date):
    """Bannière d'état de la végétation (dernier NDVI), même gabarit que le bilan carbone."""
    if ndvi is None:
        label, bg, color, icon = 'Vegetation status unavailable', GRAY_BG, MUTED, _icon_warn(color=MUTED)
    elif ndvi >= 0.6:
        label, bg, color, icon = 'Healthy Vegetation', GREEN_LIGHT, colors.HexColor('#1b5e20'), _icon_ok(color=colors.HexColor('#1b5e20'))
    elif ndvi >= 0.3:
        label, bg, color, icon = 'Moderate Vegetation', ORANGE_LIGHT, ORANGE, _icon_warn(color=ORANGE)
    else:
        label, bg, color, icon = 'Sparse or Stressed Vegetation', RED_LIGHT, RED, _icon_bad(color=RED)
    if ndvi is not None:
        label += f'  ·  NDVI {ndvi:.3f}, {_quarter_label(last_date)}'
    row = _icon_text_row(icon, label, ParagraphStyle('sb', fontName='Helvetica-Bold', fontSize=12, textColor=color))
    t = Table([[row]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), bg),
        ('BOX',          (0, 0), (-1, -1), 1, GRAY_BORDER),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ('LEFTPADDING',  (0, 0), (-1, -1), 14),
    ]))
    return t


def _sat_latest_table(last, forecast):
    """Dernière lecture de chaque indice, son état et la prévision du trimestre suivant."""
    st = _styles()
    small = ParagraphStyle('sl', parent=st['body'], fontSize=8, leading=10)
    head = ['Index', 'Measures', 'Latest value', 'Status', 'Next quarter (80 % CI)']
    data = [[Paragraph(f'<b>{h}</b>', ParagraphStyle('slh', parent=small, textColor=WHITE)) for h in head]]
    style = [
        ('BACKGROUND',   (0, 0), (-1, 0), GREEN),
        ('GRID',         (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
        ('LEFTPADDING',  (0, 0), (-1, -1), 6),
    ]
    for i, (idx, label, measures, _) in enumerate(SAT_INDICES, start=1):
        val, tier = _sat_val(last, idx)
        fc = ((forecast or {}).get(idx) or [None])[0]
        fc_txt = (f"{fc['value']:.4f}  ({fc.get('lower_80', fc['value']):.3f} – {fc.get('upper_80', fc['value']):.3f})"
                  if fc else 'N/A')
        tier_color = colors.HexColor(tier.get('color', '#666666'))
        data.append([
            Paragraph(f'<b>{label}</b>', small),
            Paragraph(measures, small),
            Paragraph(f'{val:.4f}' if val is not None else 'N/A', small),
            Paragraph(f'<b>{tier.get("label", "N/A")}</b>', ParagraphStyle(f'tc{i}', parent=small, textColor=tier_color)),
            Paragraph(fc_txt, small),
        ])
        if tier.get('bg'):
            style.append(('BACKGROUND', (3, i), (3, i), colors.HexColor(tier['bg'])))
    t = Table(data, colWidths=[16 * mm, 36 * mm, 24 * mm, 44 * mm, CONTENT_W - 120 * mm])
    t.setStyle(TableStyle(style))
    return t


def _sat_index_chart(history, forecast, idx, color, label):
    """Courbe historique trimestrielle + prévision (pointillés) + IC 80 %, fond blanc."""
    pts = [(datetime.strptime(r['date'][:10], '%Y-%m-%d'), _sat_val(r, idx)[0]) for r in history if r.get('date')]
    pts = [(d, v) for d, v in pts if v is not None]
    if len(pts) < 2:
        return None
    fc = [f for f in (forecast or {}).get(idx) or [] if f.get('date')]
    fig, ax = plt.subplots(figsize=(3.7, 2.1), facecolor='white')
    ax.plot([d for d, _ in pts], [v for _, v in pts], color=color, linewidth=1.4, marker='o', markersize=2, label='Observed')
    lo, hi = SAT_INDEX_RANGE.get(idx, (-1, 1))
    values = [v for _, v in pts]
    if fc:
        fd = [datetime.strptime(f['date'][:10], '%Y-%m-%d') for f in fc]
        fv = [f['value'] for f in fc]
        ax.plot([pts[-1][0], fd[0]], [pts[-1][1], fv[0]], color=color, linewidth=1, linestyle='--', alpha=0.6)
        ax.plot(fd, fv, color=color, linewidth=1.2, linestyle='--', label='Forecast')
        ax.fill_between(fd, [f.get('lower_80', f['value']) for f in fc],
                        [f.get('upper_80', f['value']) for f in fc], color=color, alpha=0.18, label='80 % CI')
        values += [f.get('lower_80', f['value']) for f in fc] + [f.get('upper_80', f['value']) for f in fc]
    pad = 0.05
    ax.set_ylim(min(lo, min(values) - pad), max(hi, max(values) + pad))
    ax.set_title(label, fontsize=8.5, fontweight='bold', loc='left')
    ax.tick_params(labelsize=6.5)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=6, frameon=False, loc='lower left', ncol=3)
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout(pad=0.4)
    return _line_chart_image(fig, width=CONTENT_W / 2 - 2 * mm, ratio=2.1 / 3.7)


def _sat_agb_elems(agb, st):
    """Biomasse aérienne (AGB) : historique, tendance et prévision."""
    hist = [h for h in (agb or {}).get('history') or [] if h.get('date') and h.get('agb_t_ha') is not None]
    if len(hist) < 2:
        return []
    fc = [f for f in agb.get('forecast') or [] if f.get('date')]
    sm = agb.get('summary') or {}
    hd = [datetime.strptime(h['date'][:10], '%Y-%m-%d') for h in hist]
    fig, ax = plt.subplots(figsize=(7.5, 2.6), facecolor='white')
    ax.plot(hd, [h['agb_t_ha'] for h in hist], color='#2d7a2d', linewidth=1.4, marker='o', markersize=2.5, label='AGB (observed)')
    slope = sm.get('slope_t_ha_per_year')
    if slope is not None:
        xs = [d.toordinal() / 365.25 for d in hd]
        ys = [h['agb_t_ha'] for h in hist]
        b = sum(ys) / len(ys) - slope * sum(xs) / len(xs)
        ax.plot(hd, [slope * x + b for x in xs], color='#fb8c00', linewidth=1, linestyle=':',
                label=f'Linear trend ({slope:+.3f} t/ha/yr)')
    if fc:
        fd = [datetime.strptime(f['date'][:10], '%Y-%m-%d') for f in fc]
        ax.plot([hd[-1], fd[0]], [hist[-1]['agb_t_ha'], fc[0]['agb_t_ha']], color='#2d7a2d', linewidth=1, linestyle='--', alpha=0.6)
        ax.plot(fd, [f['agb_t_ha'] for f in fc], color='#2d7a2d', linewidth=1.2, linestyle='--', label='AGB (forecast)')
        ax.fill_between(fd, [f.get('lower_80') or f['agb_t_ha'] for f in fc],
                        [f.get('upper_80') or f['agb_t_ha'] for f in fc], color='#2d7a2d', alpha=0.15, label='80 % CI')
    ax.set_ylim(bottom=0)
    ax.set_ylabel('AGB (t/ha)', fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, frameon=False, loc='upper left', ncol=2)
    fig.tight_layout()

    elems = [KeepTogether(_section_bar('Above-Ground Biomass (AGB): 5-Year Trend & Forecast', st) + [_line_chart_image(fig, ratio=0.35)])]
    elems.append(Paragraph(
        f"Model: <b>{agb.get('agb_formula')}</b>, applied to each quarterly reading and to the forecast indices. "
        f"Mean AGB {sm.get('history_from') or ''} → {sm.get('history_to') or ''}: <b>{_fmt(sm.get('mean_agb_t_ha'))} t/ha</b>; "
        f"trend <b>{_fmt(sm.get('slope_t_ha_per_year'), 3, signed=True)} t/ha/yr</b> ({sm.get('direction') or 'N/A'}); "
        f"last <b>{_fmt(sm.get('last_agb_t_ha'))} t/ha</b>; end of forecast <b>{_fmt(sm.get('forecast_end_agb_t_ha'))} t/ha</b> "
        f"({_fmt(sm.get('forecast_change_pct'), 1, signed=True)} %).", st['body']))
    if agb.get('agb_model') == 'generic_ndvi':
        elems.append(Paragraph(
            'Note: generic NDVI biomass model (no field calibration for this crop yet). It is very sensitive to NDVI '
            '(+0.1 NDVI ≈ ×1.9 AGB), so quarter-to-quarter swings reflect canopy greenness more than real biomass change.',
            ParagraphStyle('agbn', parent=st['small'], textColor=ORANGE)))
    if fc:
        w = CONTENT_W / 4
        elems.append(_simple_table(
            ['Quarter', 'AGB (t/ha)', '80 % CI (t/ha)', 'Biomass stock (Mg CO2e)'],
            [[f.get('quarter') or f['date'], _fmt(f['agb_t_ha']),
              f"{_fmt(f.get('lower_80'))} – {_fmt(f.get('upper_80'))}", _fmt(f.get('stock_co2e_mg'))] for f in fc],
            [w] * 4))
    elems.append(Spacer(1, 5 * mm))
    return elems


def _sat_ltv_elems(ltv, st):
    """Analyse financière multi-indices (LTV) — même calcul que l'écran."""
    if not ltv or not ltv.get('indices'):
        return []
    labels = {k: lbl for k, lbl, _, _ in SAT_INDICES}
    rows = []
    for idx, v in ltv['indices'].items():
        rows.append([labels.get(idx, idx.upper()), _fmt(v.get('index_value'), 4), _fmt(v.get('factor'), 3),
                     _fmt(v.get('adjusted_yield_t_ha'), 3), f"{v.get('estimated_crop_value_usd') or 0:,.2f}",
                     f"{v['ltv_ratio_pct']} %" if v.get('ltv_ratio_pct') is not None else 'N/A',
                     f"{v.get('insurance_premium_pct', 0):.2f} %", f"{(v.get('weight') or 0) * 100:.0f} %"])
    c = ltv.get('composite') or {}
    rows.append(['<b>Composite</b>', '—', f"<b>{_fmt(c.get('factor'), 3)}</b>",
                 f"<b>{_fmt(c.get('adjusted_yield_t_ha'), 3)}</b>", f"<b>{c.get('estimated_crop_value_usd') or 0:,.2f}</b>",
                 f"<b>{c['ltv_ratio_pct']} %</b>" if c.get('ltv_ratio_pct') is not None else 'N/A',
                 f"<b>{c.get('insurance_premium_pct', 0):.2f} %</b>", '<b>100 %</b>'])
    w = CONTENT_W
    table = _simple_table(
        ['Index', 'Value', 'Productivity factor', 'Adjusted yield (t/ha)', 'Crop value (USD)', 'LTV', 'Insurance premium', 'Weight'],
        rows, [w * 0.11, w * 0.10, w * 0.13, w * 0.14, w * 0.15, w * 0.10, w * 0.15, w * 0.12])
    table.setStyle(TableStyle([('BACKGROUND', (0, len(rows)), (-1, len(rows)), GREEN_LIGHT)]))
    loan = ltv.get('loan_amount_usd')
    head = _section_bar('Financial Analysis (LTV): Multi-Index Breakdown', st)
    head.append(Paragraph(
        f"Area <b>{ltv.get('area_ha', 'N/A')} ha</b> · target yield <b>{ltv.get('yield_t_per_ha', 'N/A')} t/ha</b> · "
        f"market price <b>USD {ltv.get('price_per_t') or 0:,.0f}/t</b> · loan amount <b>"
        + (f"USD {loan:,.0f}" if loan else 'not provided (LTV not computed)') + '</b>', st['body']))
    elems = [KeepTogether(head + [table])]
    elems += [Spacer(1, 2 * mm), Paragraph(
        'Each index is turned into a productivity factor (0–1, relative to its optimal value); adjusted yield = target yield × factor; '
        'crop value = area × adjusted yield × price; LTV = loan ÷ crop value; insurance premium = 3 % + health risk + LTV risk. '
        'The composite weights the indices (NDVI 28 %, EVI and NDMI 18 %, SAVI 14 %, NDWI 10 %, NMDI 6 %, NBR 4 %, BSI 2 %).',
        st['small']), Spacer(1, 5 * mm)]
    return elems


def _sat_history_table(history):
    st = _styles()
    small = ParagraphStyle('sh', parent=st['body'], fontSize=7, leading=9)
    head = ['Quarter'] + [lbl for _, lbl, _, _ in SAT_INDICES]
    data = [[Paragraph(f'<b>{h}</b>', ParagraphStyle('shh', parent=small, textColor=WHITE)) for h in head]]
    for row in reversed(history):
        cells = [Paragraph(_quarter_label(row.get('date')), small)]
        for idx, _, _, _ in SAT_INDICES:
            val, tier = _sat_val(row, idx)
            cells.append(Paragraph(f'{val:.3f}' if val is not None else '—',
                                   ParagraphStyle('shc', parent=small, textColor=colors.HexColor(tier.get('color', '#1a1a1a')))))
        data.append(cells)
    first = 34 * mm
    t = Table(data, colWidths=[first] + [(CONTENT_W - first) / len(SAT_INDICES)] * len(SAT_INDICES), repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), GREEN),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, GRAY_BG]),
        ('GRID',         (0, 0), (-1, -1), 0.4, GRAY_BORDER),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',   (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 2.5),
        ('LEFTPADDING',  (0, 0), (-1, -1), 4),
    ]))
    return t


def build_sat_index_pdf(
    report_id  : str,
    farm_info  : dict,
    data       : dict,
    coords     : list | None = None,
    logo_parrot: str | None = None,
    logo_agri  : str | None = None,
) -> bytes:
    """
    Rapport « Satellite Index » (sortie de get_sat_index_full / _guest +
    agb_trend) — même gabarit que les rapports Carbon et EUDR.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=22 * mm,
        title=f'Satellite Index Report {report_id}',
        author='Agriyields',
    )
    st      = _styles()
    today   = datetime.now().strftime('%d %B %Y')
    history = [r for r in data.get('history') or [] if r.get('date')]
    history.sort(key=lambda r: r['date'])
    forecast = data.get('forecast') or {}
    period   = data.get('period') or {}
    last     = history[-1] if history else {}
    elems    = []

    elems.append(_header_table(
        logo_parrot, logo_agri,
        'SATELLITE INDEX REPORT',
        f'Generated on {today}  •  Sentinel-2 L2A  •  {period.get("from", "")} → {period.get("to", "")}',
    ))
    elems.append(Spacer(1, 5 * mm))

    ndvi, _ = _sat_val(last, 'ndvi')
    elems.append(_sat_status_badge(ndvi, last.get('date')))
    elems.append(Spacer(1, 5 * mm))

    elems += _section_bar('Farm Information', st)
    area_ha = (data.get('ltv') or {}).get('area_ha') or data.get('area_ha')
    rows = [
        ('Farm ID',     farm_info.get('farm_id') or report_id),
        ('Name',        farm_info.get('name') or data.get('name')),
        ('Geolocation', farm_info.get('geolocation') or data.get('geolocation')),
        ('Crop',        farm_info.get('crop') or (data.get('agb_trend') or {}).get('crop')),
    ]
    if area_ha:
        rows.append(('Project Area', f"{float(area_ha) * 10_000:,.2f} m²  ({float(area_ha):.2f} ha)"))
    rows += [
        ('Observation Period', f"{period.get('from', 'N/A')} → {period.get('to', 'N/A')}  ({len(history)} quarterly readings)"),
        ('Latest Reading', _quarter_label(last.get('date')) if last else 'N/A'),
    ]
    elems.append(_info_table([(k, v) for k, v in rows if v]))
    elems.append(Spacer(1, 5 * mm))

    elems.append(KeepTogether(_section_bar('Latest Vegetation Indices', st) + [_sat_latest_table(last, forecast)]))
    elems.append(Spacer(1, 5 * mm))

    charts = [_sat_index_chart(history, forecast, idx, color, lbl)
              for idx, color in SAT_CHART_INDICES
              for k, lbl, _, _ in SAT_INDICES if k == idx]
    charts = [c for c in charts if c is not None]
    if charts:
        if len(charts) % 2:
            charts.append(Paragraph('', st['body']))
        grid = Table([charts[i:i + 2] for i in range(0, len(charts), 2)], colWidths=[CONTENT_W / 2] * 2)
        grid.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                  ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0)]))
        elems.append(KeepTogether(_section_bar('Index Trends: 5-Year History & Forecast', st) + [grid]))
        elems.append(Spacer(1, 5 * mm))

    elems += _sat_agb_elems(data.get('agb_trend'), st)
    elems += _sat_ltv_elems(data.get('ltv'), st)

    if history:
        elems += _section_bar('Quarterly Readings', st)
        elems.append(_sat_history_table(history))
        elems.append(Spacer(1, 5 * mm))

    elems += _section_bar('Methodology & Interpretation', st)
    method = [(f'<b>{lbl}</b>', f'{measures}: {formula}') for _, lbl, measures, formula in SAT_INDICES]
    method += [
        ('<b>Imagery</b>', 'Sentinel-2 L2A surface reflectance, 10–20 m, via the Copernicus Data Space Statistical API. '
                           'Clouds, cloud shadows and cirrus (scene classification SCL 3, 8, 9, 10) are masked pixel by pixel; '
                           'the least cloudy scene of each quarter is used. Values are polygon means per quarter.'),
        ('<b>Status</b>', 'Each value is placed in a class (e.g. NDVI > 0.6 = Dense / Healthy, 0.3–0.6 = Moderate, 0.1–0.3 = '
                          'Sparse / Stressed) shown in colour in the tables.'),
        ('<b>Forecast</b>', 'Next quarters forecast with Prophet (seasonal time-series model) on the quarterly history, '
                            'with an 80 % confidence interval; seasonal naive forecast when the history is too short.'),
    ]
    for oob in (data.get('out_of_bounds') or [])[:5]:
        method.append(('<b>Note</b>', f"{oob.get('index', '').upper()} on {oob.get('date')}: raw value {oob.get('raw')} "
                                      f"outside [−1, 1], clamped to {oob.get('clamped_to')}."))
    mt = Table([[Paragraph(a, ParagraphStyle('mk', fontName='Helvetica-Bold', fontSize=8, textColor=GREEN)),
                 Paragraph(b, ParagraphStyle('md', fontName='Helvetica', fontSize=8, textColor=BLACK, leading=11))]
                for a, b in method], colWidths=[30 * mm, CONTENT_W - 30 * mm])
    mt.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), GRAY_BG),
        ('GRID',         (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
        ('LEFTPADDING',  (0, 0), (-1, -1), 6),
    ]))
    elems.append(mt)
    elems.append(Spacer(1, 5 * mm))

    if coords:
        map_img = _mapbox_image(coords)
        if map_img:
            elems += _section_bar('Plot Map: Satellite View', st)
            elems.append(map_img)

    doc.build(elems, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas, canvasmaker=_NumberedCanvas)
    return buf.getvalue()
