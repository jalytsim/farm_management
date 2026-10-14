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

Stock biomasse (Mg CO2e) = chaîne calculate_biomass_and_co2 (BGB 20 %, matière
sèche 72.5 %, carbone 50 %, CO2/C 3.67) appliquée à AGB × surface.

Carbone organique du sol (SoC) : stock SoilGrids ISRIC (ocs, 0-30 cm, profondeur
par défaut IPCC pour les sols minéraux) en t C/ha × surface. C'est une carte
statique : il s'ajoute au stock total mais ne change pas les flux.
  Stock total (Mg C)    = AGB C + BGB C + SoC
  Stock total (Mg CO2e) = stock biomasse CO2e + SoC × 44/12

Historique 5 ans : lectures mensuelles sur 60 mois, moyenne annuelle du stock
et pente (régression linéaire) en Mg CO2e/an.

Méthode des stocks (IPCC « stock-difference ») sur les 12 derniers mois, entre
la lecture la plus ancienne de la fenêtre et la plus récente :
  ΔStock    = Stock(fin) - Stock(début)
  Removals  = max(ΔStock, 0)
  Emissions = max(-ΔStock, 0)
  Net       = Emissions - Removals  (= -ΔStock ; > 0 → source, < 0 → puits)
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import asyncio
import logging

from dateutil.relativedelta import relativedelta

from app.utils.crop_biomass_utils import (
    INDEX_MODELS, G_M2_TO_T_HA, _index_value, biomass_from_indices, resolve_crop_key,
)
from app.utils.tree_co2_utils import (
    BGB_RATIO, CARBON_RATIO, CO2_C_RATIO, DRY_MATTER_RATIO, NDVI_AGB_A, NDVI_AGB_B,
    calculate_agb_per_ha_from_ndvi, calculate_biomass_and_co2,
)

logger = logging.getLogger(__name__)

HISTORY_MONTHS = 60   # historique carbone : 5 ans
BALANCE_MONTHS = 12   # fenêtre émissions / absorptions
SOC_DEPTH = '0-30cm'

REPORT_INDICES = ('ndvi', 'evi', 'savi', 'ndre')

INDEX_FORMULAS = {
    'ndvi': '(B08 − B04) / (B08 + B04)',
    'evi':  '2.5 × (B08 − B04) / (B08 + 6·B04 − 7.5·B02 + 1)',
    'savi': '1.5 × (B08 − B04) / (B08 + B04 + 0.5)',
    'ndre': '(B08 − B05) / (B08 + B05)',
}

GENERIC_NDVI_FORMULA = f'AGB (t/ha) = {NDVI_AGB_A} × exp({NDVI_AGB_B} × NDVI)'


def fetch_index_rows(geometry, months=HISTORY_MONTHS):
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


def ring_centroid(ring):
    """(lat, lon) moyen des sommets — suffisant pour une maille SoilGrids de 250 m."""
    pts = ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring
    return (sum(p[1] for p in pts) / len(pts), sum(p[0] for p in pts) / len(pts))


def fetch_soc_stock(ring):
    """
    Stock de carbone organique du sol au centroïde (SoilGrids, ocs 0-30 cm,
    t C/ha). None si l'API ne répond pas — le rapport reste généré sans SoC.
    """
    from app.utils.sentinel_utils import _fetch_soc_soilgrids
    if not ring:
        return None
    lat, lon = ring_centroid(ring)
    # Les vues sont async : asyncio.run doit tourner hors de la boucle courante.
    with ThreadPoolExecutor(max_workers=1) as pool:
        data = pool.submit(asyncio.run, _fetch_soc_soilgrids(lat, lon)).result()
    # _fetch_soc_soilgrids divise par le d_factor (10) : ocs y est en kg/m²
    # (unité cible SoilGrids). 1 kg/m² = 10 t/ha.
    ocs_kg_m2 = (data or {}).get(f'ocs_{SOC_DEPTH}')
    ocs = None if ocs_kg_m2 is None else ocs_kg_m2 * 10.0
    if ocs is None:
        logger.warning(f'[Carbon] SoilGrids SOC unavailable at {lat:.5f},{lon:.5f}')
        return None
    return {
        'ocs_t_c_ha': float(ocs),
        'soc_g_kg':   (data or {}).get(f'soc_{SOC_DEPTH}') or (data or {}).get('soc_0-5cm'),
        'depth':      SOC_DEPTH,
        'lat':        round(lat, 6),
        'lon':        round(lon, 6),
        'source':     'ISRIC SoilGrids v2.0',
    }


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


def _yearly_history(series, soc_co2e_mg):
    """Stock moyen par année civile (biomasse, SoC, total) sur l'historique."""
    years = {}
    for r in series:
        if r['date']:
            years.setdefault(r['date'][:4], []).append(r['_stock']['co2e_mg'])
    out = []
    for year in sorted(years):
        vals = years[year]
        biomass = sum(vals) / len(vals)
        out.append({
            'year':                  int(year),
            'readings':              len(vals),
            'biomass_stock_co2e_mg': round(biomass, 4),
            'soc_co2e_mg':           round(soc_co2e_mg, 4) if soc_co2e_mg is not None else None,
            'total_stock_co2e_mg':   round(biomass + (soc_co2e_mg or 0.0), 4),
        })
    for prev, cur in zip(out, out[1:]):
        cur['change_co2e_mg'] = round(cur['biomass_stock_co2e_mg'] - prev['biomass_stock_co2e_mg'], 4)
    return out


def compute_carbon_from_indices(rows, area_ha, crop_name=None, property_type='farm', soc=None):
    """
    rows : lignes Sentinel {date, ndvi, evi, savi, ndre, ...} (brutes ou guest),
           idéalement 5 ans (HISTORY_MONTHS) : les flux portent sur les 12
           derniers mois, l'historique sur toute la série.
    soc  : sortie de fetch_soc_stock (optionnel).
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
    end = series[-1]
    window = series
    if end['date']:
        cutoff = (datetime.strptime(end['date'][:10], '%Y-%m-%d')
                  - relativedelta(months=BALANCE_MONTHS)).strftime('%Y-%m-%d')
        window = [r for r in series if (r['date'] or '') >= cutoff] or series
    start = window[0]
    delta = end['_stock']['co2e_mg'] - start['_stock']['co2e_mg']

    soc_c_mg = soc_co2e_mg = None
    if soc and soc.get('ocs_t_c_ha') is not None:
        soc_c_mg = soc['ocs_t_c_ha'] * area_ha
        soc_co2e_mg = soc_c_mg * CO2_C_RATIO
    biomass_c = end['_stock']['above_c_mg'] + end['_stock']['below_c_mg']
    slope = _linear_slope_per_year(
        [(r['date'], r['_stock']['co2e_mg']) for r in series if r['date']])

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
        'stock_soc_c':   round(soc_c_mg, 4) if soc_c_mg is not None else None,
        'stock_total_c': round(biomass_c + (soc_c_mg or 0.0), 4),
        'stock_total_co2e_mg': round(end['_stock']['co2e_mg'] + (soc_co2e_mg or 0.0), 4),
        'soc':           soc,
        'history_from':  series[0]['date'],
        'history_to':    end['date'],
        'history_yearly': _yearly_history(series, soc_co2e_mg),
        'trend_co2e_mg_per_year': round(slope, 4) if slope is not None else None,
        'indices':       {idx: end[idx] for idx in REPORT_INDICES},
        'index_formulas': INDEX_FORMULAS,
        'history':       [{k: v for k, v in r.items() if k != '_stock'} for r in series],
    }
    warnings = []
    if len(window) < 2:
        warnings.append('Only one cloud-free reading: emissions/removals cannot be computed (set to 0).')
    if soc_c_mg is None:
        warnings.append('Soil organic carbon unavailable (SoilGrids did not answer): total stock is biomass only.')
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


# ── Tendance AGB sur l'historique 5 ans + prévision (sat-index) ──────────────

def _agb_from_values(values, crop_key):
    """AGB (t/ha) depuis un dict {indice: valeur} ; None si un indice manque."""
    agb = _agb_t_ha(values, crop_key)
    return None if agb is None else round(max(0.0, agb), 4)


def _linear_slope_per_year(points):
    """Pente (t/ha/an) d'une régression linéaire sur [(date 'YYYY-MM-DD', agb)]."""
    if len(points) < 2:
        return None
    xs = [datetime.strptime(d[:10], '%Y-%m-%d').toordinal() / 365.25 for d, _ in points]
    ys = [v for _, v in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def compute_agb_trend(history, forecast, crop_name=None, property_type='farm', area_ha=None):
    """
    Applique la formule AGB de la culture à chaque lecture de l'historique
    (≈ 5 ans, trimestriel) et à chaque trimestre prévu (Prophet / seasonal naive).

    history  : lignes {date, ndvi: {value,...} | float, ...}
    forecast : {indice: [{date, quarter, value, lower_80, upper_80}, ...]}
    Les formules sont croissantes en chaque indice → l'intervalle 80 % de l'AGB
    est obtenu en appliquant la formule aux bornes basses / hautes des indices.
    """
    crop_key, agb_formula = _agb_model(crop_name, property_type)
    needed = INDEX_MODELS[crop_key]['indices'] if crop_key else ('ndvi',)

    def _stock_mg(agb):
        if agb is None or not area_ha:
            return None
        return round(calculate_biomass_and_co2(agb * area_ha * 1000.0)['co2_sequestered_kg'] / 1000.0, 4)

    hist_out = []
    for row in history or []:
        agb = _agb_from_values(row, crop_key)
        if agb is None:
            continue
        hist_out.append({'date': row.get('date'), 'agb_t_ha': agb, 'stock_co2e_mg': _stock_mg(agb)})
    hist_out.sort(key=lambda r: r['date'] or '')

    # Prévisions indexées par date ; on ne garde que les trimestres où tous les indices requis existent
    by_date = {}
    for idx in needed:
        for f in (forecast or {}).get(idx) or []:
            by_date.setdefault(f['date'], {'quarter': f.get('quarter')})[idx] = f
    fc_out = []
    for date in sorted(by_date):
        entry = by_date[date]
        if not all(idx in entry for idx in needed):
            continue
        agb = _agb_from_values({idx: entry[idx]['value'] for idx in needed}, crop_key)
        lo  = _agb_from_values({idx: entry[idx].get('lower_80', entry[idx]['value']) for idx in needed}, crop_key)
        hi  = _agb_from_values({idx: entry[idx].get('upper_80', entry[idx]['value']) for idx in needed}, crop_key)
        if agb is None:
            continue
        fc_out.append({
            'date': date, 'quarter': entry.get('quarter'),
            'agb_t_ha': agb, 'lower_80': lo, 'upper_80': hi,
            'stock_co2e_mg': _stock_mg(agb), 'is_forecast': True,
        })

    slope_hist = _linear_slope_per_year([(r['date'], r['agb_t_ha']) for r in hist_out])
    last = hist_out[-1]['agb_t_ha'] if hist_out else None
    end  = fc_out[-1]['agb_t_ha'] if fc_out else None
    change_pct = round((end - last) / last * 100, 2) if last and end is not None else None

    if slope_hist is None:
        direction = None
    elif abs(slope_hist) < 0.01 * max(last or 0, 1e-6):
        direction = 'stable'
    else:
        direction = 'increasing' if slope_hist > 0 else 'decreasing'

    return {
        'crop':         crop_name,
        'agb_model':    crop_key or 'generic_ndvi',
        'agb_formula':  agb_formula,
        'unit':         't/ha',
        'area_ha':      round(area_ha, 4) if area_ha else None,
        'history':      hist_out,
        'forecast':     fc_out,
        'summary': {
            'history_from':           hist_out[0]['date'] if hist_out else None,
            'history_to':             hist_out[-1]['date'] if hist_out else None,
            'mean_agb_t_ha':          round(sum(r['agb_t_ha'] for r in hist_out) / len(hist_out), 4) if hist_out else None,
            'slope_t_ha_per_year':    round(slope_hist, 4) if slope_hist is not None else None,
            'direction':              direction,
            'last_agb_t_ha':          last,
            'forecast_end_agb_t_ha':  end,
            'forecast_change_pct':    change_pct,
        },
    }
