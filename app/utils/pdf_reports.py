"""
pdf_reports.py
──────────────────────────────────────────────────────────────────────────────
Génération 100 % backend des rapports PDF avec ReportLab.
Aucune dépendance navigateur, aucun HTML à parser.

Rapports disponibles :
  • build_eudr_farm_pdf(farm_id, farm_info, gfw_data)   → bytes
  • build_eudr_forest_pdf(forest_id, forest_info, gfw_data) → bytes
  • build_carbon_farm_pdf(farm_id, farm_info, report)   → bytes
  • build_carbon_forest_pdf(forest_id, forest_info, report) → bytes

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
from datetime import datetime
from shapely.geometry import Polygon

from reportlab.lib              import colors
from reportlab.lib.pagesizes    import A4
from reportlab.lib.units        import mm
from reportlab.lib.styles       import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums        import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus         import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, HRFlowable, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, String
from reportlab.pdfbase          import pdfmetrics

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
    """Retourne une table avec le badge de conformité coloré."""
    if status == '100% Compliant':
        bg, fc = GREEN_LIGHT, colors.HexColor('#1b5e20')
        icon = '✓'
    elif status == 'Compliant':
        # No forest cover, but tree cover loss detected — compliant, shade-tree planting recommended
        bg, fc = GREEN_LIGHT, colors.HexColor('#2e7d32')
        icon = '✓'
    elif status == 'Not Compliant':
        bg, fc = RED_LIGHT, RED
        icon = '✗'
    else:
        bg, fc = GRAY_BG, MUTED
        icon = '?'

    st = _styles()
    badge_para = Paragraph(
        f'<b>{icon}  {status}</b>',
        ParagraphStyle('badge', fontName='Helvetica-Bold', fontSize=13,
                       textColor=fc, alignment=TA_LEFT)
    )
    desc_para = Paragraph(description or '', _styles()['small'])
    t = Table([[badge_para], [desc_para]],
              colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (0, -1), bg),
        ('BOX',          (0, 0), (-1, -1), 1, GRAY_BORDER),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ('LEFTPADDING',  (0, 0), (-1, -1), 12),
        ('ROUNDEDCORNERS', [5]),
    ]))
    return t





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
    except Exception:
        return 0.0, 0.0


def _calc_area_ha_simple(coordinates: list) -> tuple[float, float]:
    """Calcul d'aire simplifié sans pyproj (shapely seul, degrés → m² approx)."""
    try:
        poly = Polygon(coordinates)
        # Correction latitude : 1 degré lat ≈ 111 320 m, 1 degré lon ≈ 111 320 * cos(lat) m
        import math
        lat_c = sum(c[1] for c in coordinates) / len(coordinates)
        scale = 111_320 * 111_320 * math.cos(math.radians(lat_c))
        area_m2 = abs(poly.area) * scale
        return area_m2, area_m2 / 10_000
    except Exception:
        return 0.0, 0.0


def _compliance_status(tree_cover_loss: float, has_forest: bool) -> dict:
    """
    Règles (ordre de priorité strict — corrigé) :
    1) Forest cover detected (JRC 2020)            -> Not Compliant, quel que soit le tree cover loss
    2) No forest cover AND no tree cover loss       -> 100% Compliant
    3) No forest cover AND tree cover loss detected -> Compliant, plantation d'arbres d'ombrage recommandée
    """
    if has_forest:
        return {
            'status':      'Not Compliant',
            'description': 'Forest cover detected on this plot (EUDR Article 2). Not compliant with EUDR regulations, regardless of tree cover loss status.',
        }

    if tree_cover_loss == 0:
        return {
            'status':      '100% Compliant',
            'description': 'No forest cover and no tree cover loss detected. Fully compliant with EUDR regulations.',
        }

    return {
        'status':      'Compliant',
        'description': (
            'No forest cover detected, but tree cover loss was recorded since 2020. Before finalizing this '
            'status, verify whether the loss results from cyclical agroforestry practices (e.g. routine canopy '
            'pruning, tree stumping, or shade-tree rejuvenation/cutting for pest mitigation) rather than '
            'deforestation. Planting shade trees is recommended.'
        ),
    }


def _extract_eudr_metrics(gfw_data: dict) -> dict:
    """
    Extrait et calcule toutes les métriques EUDR depuis les données GFW brutes.
    gfw_data : dict groupé par dataset (format retourné par /report)
    """
    m = {}

    # Coordonnées
    coords = (
        gfw_data.get('jrc global forest cover', [{}])[0].get('coordinates', [[]])[0]
        or gfw_data.get('tree cover loss', [{}])[0].get('coordinates', [[]])[0]
        or gfw_data.get('soil carbon', [{}])[0].get('coordinates', [[]])[0]
    )
    m['coordinates'] = coords
    m['area_m2'], m['area_ha'] = _calc_area_ha_simple(coords) if coords else (0, 0)

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
    m['protected_pct'] = prot_pct or {'No data': '–'}

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
    m['compliance'] = _compliance_status(m['tree_cover_loss_ha'], m['has_forest'])

    return m


# ══════════════════════════════════════════════════════════════════════════════
# EUDR COMPLIANCE TABLE  (ReportLab)
# ══════════════════════════════════════════════════════════════════════════════

def _eudr_compliance_table(m: dict) -> Table:
    st = _styles()

    def cell(text, bold=False, color=BLACK):
        fn = 'Helvetica-Bold' if bold else 'Helvetica'
        return Paragraph(f'<font name="{fn}">{text}</font>',
                         ParagraphStyle('c', fontName=fn, fontSize=8,
                                        textColor=color, leading=11))

    tcl_color  = GREEN if m['tree_cover_loss_ha'] == 0 else RED
    radd_color = GREEN if m['radd_ha'] == 0 else RED
    cs         = m['compliance']
    cs_color   = (colors.HexColor('#1b5e20') if cs['status'] == '100% Compliant'
                  else colors.HexColor('#2e7d32') if cs['status'] == 'Compliant' else RED)
    fc_color   = ORANGE if m['has_forest'] else GREEN

    prot_text = '\n'.join(f'{k}: {v}' for k, v in m['protected_pct'].items())
    vc_text   = '  '.join(
        f'Decile {r["decile"]}: {r["count"]}'
        for r in m['val_counts'] if r['count'] > 0
    ) or 'No data'

    # ✅ FIX (annotation PDF) : le ratio n'est plus recalculé/affiché ici sur la ligne
    # "Country Deforestation Risk" — il est déjà calculé (et plafonné) dans
    # _extract_eudr_metrics et affiché sur la ligne "Tree Cover Loss" ci-dessous.
    loss_ratio_text = f"{m['tree_cover_loss_ha']} ha — "
    if m['tree_cover_loss_ha'] == 0:
        loss_ratio_text += 'No loss detected ✓'
    else:
        loss_ratio_text += f"Loss detected ⚠ — Tree loss ratio: {m['tree_cover_loss_ratio']:.2f}% of plot area"
        if m.get('tree_cover_loss_capped'):
            loss_ratio_text += ' (capped — source value exceeded plot area, please verify)'

    rows = [
        # Header
        [cell('Metric', bold=True), cell('Value / Assessment', bold=True)],
        # Data rows
        [cell('Project Area'),
         cell(f"{m['area_ha']:.2f} ha  ({m['area_m2']:.0f} m²)")],

        [cell('Country Deforestation Risk'),
         cell('STANDARD')],

        [cell('RADD Alert'),
         cell(f"{m['radd_ha']} ha — {'No alert ✓' if m['radd_ha']==0 else 'Alert detected ⚠'}",
              color=radd_color)],

        [cell('Tree Cover Loss (since 2020)'),
         cell(loss_ratio_text, color=tcl_color)],

        [cell('Forest Cover (JRC 2020)'),
         cell(m['forest_cover_text'], color=fc_color)],

        [cell('EUDR Compliance'),
         cell(f"{cs['status']}  —  {cs['description']}", bold=True, color=cs_color)],

        [cell('Protected Area Status'),
         cell(prot_text)],

        [cell('Tree Cover Extent'),
         cell(f"Coverage: {m['cover_pct']:.1f}%  —  Non-zero pts: {m['cover_count']}\n{vc_text}")],

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
        title=f'EUDR Compliance Report — {farm_id}',
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
            f"located in {location_val if location_val else 'N/A'}. The farm is a member of the 1 and plays a "
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
    if m['area_ha']:
        rows.append(('Farm Area', f"{m['area_ha']:.2f} ha  ({m['area_m2']:.0f} m²)"))
    elems.append(_info_table(rows))
    elems.append(Spacer(1, 5 * mm))

    # ── Regulatory framework ──────────────────────────────────────────────────
    elems += _section_bar('Regulatory Framework (EU) 2023/1115', st)
    articles = [
        ('1. RADD Alert (Article 2)',
         'Applicable to most parts of Uganda, only parts of Lake Albert region neighbouring DRC Congo.'),
        ('2. Tree Cover Loss (Article 2)',
         'Area in which tree loss was identified since December 2020. Zero = Fully compliant. Non-Zero = Likely non-compliant.'),
        ('3. Forest Cover (Article 2)',
         'EU JRC Geostore for forest cover as of 2020. None detected = fully compliant. Forest detected = requires assessment.'),
        ('4. Tree Cover Extent (Article 2)',
         'Analysis of tree cover expressed in deciles (0–100) to evaluate forest coverage within the farm boundary.'),
        ('5. Tree Cover Loss Drivers (Article 10)',
         'Identifies the primary causes of deforestation or forest degradation.'),
        ('6. Protected Area (Article 10)',
         'Indicates if the plot is in a gazetted protected area (national park, wetland, game reserve).'),
        ('7. Indigenous and Community Lands (Article 10)',
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
    elems.append(_eudr_compliance_table(m))
    elems.append(Spacer(1, 5 * mm))

    # ── Risk assessment breakdown ─────────────────────────────────────────────
    elems += _section_bar('Risk Assessment Breakdown', st)
    risk_rows = [
        ('Farm Area',               f"{m['area_ha']:.2f} ha"),
        ('Tree Cover Loss',         f"{m['tree_cover_loss_ha']} ha ({m['tree_cover_loss_ratio']:.2f}%)"),
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
            elems += _section_bar('Plot Map — Satellite View', st)
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
            
            elems += _section_bar('Tree Cover Spatial Analysis — Heatmap View', st)
            elems.append(forest_img)
            elems.append(Spacer(1, 3 * mm))
        except Exception as e:
            print(f"Erreur d'intégration de la carte forestière : {e}")

    doc.build(elems, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas)
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
        title=f'EUDR Compliance Report — Forest {forest_id}',
        author='Agriyields',
    )
    st    = _styles()
    today = datetime.now().strftime('%d %B %Y')
    m     = _extract_eudr_metrics(gfw_data)
    elems = []

    elems.append(_header_table(
        logo_parrot, logo_agri,
        'EUDR COMPLIANCE REPORT — FOREST',
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
            elems += _section_bar('Plot Map — Satellite View', st)
            elems.append(map_img)

    doc.build(elems, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# BUILD CARBON FARM PDF
# ══════════════════════════════════════════════════════════════════════════════

def _carbon_table(vals: dict) -> Table:
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

    rows = [
        [Paragraph('<b>Category</b>',        _styles()['body_bold']),
         Paragraph('<b>Value (Mg CO₂e)</b>', _styles()['body_bold'])],
        [Paragraph('Carbon Gross Emissions',             _styles()['body']),
         badge_cell(vals['emissions'], BADGE_COLORS['emissions'])],
        [Paragraph('Carbon Gross Absorption (Removals)', _styles()['body']),
         badge_cell(vals['removals'],  BADGE_COLORS['removals'])],
        [Paragraph('Carbon Net Emissions',               _styles()['body']),
         badge_cell(vals['net'],
                    BADGE_COLORS['net_pos'] if vals['net'] >= 0 else BADGE_COLORS['net_neg'])],
        [Paragraph('Sequestration Potential (Belowground)', _styles()['body']),
         Paragraph(f"{vals['seq_below']:.4f} Mg C", _styles()['body'])],
        [Paragraph('Sequestration Potential (Aboveground)', _styles()['body']),
         Paragraph(f"{vals['seq_above']:.4f} Mg C", _styles()['body'])],
    ]

    t = Table(rows, colWidths=[CONTENT_W * 0.65, CONTENT_W * 0.35])
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


def build_carbon_farm_pdf(
    farm_id    : str,
    farm_info  : dict,
    report     : list,
    logo_parrot: str | None = None,
    logo_agri  : str | None = None,
) -> bytes:
    """Génère le rapport Carbon pour une ferme."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=22 * mm,
        title=f'Carbon Emissions Assessment — {farm_id}',
        author='Agriyields',
    )
    st    = _styles()
    today = datetime.now().strftime('%d %B %Y')
    elems = []

    # Extraire les valeurs
    emissions  = (report[0].get('data_fields', {}).get('gfw_forest_carbon_gross_emissions__Mg_CO2e', 0) or 0) if len(report) > 0 else 0
    removals   = (report[1].get('data_fields', {}).get('gfw_forest_carbon_gross_removals__Mg_CO2e',  0) or 0) if len(report) > 1 else 0
    net        = (report[2].get('data_fields', {}).get('gfw_forest_carbon_net_flux__Mg_CO2e',        0) or 0) if len(report) > 2 else 0
    seq_below  = (report[3].get('data_fields', {}).get('gfw_reforestable_extent_belowground_carbon_potential_sequestration__Mg_C', 0) or 0) if len(report) > 3 else 0
    seq_above  = (report[4].get('data_fields', {}).get('gfw_reforestable_extent_aboveground_carbon_potential_sequestration__Mg_C', 0) or 0) if len(report) > 4 else 0
    coords     = report[0].get('coordinates', [[]])[0] if report else []

    area_m2, area_ha = _calc_area_ha_simple(coords) if coords else (0, 0)
    net_positive     = net >= 0

    vals = {'emissions': emissions, 'removals': removals,
            'net': net, 'seq_below': seq_below, 'seq_above': seq_above}

    # ── En-tête ──────────────────────────────────────────────────────────────
    elems.append(_header_table(
        logo_parrot, logo_agri,
        'CARBON EMISSIONS ASSESSMENT',
        f'Generated on {today}  •  Regulation (EU) 2023/1115',
    ))
    elems.append(Spacer(1, 5 * mm))

    # ── Net status badge ──────────────────────────────────────────────────────
    status_text = ('⚠  Net Carbon Source' if net_positive else '✓  Net Carbon Sink')
    status_bg   = RED_LIGHT if net_positive else GREEN_LIGHT
    status_color= RED if net_positive else GREEN
    badge_t = Table([[Paragraph(f'<b>{status_text}</b>',
                     ParagraphStyle('nb', fontName='Helvetica-Bold', fontSize=12,
                                    textColor=status_color))]],
                    colWidths=[CONTENT_W])
    badge_t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), status_bg),
        ('BOX',          (0, 0), (-1, -1), 1, GRAY_BORDER),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ('LEFTPADDING',  (0, 0), (-1, -1), 14),
    ]))
    elems.append(badge_t)
    elems.append(Spacer(1, 5 * mm))

    # ── Farm info ─────────────────────────────────────────────────────────────
    elems += _section_bar('Farm Information', st)
    rows = [
        ('Farm ID',      farm_info.get('farm_id', farm_id)),
        ('Owner',        farm_info.get('name')),
        ('Geolocation',  farm_info.get('geolocation')),
    ]
    if farm_info.get('crops'):
        rows.append(('Primary Crop', farm_info['crops'][0].get('crop', 'N/A')))
        rows.append(('Land Type',    farm_info['crops'][0].get('land_type', 'N/A')))
    if area_ha:
        rows.append(('Project Area', f"{area_m2:.2f} m²  ({area_ha:.2f} ha)"))
    elems.append(_info_table(rows))
    elems.append(Spacer(1, 5 * mm))

    # ── Carbon table + pie chart côte à côte ─────────────────────────────────
    elems += _section_bar('Carbon Assessment Summary', st)

    pie = _pie_chart_image({
        'Gross Emissions': abs(emissions),
        'Gross Removals':  abs(removals),
        'Net Flux':        abs(net),
        'Sequestration':   abs(seq_below),
    }, size=60 * mm)

    side_t = Table(
        [[_carbon_table(vals), pie]],
        colWidths=[CONTENT_W - 68 * mm, 68 * mm],
    )
    side_t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elems.append(side_t)
    elems.append(Spacer(1, 5 * mm))

    # ── Interpretation box ────────────────────────────────────────────────────
    elems += _section_bar('Carbon Balance Interpretation', st)
    interp = [
        ('<b>Gross Emissions</b>', 'Carbon released through land-use change and disturbances.'),
        ('<b>Gross Removals</b>',  'Carbon absorbed by forest growth and regeneration.'),
        ('<b>Net Flux</b>',        f'Balance: {"positive = net source ⚠" if net_positive else "negative = net sink ✓"}. Current value: {net:.4f} Mg CO₂e.'),
        ('<b>Sequestration</b>',   f'Reforestation potential — Belowground: {seq_below:.4f} Mg C, Aboveground: {seq_above:.4f} Mg C.'),
    ]
    interp_data = [
        [Paragraph(t, ParagraphStyle('ik', fontName='Helvetica-Bold', fontSize=8,
                                     textColor=GREEN)),
         Paragraph(d, ParagraphStyle('id', fontName='Helvetica', fontSize=8,
                                     textColor=BLACK, leading=11))]
        for t, d in interp
    ]
    interp_t = Table(interp_data, colWidths=[42 * mm, CONTENT_W - 42 * mm])
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

    # ── Satellite map ─────────────────────────────────────────────────────────
    if coords:
        map_img = _mapbox_image(coords)
        if map_img:
            elems += _section_bar('Plot Map — Satellite View', st)
            elems.append(map_img)

    doc.build(elems, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# BUILD CARBON FOREST PDF
# ══════════════════════════════════════════════════════════════════════════════

def build_carbon_forest_pdf(
    forest_id  : int | str,
    forest_info: dict,
    report     : list,
    logo_parrot: str | None = None,
    logo_agri  : str | None = None,
) -> bytes:
    """Génère le rapport Carbon pour une forêt — même structure que farm."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=22 * mm,
        title=f'Carbon Emissions Assessment — Forest {forest_id}',
        author='Agriyields',
    )
    st    = _styles()
    today = datetime.now().strftime('%d %B %Y')
    elems = []

    emissions = (report[0].get('data_fields', {}).get('gfw_forest_carbon_gross_emissions__Mg_CO2e', 0) or 0) if len(report) > 0 else 0
    removals  = (report[1].get('data_fields', {}).get('gfw_forest_carbon_gross_removals__Mg_CO2e',  0) or 0) if len(report) > 1 else 0
    net       = (report[2].get('data_fields', {}).get('gfw_forest_carbon_net_flux__Mg_CO2e',        0) or 0) if len(report) > 2 else 0
    seq_below = (report[3].get('data_fields', {}).get('gfw_reforestable_extent_belowground_carbon_potential_sequestration__Mg_C', 0) or 0) if len(report) > 3 else 0
    seq_above = (report[4].get('data_fields', {}).get('gfw_reforestable_extent_aboveground_carbon_potential_sequestration__Mg_C', 0) or 0) if len(report) > 4 else 0
    coords    = report[0].get('coordinates', [[]])[0] if report else []

    area_m2, area_ha = _calc_area_ha_simple(coords) if coords else (0, 0)
    net_positive     = net >= 0
    vals = {'emissions': emissions, 'removals': removals,
            'net': net, 'seq_below': seq_below, 'seq_above': seq_above}

    elems.append(_header_table(
        logo_parrot, logo_agri,
        'CARBON EMISSIONS ASSESSMENT — FOREST',
        f'Generated on {today}  •  Regulation (EU) 2023/1115',
    ))
    elems.append(Spacer(1, 5 * mm))

    status_text = '⚠  Net Carbon Source' if net_positive else '✓  Net Carbon Sink'
    badge_t = Table(
        [[Paragraph(f'<b>{status_text}</b>',
          ParagraphStyle('nb', fontName='Helvetica-Bold', fontSize=12,
                         textColor=RED if net_positive else GREEN))]],
        colWidths=[CONTENT_W])
    badge_t.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), RED_LIGHT if net_positive else GREEN_LIGHT),
        ('BOX',          (0, 0), (-1, -1), 1, GRAY_BORDER),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ('LEFTPADDING',  (0, 0), (-1, -1), 14),
    ]))
    elems.append(badge_t)
    elems.append(Spacer(1, 5 * mm))

    elems += _section_bar('Forest Information', st)
    rows = [
        ('Forest Name',  forest_info.get('name')),
        ('Tree Type',    forest_info.get('tree_type', 'N/A')),
        ('Date Created', forest_info.get('date_created', 'N/A')),
        ('Last Updated', forest_info.get('date_updated', 'N/A')),
    ]
    if area_ha:
        rows.append(('Project Area', f"{area_m2:.2f} m²  ({area_ha:.2f} ha)"))
    elems.append(_info_table(rows))
    elems.append(Spacer(1, 5 * mm))

    elems += _section_bar('Carbon Assessment Summary', st)
    pie = _pie_chart_image({
        'Gross Emissions': abs(emissions),
        'Gross Removals':  abs(removals),
        'Net Flux':        abs(net),
        'Sequestration':   abs(seq_below),
    }, size=60 * mm)
    side_t = Table(
        [[_carbon_table(vals), pie]],
        colWidths=[CONTENT_W - 68 * mm, 68 * mm],
    )
    side_t.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elems.append(side_t)
    elems.append(Spacer(1, 5 * mm))

    if coords:
        map_img = _mapbox_image(coords)
        if map_img:
            elems += _section_bar('Plot Map — Satellite View', st)
            elems.append(map_img)

    doc.build(elems, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas)
    return buf.getvalue()