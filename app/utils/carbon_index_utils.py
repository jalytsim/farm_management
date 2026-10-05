"""
carbon_index_utils.py
──────────────────────────────────────────────────────────────────────────────
Bilan carbone d'une parcelle (ferme ou forêt) à partir des indices Sentinel-2,
en remplacement des datasets GFW (gross emissions / removals / net flux).

Indices (evalscript de sentinel_utils.py) :
  NDVI = (B08 - B04) / (B08 + B04)
  EVI  = 2.5 × (B08 - B04) / (B08 + 6·B04 - 7.5·B02 + 1)
  SAVI = 1.5 × (B08 - B04) / (B08 + B04 + 0.5)
  NDRE = (B08 - B05) / (B08 + B05)

AGB (t/ha) par lecture mensuelle :
  - culture avec modèle indice (maize, rice, wheat, cocoa) → crop_biomass_utils
    (g/m² × 0.01) ;
  - forêt, café, culture sans modèle → AGB = 1.43 × exp(6.26 × NDVI)
    (tree_co2_utils.calculate_agb_per_ha_from_ndvi).

Stock (Mg CO2e) = chaîne calculate_biomass_and_co2 (BGB 20 %, matière sèche
72.5 %, carbone 50 %, CO2/C 3.67) appliquée à AGB × surface.

Méthode des stocks (IPCC « stock-difference ») entre la lecture la plus ancienne
(≈ 12 mois avant) et la plus récente :
  ΔStock    = Stock(fin) - Stock(début)
  Removals  = max(ΔStock, 0)
  Emissions = max(-ΔStock, 0)
  Net       = Emissions - Removals  (= -ΔStock ; > 0 → source, < 0 → puits)
"""

from datetime import datetime

from dateutil.relativedelta import relativedelta

from app.utils.crop_biomass_utils import (
    INDEX_MODELS, G_M2_TO_T_HA, _index_value, biomass_from_indices, resolve_crop_key,
)
from app.utils.tree_co2_utils import (
    BGB_RATIO, CARBON_RATIO, DRY_MATTER_RATIO, NDVI_AGB_A, NDVI_AGB_B,
    calculate_agb_per_ha_from_ndvi, calculate_biomass_and_co2,
)

REPORT_INDICES = ('ndvi', 'evi', 'savi', 'ndre')

INDEX_FORMULAS = {
    'ndvi': '(B08 − B04) / (B08 + B04)',
    'evi':  '2.5 × (B08 − B04) / (B08 + 6·B04 − 7.5·B02 + 1)',
    'savi': '1.5 × (B08 − B04) / (B08 + B04 + 0.5)',
    'ndre': '(B08 − B05) / (B08 + B05)',
}

GENERIC_NDVI_FORMULA = f'AGB (t/ha) = {NDVI_AGB_A} × exp({NDVI_AGB_B} × NDVI)'


def fetch_index_rows(geometry, months=12):
    """Lectures Sentinel-2 mensuelles sur `months` + 1 mois (même mois l'an dernier inclus)."""
    from app.utils.sentinel_utils import _call_statistics, _parse_response

    now = datetime.utcnow()
    raw = _call_statistics(
        geometry,
        (now - relativedelta(months=months + 1)).strftime('%Y-%m-%dT00:00:00Z'),
        now.strftime('%Y-%m-%dT23:59:59Z'),
        interval='P1M',
    )
    rows, _ = _parse_response(raw)
    return rows


def _agb_model(crop_name, property_type):
    """(clé modèle, libellé formule). Clé None → modèle NDVI générique."""
    crop_key = resolve_crop_key(crop_name) if property_type == 'farm' else None
    if crop_key in INDEX_MODELS:
        return crop_key, f"{INDEX_MODELS[crop_key]['formula']} (g/m²)"
    return None, GENERIC_NDVI_FORMULA


def _agb_t_ha(row, crop_key):
    if crop_key:
        g_m2 = biomass_from_indices(crop_key, row)
        return None if g_m2 is None else g_m2 * G_M2_TO_T_HA
    ndvi = _index_value(row, 'ndvi')
    return None if ndvi is None else calculate_agb_per_ha_from_ndvi(float(ndvi))


def _stock(agb_t_ha, area_ha):
    agb_kg = agb_t_ha * area_ha * 1000.0
    co2 = calculate_biomass_and_co2(agb_kg)
    return {
        'agb_t_ha':  round(agb_t_ha, 4),
        'co2e_mg':   co2['co2_sequestered_kg'] / 1000.0,
        'above_c_mg': agb_kg * DRY_MATTER_RATIO * CARBON_RATIO / 1000.0,
        'below_c_mg': agb_kg * BGB_RATIO * DRY_MATTER_RATIO * CARBON_RATIO / 1000.0,
    }


def compute_carbon_from_indices(rows, area_ha, crop_name=None, property_type='farm'):
    """
    rows : lignes Sentinel {date, ndvi, evi, savi, ndre, ...} (brutes ou guest).
    Retourne (carbon_dict, error_message).
    """
    if not area_ha or area_ha <= 0:
        return None, 'Could not compute parcel area'

    crop_key, agb_formula = _agb_model(crop_name, property_type)

    series = []
    for row in rows or []:
        agb = _agb_t_ha(row, crop_key)
        if agb is None:
            continue
        stock = _stock(max(0.0, agb), area_ha)
        series.append({
            'date': row.get('date'),
            **{idx: _index_value(row, idx) for idx in REPORT_INDICES},
            'agb_t_ha': stock['agb_t_ha'],
            'stock_co2e_mg': round(stock['co2e_mg'], 4),
            '_stock': stock,
        })
    if not series:
        return None, 'No cloud-free Sentinel-2 reading available for this parcel'

    series.sort(key=lambda r: r['date'] or '')
    start, end = series[0], series[-1]
    delta = end['_stock']['co2e_mg'] - start['_stock']['co2e_mg']

    carbon = {
        'source':        'sentinel-2-indices',
        'property_type': property_type,
        'crop':          crop_name,
        'agb_model':     crop_key or 'generic_ndvi',
        'agb_formula':   agb_formula,
        'area_ha':       round(area_ha, 4),
        'start_date':    start['date'],
        'end_date':      end['date'],
        'stock_start_co2e_mg': round(start['_stock']['co2e_mg'], 4),
        'stock_end_co2e_mg':   round(end['_stock']['co2e_mg'], 4),
        'emissions':     round(max(-delta, 0.0), 4),
        'removals':      round(max(delta, 0.0), 4),
        'net':           round(-delta, 4),
        'stock_above_c': round(end['_stock']['above_c_mg'], 4),
        'stock_below_c': round(end['_stock']['below_c_mg'], 4),
        'indices':       {idx: end[idx] for idx in REPORT_INDICES},
        'index_formulas': INDEX_FORMULAS,
        'history':       [{k: v for k, v in r.items() if k != '_stock'} for r in series],
    }
    warnings = []
    if len(series) < 2:
        warnings.append('Only one cloud-free reading: emissions/removals cannot be computed (set to 0).')
    if crop_key is None and property_type == 'farm':
        warnings.append(f"No crop-specific index model for '{crop_name or 'unknown crop'}': generic NDVI biomass model used.")
    if crop_key == 'cocoa':
        from app.utils.crop_biomass_utils import COCOA_NDII_COEF
        if COCOA_NDII_COEF == 0:
            warnings.append('NDII coefficient (x) not calibrated yet: cocoa biomass uses the NDVI term only.')
    if warnings:
        carbon['warnings'] = warnings
    return carbon, None


def ring_from_report_coordinates(coordinates):
    """
    Anneau [[lon, lat], ...] depuis le champ 'coordinates' d'un rapport GFW
    (Polygon → [ring], MultiPolygon → [[ring], ...]) — premier polygone.
    """
    c = coordinates
    while isinstance(c, list) and c and isinstance(c[0], list) and c[0] and isinstance(c[0][0], list):
        c = c[0]
    if not isinstance(c, list) or len(c) < 3:
        return None
    return [[float(p[0]), float(p[1])] for p in c]


def polygon_geometry(ring):
    ring = [[float(lon), float(lat)] for lon, lat in ring]
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    return {'type': 'Polygon', 'coordinates': [ring]}
