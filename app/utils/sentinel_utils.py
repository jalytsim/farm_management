"""
sentinel_utils.py — Sentinel-2 + Prophet ML Forecast

Changes in this version:
  - INDEX_LTV_CONFIG: per-index agronomic parameters (optimal, invert, weight, factor logic)
  - _compute_index_factor: normalises any index value to a crop-productivity factor [0.3, 1.0]
  - compute_ltv_multi: replaces compute_ltv — returns per-index breakdown + weighted composite
    · backward-compatible keys kept at top level (ndvi_factor, adjusted_yield_t_ha, …)
  - get_sat_index_full: both cache and fresh-data paths now call compute_ltv_multi
  - _parse_response returns (data, out_of_bounds_log) tuple (unchanged from previous version)
"""

import os, time, warnings, logging
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

# SENTINEL_CLIENT_ID     = os.environ.get('SENTINEL_CLIENT_ID',     '932e6314-b550-4211-9680-02c6c1b8acf6')
# SENTINEL_CLIENT_SECRET = os.environ.get('SENTINEL_CLIENT_SECRET', 'WghCT9aY9eA9fq6a6OsBw9zeYv4FTwhv')
# TOKEN_URL = 'https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token'
# STATS_URL = 'https://services.sentinel-hub.com/api/v1/statistics'


SENTINEL_CLIENT_ID     = os.environ.get('SENTINEL_CLIENT_ID',     'sh-07766274-9bf2-47ca-9396-9377b3fb4fbc')
SENTINEL_CLIENT_SECRET = os.environ.get('SENTINEL_CLIENT_SECRET', 'AIYhNwWvbtCrSbSyLspjBEPBNiBZy79T')

TOKEN_URL = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
STATS_URL = 'https://sh.dataspace.copernicus.eu/api/v1/statistics'

_token_cache = {'token': None, 'expires_at': 0}


def _get_token():
    now = time.time()
    if _token_cache['token'] and _token_cache['expires_at'] > now + 60:
        return _token_cache['token']
    resp = requests.post(TOKEN_URL, data={
        'grant_type':    'client_credentials',
        'client_id':     SENTINEL_CLIENT_ID,
        'client_secret': SENTINEL_CLIENT_SECRET,
    }, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=15)
    resp.raise_for_status()
    d = resp.json()
    _token_cache['token']      = d['access_token']
    _token_cache['expires_at'] = now + d.get('expires_in', 3600)
    return _token_cache['token']


EVALSCRIPT = """//VERSION=3
function setup(){return{input:[{bands:['B02','B03','B04','B08','B11','B12','dataMask']}],output:[
  {id:'ndvi',bands:1},{id:'ndmi',bands:1},{id:'ndwi',bands:1},{id:'nmdi',bands:1},
  {id:'evi',bands:1},{id:'savi',bands:1},{id:'nbr',bands:1},{id:'bsi',bands:1},
  {id:'dataMask',bands:1}
]};}
function clamp(v,lo,hi){return Math.max(lo,Math.min(hi,v));}
function evaluatePixel(s){
  if(s.dataMask===0)return{ndvi:[0],ndmi:[0],ndwi:[0],nmdi:[0],evi:[0],savi:[0],nbr:[0],bsi:[0],dataMask:[0]};
  var ndvi=(s.B08-s.B04)/(s.B08+s.B04+1e-10);
  var ndmi=(s.B08-s.B11)/(s.B08+s.B11+1e-10);
  var ndwi=(s.B03-s.B08)/(s.B03+s.B08+1e-10);
  var nmdiD=s.B08+(s.B11-s.B12); var nmdi=Math.abs(nmdiD)>1e-6?(s.B08-(s.B11-s.B12))/nmdiD:0;
  var eviD=s.B08+6*s.B04-7.5*s.B02+1; var evi=Math.abs(eviD)>1e-6?2.5*(s.B08-s.B04)/eviD:0;
  var savi=1.5*(s.B08-s.B04)/(s.B08+s.B04+0.5+1e-10);
  var nbr=(s.B08-s.B12)/(s.B08+s.B12+1e-10);
  var bsiD=(s.B11+s.B04)+(s.B08+s.B02); var bsi=Math.abs(bsiD)>1e-6?((s.B11+s.B04)-(s.B08+s.B02))/bsiD:0;
  return{
    ndvi:[clamp(ndvi,-1,1)],ndmi:[clamp(ndmi,-1,1)],ndwi:[clamp(ndwi,-1,1)],nmdi:[clamp(nmdi,-1,1)],
    evi:[clamp(evi,-1,1)],savi:[clamp(savi,-1,1)],nbr:[clamp(nbr,-1,1)],bsi:[clamp(bsi,-1,1)],
    dataMask:[s.dataMask]
  };
}"""  


def _call_statistics(geometry, date_from, date_to):
    token   = _get_token()
    payload = {
        'input': {
            'bounds': {'geometry': geometry},
            'data': [{'type': 'sentinel-2-l2a', 'dataFilter': {
                'timeRange':       {'from': date_from, 'to': date_to},
                'maxCloudCoverage': 30,
            }}],
        },
        'aggregation': {
            'timeRange':           {'from': date_from, 'to': date_to},
            'aggregationInterval': {'of': 'P3M'},
            'resx': 0.0001, 'resy': 0.0001,
            'evalscript': EVALSCRIPT,
        },
        'calculations': {'default': {}},
    }
    resp = requests.post(
        STATS_URL, json=payload,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()


def _parse_response(api_response):
    """
    Parse the Sentinel Statistics API response.

    Returns:
        (result, out_of_bounds_log)
        result           : list of row dicts  {date, idx, idx_raw, ...}
        out_of_bounds_log: list of dicts      {date, index, raw, clamped_to}
    """
    result            = []
    out_of_bounds_log = []

    for item in api_response.get('data', []):
        date = item['interval']['from'][:10]
        row  = {'date': date}

        for idx, idx_data in item.get('outputs', {}).items():
            if idx == 'dataMask':
                continue
            try:
                raw_val = float(idx_data['bands']['B0']['stats']['mean'])

                if raw_val != raw_val:  # NaN check
                    row[idx]           = None
                    row[f'{idx}_raw']  = None
                else:
                    is_oob = raw_val < -1.0 or raw_val > 1.0
                    if is_oob:
                        entry = {
                            'date':       date,
                            'index':      idx,
                            'raw':        round(raw_val, 6),
                            'clamped_to': round(max(-1.0, min(1.0, raw_val)), 6),
                        }
                        out_of_bounds_log.append(entry)
                        logger.warning(
                            f'[Sentinel] OUT_OF_BOUNDS {idx}@{date}: '
                            f'raw={raw_val:.6f} — clamped to [-1, 1]'
                        )

                    row[idx]          = round(max(-1.0, min(1.0, raw_val)), 4)
                    row[f'{idx}_raw'] = round(raw_val, 4)

            except Exception:
                row[idx]          = None
                row[f'{idx}_raw'] = None

        result.append(row)

    return result, out_of_bounds_log


# ── Tiers ────────────────────────────────────────────────────────────────────
TIERS = {
    'ndvi': [
        {'max': -0.10, 'label': 'Water / Ice',               'color': '#0284c7', 'bg': '#eff6ff'},
        {'max':  0.10, 'label': 'Barren Land',                'color': '#92400e', 'bg': '#fef3c7'},
        {'max':  0.30, 'label': 'Sparse / Stressed',          'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  0.60, 'label': 'Moderate Vegetation',        'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  1.00, 'label': 'Dense / Healthy',            'color': '#15803d', 'bg': '#dcfce7'},
    ],
    'evi': [
        {'max':  0.00, 'label': 'Water / Barren',             'color': '#0284c7', 'bg': '#eff6ff'},
        {'max':  0.20, 'label': 'Dry / Stressed',             'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  1.00, 'label': 'Healthy Vegetation',         'color': '#15803d', 'bg': '#dcfce7'},
    ],
    'savi': [
        {'max':  0.10, 'label': 'Non-Vegetated',              'color': '#92400e', 'bg': '#fef3c7'},
        {'max':  0.30, 'label': 'Sparse / Stressed',          'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  1.00, 'label': 'Dense / Healthy',            'color': '#15803d', 'bg': '#dcfce7'},
    ],
    'ndmi': [
        {'max': -0.60, 'label': 'Bare Soil / Severe Drought', 'color': '#7f1d1d', 'bg': '#fef2f2'},
        {'max': -0.20, 'label': 'Dry / Sparse Canopy',        'color': '#dc2626', 'bg': '#fef2f2'},
        {'max':  0.00, 'label': 'Water Stress',               'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  0.20, 'label': 'Initial Water Stress',       'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  0.40, 'label': 'Low Water Stress',           'color': '#16a34a', 'bg': '#f0fdf4'},
        {'max':  1.00, 'label': 'High Moisture',              'color': '#0284c7', 'bg': '#eff6ff'},
    ],
    'ndwi': [
        {'max': -0.30, 'label': 'High Water Stress',          'color': '#dc2626', 'bg': '#fef2f2'},
        {'max':  0.00, 'label': 'Moderate Drought',           'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  0.30, 'label': 'Shallow / Wetland',          'color': '#16a34a', 'bg': '#f0fdf4'},
        {'max':  1.00, 'label': 'Clear Water',                'color': '#0284c7', 'bg': '#eff6ff'},
    ],
    'nmdi': [
        {'max':  0.60, 'label': 'Wet Soil',                   'color': '#0284c7', 'bg': '#eff6ff'},
        {'max':  0.70, 'label': 'Moderate Drought',           'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  1.00, 'label': 'Extremely Dry',              'color': '#dc2626', 'bg': '#fef2f2'},
    ],
    'nbr': [
        {'max': -0.10, 'label': 'Burned Area',                'color': '#7f1d1d', 'bg': '#fef2f2'},
        {'max':  0.10, 'label': 'Bare / Dry Soil',            'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  1.00, 'label': 'Healthy Vegetation',         'color': '#15803d', 'bg': '#dcfce7'},
    ],
    'bsi': [
        {'max':  0.00, 'label': 'Good Vegetation',            'color': '#15803d', 'bg': '#dcfce7'},
        {'max':  0.10, 'label': 'Sparse / Mixed',             'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  1.00, 'label': 'Bare Soil',                  'color': '#92400e', 'bg': '#fef3c7'},
    ],
}


def get_tier(index_name, value):
    if value is None:
        return {'label': 'N/A', 'color': '#9ca3af', 'bg': '#f9fafb'}
    for t in TIERS.get(index_name, TIERS['ndvi']):
        if value <= t['max']:
            return {'label': t['label'], 'color': t['color'], 'bg': t['bg']}
    last = TIERS.get(index_name, TIERS['ndvi'])[-1]
    return {'label': last['label'], 'color': last['color'], 'bg': last['bg']}


# ══════════════════════════════════════════════════════════════════════════════
# MULTI-INDEX LTV
# ══════════════════════════════════════════════════════════════════════════════

# Per-index agronomic parameters used to derive a crop-productivity factor.
#
# optimal   : reference value at which factor = 1.0 (best expected crop output)
# invert    : True  → lower index value = better agronomic condition (NMDI, BSI)
#             False → higher index value = better (NDVI, EVI, SAVI, NDMI, NDWI, NBR)
# range_lo  : natural lower bound of the index (used for normalisation)
# range_hi  : natural upper bound
# weight    : contribution to the weighted composite (must sum to 1.0)
# icon / label / color: display metadata
#
# Agronomic rationale
# -------------------
# NDVI  (0.70) : dense, healthy canopy → strongest yield signal, highest weight
# EVI   (0.50) : corrects atmospheric effects; independent NDVI complement
# SAVI  (0.50) : soil-adjusted — crucial when canopy is sparse (young crops)
# NDMI  (0.30) : canopy moisture; optimal = well-hydrated leaf tissue
# NDWI  (0.15) : open-water / surface moisture; moderate positive = irrigation OK
# NMDI  (0.65) : drought index; LOWER = wetter = better → invert=True
#                at 0.65 soil is adequately moist; above 0.80 = drought stress
# NBR   (0.40) : burn / senescence ratio; healthy vegetation > 0.40
# BSI   (0.00) : bare-soil exposure; ideal = fully covered → invert=True,
#                optimal=0 means 0 bare soil is best

INDEX_LTV_CONFIG = {
    'ndvi': {
        'label':    'NDVI — Vegetation Health',
        'icon':     '🌱',
        'color':    '#16a34a',
        'optimal':  0.70,
        'range_lo': 0.0,   # only positive values are agronomically meaningful
        'range_hi': 1.0,
        'invert':   False,
        'weight':   0.28,
    },
    'evi': {
        'label':    'EVI — Enhanced Vegetation',
        'icon':     '🌿',
        'color':    '#0d9488',
        'optimal':  0.50,
        'range_lo': 0.0,
        'range_hi': 1.0,
        'invert':   False,
        'weight':   0.18,
    },
    'savi': {
        'label':    'SAVI — Soil-Adj Vegetation',
        'icon':     '🌾',
        'color':    '#65a30d',
        'optimal':  0.50,
        'range_lo': 0.0,
        'range_hi': 1.0,
        'invert':   False,
        'weight':   0.14,
    },
    'ndmi': {
        'label':    'NDMI — Canopy Moisture',
        'icon':     '💧',
        'color':    '#0284c7',
        'optimal':  0.30,
        'range_lo': -1.0,  # full [-1, 1] range
        'range_hi':  1.0,
        'invert':   False,
        'weight':   0.18,
    },
    'ndwi': {
        'label':    'NDWI — Water Content',
        'icon':     '🌊',
        'color':    '#0ea5e9',
        'optimal':  0.15,
        'range_lo': -1.0,
        'range_hi':  1.0,
        'invert':   False,
        'weight':   0.10,
    },
    'nmdi': {
        'label':    'NMDI — Drought Index',
        'icon':     '☀️',
        'color':    '#f97316',
        'optimal':  0.65,
        'range_lo':  0.0,
        'range_hi':  1.0,
        'invert':   True,   # lower = wetter soil = better
        'weight':   0.06,
    },
    'nbr': {
        'label':    'NBR — Burn Ratio',
        'icon':     '🔥',
        'color':    '#ef4444',
        'optimal':  0.40,
        'range_lo': -1.0,
        'range_hi':  1.0,
        'invert':   False,
        'weight':   0.04,
    },
    'bsi': {
        'label':    'BSI — Bare Soil Index',
        'icon':     '⛰️',
        'color':    '#92400e',
        'optimal':  0.00,   # 0 bare soil = full canopy cover = best
        'range_lo': -1.0,
        'range_hi':  1.0,
        'invert':   True,   # lower BSI = more vegetation = better
        'weight':   0.02,
    },
}

# Sanity check: weights must sum to 1.0
assert abs(sum(c['weight'] for c in INDEX_LTV_CONFIG.values()) - 1.0) < 1e-9, \
    'INDEX_LTV_CONFIG weights must sum to 1.0'


def _compute_index_factor(idx_name: str, value) -> float:
    """
    Convert a satellite index value into a crop-productivity factor in [0.3, 1.0].

    Logic
    -----
    For non-inverted indices (higher value = better):
        - Shift value to [0, range_hi - range_lo] so negatives don't penalise
        - Divide by shifted optimal to get a ratio; clamp to [0.3, 1.0]

    For inverted indices (lower value = better, e.g. NMDI drought, BSI bare soil):
        - Reflect around optimal: factor ∝ optimal / value
        - At value == optimal, factor = 1.0; above optimal, factor < 1.0

    A floor of 0.3 avoids zero-valued crop estimates that would cause
    division-by-zero in LTV ratio calculations.
    """
    if value is None:
        return 0.30

    cfg      = INDEX_LTV_CONFIG.get(idx_name)
    if not cfg:
        return 0.30

    optimal  = cfg['optimal']
    range_lo = cfg['range_lo']
    invert   = cfg['invert']

    if invert:
        # NMDI: optimal = 0.65; at value=0.65 → factor=1.0
        #        at value=0.80 (drought) → factor=0.65/0.80=0.81 → clamped
        # BSI:  optimal = 0.0; any positive value reduces factor
        if optimal == 0.0:
            # BSI special case: factor = 1 - |value| (max cover = factor 1)
            raw = 1.0 - abs(value)
        else:
            raw = optimal / max(abs(value), 1e-4)
    else:
        # Shift to non-negative space then normalise to optimal
        shifted_val     = value - range_lo          # e.g. NDMI: -0.5 → 0.5
        shifted_optimal = optimal - range_lo        # e.g. NDMI: 0.30 - (-1) = 1.30
        if shifted_optimal <= 0:
            raw = 0.30
        else:
            raw = shifted_val / shifted_optimal

    return round(max(0.30, min(1.0, raw)), 4)


def _regression_calibrate(ndvi_values: list, base_yields: list,
                           hist_yield_1: float | None,
                           hist_yield_2: float | None,
                           current_ndvi: float | None) -> dict:
    """
    Fit a linear regression NDVI → Yield, optionally anchored by 1 or 2
    historical ground-truth yields supplied by the analyst.

    If hist_yield_1 / hist_yield_2 are provided they are paired with the
    annual-mean NDVI of years N-2 and N-1 respectively, so the line is
    pulled toward real field observations.

    Returns:
      slope, intercept, predicted_yield (for current_ndvi),
      calibrated (bool), r2, ndvi_points, yield_points
    """
    import numpy as np

    xs = list(ndvi_values)   # NDVI history (quarterly means)
    ys = list(base_yields)   # model-estimated yields (same length)

    # --- anchor with analyst ground-truth yields if provided ----------------
    # We pair HY1 with the annual mean NDVI of 4 quarters-ago year,
    # HY2 with the most recent full-year mean NDVI.
    calibrated = False
    n = len(xs)

    if hist_yield_1 is not None and n >= 8:
        # year N-2: quarters [-8..-5]
        anchor_ndvi_1 = float(np.mean(xs[max(0, n-8):max(1, n-4)]))
        xs.append(anchor_ndvi_1)
        ys.append(hist_yield_1)
        calibrated = True

    if hist_yield_2 is not None and n >= 4:
        # year N-1: quarters [-4..-1]
        anchor_ndvi_2 = float(np.mean(xs[max(0, n-4):n]))
        xs.append(anchor_ndvi_2)
        ys.append(hist_yield_2)
        calibrated = True

    xs_arr = np.array(xs, dtype=float)
    ys_arr = np.array(ys, dtype=float)

    # least-squares fit
    if len(xs_arr) >= 2 and xs_arr.std() > 1e-6:
        coeffs   = np.polyfit(xs_arr, ys_arr, 1)
        slope    = float(coeffs[0])
        intercept = float(coeffs[1])
        # R²
        y_hat = slope * xs_arr + intercept
        ss_res = float(np.sum((ys_arr - y_hat) ** 2))
        ss_tot = float(np.sum((ys_arr - ys_arr.mean()) ** 2))
        r2 = round(1 - ss_res / ss_tot, 4) if ss_tot > 0 else 1.0
    else:
        slope    = 0.0
        intercept = float(np.mean(ys_arr)) if len(ys_arr) else 0.0
        r2       = 0.0

    predicted = None
    if current_ndvi is not None:
        predicted = round(max(0.0, slope * current_ndvi + intercept), 3)

    return {
        'slope':           round(slope, 4),
        'intercept':       round(intercept, 4),
        'r2':              r2,
        'predicted_yield': predicted,
        'calibrated':      calibrated,
        'ndvi_points':     [round(x, 4) for x in list(ndvi_values)],
        'yield_points':    [round(y, 4) for y in list(base_yields)],
    }


def compute_ltv_multi(history_out: list, area_ha: float,
                      yield_t_per_ha: float = 1.5,
                      price_per_t: float = 500.0,
                      loan_amount: float = None,
                      hist_yield_1: float = None,
                      hist_yield_2: float = None) -> dict | None:
    """
    Compute LTV for *every* satellite index in INDEX_LTV_CONFIG.

    For each index:
      - Pulls the most recent non-null value from history_out
      - Derives a productivity factor via _compute_index_factor
      - Computes adjusted yield, estimated crop value, LTV ratio, insurance premium

    Also computes a weighted composite across all indices.

    hist_yield_1 / hist_yield_2 (optional t/ha): analyst-supplied real yields
    for years N-2 and N-1. When provided, they calibrate the NDVI→Yield
    linear regression to local conditions.

    Returns a dict with:
      indices    : {idx_name: {label, icon, color, index_value, factor, ...}}
      composite  : {factor, adjusted_yield_t_ha, crop_value_usd, ltv_ratio_pct, insurance_pct}
      regression : {ndvi: {slope, intercept, r2, predicted_yield, ...}, evi: {...}, ...}
      area_ha, yield_t_per_ha, price_per_t, loan_amount_usd
      + backward-compat top-level keys (ndvi_factor, adjusted_yield_t_ha, ...)

    Returns None if area_ha <= 0 or no history available.
    """
    if not history_out or area_ha <= 0:
        return None

    per_index      = {}
    composite_factor_sum   = 0.0
    composite_weight_sum   = 0.0

    for idx_name, cfg in INDEX_LTV_CONFIG.items():
        # ── Most recent non-null value ────────────────────────────────────────
        recent_val = None
        for row in reversed(history_out):
            v = row.get(idx_name)
            val = v.get('value') if isinstance(v, dict) else v
            if val is not None:
                recent_val = val
                break

        factor         = _compute_index_factor(idx_name, recent_val)
        adj_yield      = round(yield_t_per_ha * factor, 3)
        crop_value     = round(area_ha * adj_yield * price_per_t, 2)

        ltv_ratio = (
            round(loan_amount / crop_value * 100, 1)
            if loan_amount and crop_value > 0
            else None
        )

        # Insurance premium: base 3 % + risk premium derived from factor & LTV
        base       = 3.0
        # Vegetation / moisture deficit → extra premium
        health_risk = max(0.0, (0.6 - factor) * 5.0)
        # Leverage risk: each 1 % above 60 % LTV adds 0.05 %
        ltv_risk    = max(0.0, ((ltv_ratio or 60.0) - 60.0) * 0.05) if ltv_ratio else 0.0
        insurance   = round(base + health_risk + ltv_risk, 2)

        per_index[idx_name] = {
            'label':                    cfg['label'],
            'icon':                     cfg['icon'],
            'color':                    cfg['color'],
            'index_value':              recent_val,
            'factor':                   factor,
            'adjusted_yield_t_ha':      adj_yield,
            'estimated_crop_value_usd': crop_value,
            'ltv_ratio_pct':            ltv_ratio,
            'insurance_premium_pct':    insurance,
            'weight':                   cfg['weight'],
        }

        composite_factor_sum  += factor * cfg['weight']
        composite_weight_sum  += cfg['weight']

    # ── Weighted composite ────────────────────────────────────────────────────
    comp_factor = round(composite_factor_sum / max(composite_weight_sum, 1e-9), 4)
    comp_yield  = round(yield_t_per_ha * comp_factor, 3)
    comp_crop   = round(area_ha * comp_yield * price_per_t, 2)
    comp_ltv    = (
        round(loan_amount / comp_crop * 100, 1)
        if loan_amount and comp_crop > 0
        else None
    )
    comp_health_risk = max(0.0, (0.6 - comp_factor) * 5.0)
    comp_ltv_risk    = max(0.0, ((comp_ltv or 60.0) - 60.0) * 0.05) if comp_ltv else 0.0
    comp_insurance   = round(3.0 + comp_health_risk + comp_ltv_risk, 2)

    # ── Per-index regression (dynamic — all indices, not just NDVI) ──────────
    regressions = {}
    for idx_name in INDEX_LTV_CONFIG:
        idx_history  = []
        yield_hist   = []
        for row in history_out:
            v = row.get(idx_name)
            val = v.get('value') if isinstance(v, dict) else v
            if val is not None:
                idx_history.append(val)
                f = _compute_index_factor(idx_name, val)
                yield_hist.append(round(yield_t_per_ha * f, 3))

        current_val = None
        for row in reversed(history_out):
            v = row.get(idx_name)
            val = v.get('value') if isinstance(v, dict) else v
            if val is not None:
                current_val = val
                break

        regressions[idx_name] = _regression_calibrate(
            idx_history, yield_hist,
            hist_yield_1, hist_yield_2,
            current_val,
        )

    # ── Build return dict (backward-compat top-level keys from NDVI) ──────────
    ndvi_entry = per_index.get('ndvi', {})

    return {
        # ── New structure ──────────────────────────────────────────────────────
        'indices':   per_index,
        'composite': {
            'factor':                   comp_factor,
            'adjusted_yield_t_ha':      comp_yield,
            'estimated_crop_value_usd': comp_crop,
            'ltv_ratio_pct':            comp_ltv,
            'insurance_premium_pct':    comp_insurance,
        },
        # ── Regression (per-index) ────────────────────────────────────────────
        'regression':       regressions,
        # ── Metadata ──────────────────────────────────────────────────────────
        'area_ha':          round(area_ha, 2),
        'yield_t_per_ha':   yield_t_per_ha,
        'price_per_t':      price_per_t,
        'loan_amount_usd':  loan_amount,
        'hist_yield_1':     hist_yield_1,
        'hist_yield_2':     hist_yield_2,
        # ── Backward-compatible flat keys (previously from compute_ltv) ───────
        'ndvi_factor':                  ndvi_entry.get('factor'),
        'adjusted_yield_t_ha':          ndvi_entry.get('adjusted_yield_t_ha'),
        'estimated_crop_value_usd':     ndvi_entry.get('estimated_crop_value_usd'),
        'ltv_ratio_pct':                ndvi_entry.get('ltv_ratio_pct'),
        'insurance_premium_pct':        ndvi_entry.get('insurance_premium_pct'),
    }


# Keep the old single-index function for any external callers, but delegate
# to the multi-index logic for consistency.
def compute_ltv(ndvi_mean, area_ha, yield_t_per_ha=1.5,
                price_per_t=500, loan_amount=None):
    """
    Legacy single-index LTV (NDVI only).
    Prefer compute_ltv_multi for the full multi-index breakdown.
    """
    synthetic_history = [{'ndvi': ndvi_mean}]
    result = compute_ltv_multi(
        synthetic_history, area_ha,
        yield_t_per_ha=yield_t_per_ha,
        price_per_t=price_per_t,
        loan_amount=loan_amount,
    )
    if result is None:
        return None
    # Return the old flat dict shape
    return {
        'area_ha':                  result['area_ha'],
        'ndvi_factor':              result['ndvi_factor'],
        'adjusted_yield_t_ha':      result['adjusted_yield_t_ha'],
        'estimated_crop_value_usd': result['estimated_crop_value_usd'],
        'loan_amount_usd':          loan_amount,
        'ltv_ratio_pct':            result['ltv_ratio_pct'],
        'insurance_premium_pct':    result['insurance_premium_pct'],
    }


# ── Forecast ─────────────────────────────────────────────────────────────────

def _extract_rows(data, index_name):
    rows = []
    for d in data:
        raw = d.get(index_name)
        if raw is None:
            continue
        val = raw.get('value') if isinstance(raw, dict) else raw
        if val is not None:
            rows.append((d['date'], float(val)))
    return rows


def _seasonal_naive_forecast(df, index_name, periods=4):
    import numpy as np
    df = df.copy()
    df['quarter'] = df['ds'].dt.quarter
    q_stats       = df.groupby('quarter')['y'].agg(['mean', 'std'])
    x             = np.arange(len(df))
    slope         = float(np.polyfit(x, df['y'].values, 1)[0])
    last_date     = df['ds'].max()
    result        = []

    for i in range(1, periods + 1):
        future_date = last_date + pd.DateOffset(months=3 * i)
        q           = future_date.quarter
        row         = q_stats.loc[q] if q in q_stats.index else None
        q_mean      = float(row['mean']) if row is not None else df['y'].mean()
        q_std       = float(row['std'])  if row is not None and not pd.isna(row['std']) else df['y'].std()
        if pd.isna(q_std) or q_std < 0.005:
            q_std = max(df['y'].std(), 0.005)

        val = round(max(-1.0, min(1.0, q_mean + slope * i * 0.1)), 4)
        ci  = max(q_std * 1.28, 0.01)
        lo  = round(max(-1.0, min(1.0, val - ci)), 4)
        hi  = round(max(-1.0, min(1.0, val + ci)), 4)

        result.append({
            'date':        future_date.strftime('%Y-%m-%d'),
            'quarter':     f"{future_date.year}-Q{q}",
            'value':       val,
            'lower_80':    lo,
            'upper_80':    hi,
            'tier':        get_tier(index_name, val),
            'is_forecast': True,
        })

    logger.info(f'[SeasonalNaive] {index_name}: {len(result)} quarters → {[r["value"] for r in result]}')
    return result


def _prophet_forecast(data, index_name, periods=4):
    rows = _extract_rows(data, index_name)
    if len(rows) < 8:
        logger.warning(f'[Forecast] {index_name}: only {len(rows)} points (need ≥ 8) — skipping.')
        return []

    df = pd.DataFrame({
        'ds': pd.to_datetime([r[0] for r in rows]),
        'y':  [r[1] for r in rows],
    })

    historical_mean = df['y'].mean()
    historical_std  = max(df['y'].std(), 0.005)
    prophet_result  = []

    try:
        from prophet import Prophet

        y_min  = df['y'].min()
        y_max  = df['y'].max()
        margin = max((y_max - y_min) * 0.5, 0.05)
        cap    = min(y_max + margin,  1.0)
        floor  = max(y_min - margin, -1.0)

        df_p          = df.copy()
        df_p['cap']   = cap
        df_p['floor'] = floor

        model = Prophet(
            growth='logistic',
            yearly_seasonality=2,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='additive',
            changepoint_prior_scale=0.005,
            seasonality_prior_scale=0.5,
            interval_width=0.80,
        )
        model.fit(df_p)

        future          = model.make_future_dataframe(periods=periods, freq='QS')
        future['cap']   = cap
        future['floor'] = floor
        forecast        = model.predict(future)
        pred            = forecast[forecast['ds'] > df['ds'].max()]

        for _, row in pred.iterrows():
            val = float(row['yhat'])
            if abs(val - historical_mean) > 3 * historical_std:
                logger.warning(
                    f'[Prophet] {index_name}: prediction {val:.4f} is '
                    f'{abs(val - historical_mean) / historical_std:.1f}σ from mean '
                    f'{historical_mean:.4f} — falling back to seasonal naive.'
                )
                prophet_result = []
                break
            val = round(max(-1.0, min(1.0, val)), 4)
            lo  = round(max(-1.0, min(1.0, float(row['yhat_lower']))), 4)
            hi  = round(max(-1.0, min(1.0, float(row['yhat_upper']))), 4)
            prophet_result.append({
                'date':        row['ds'].strftime('%Y-%m-%d'),
                'quarter':     row['ds'].strftime('%Y-Q') + str((row['ds'].month - 1) // 3 + 1),
                'value':       val,
                'lower_80':    lo,
                'upper_80':    hi,
                'tier':        get_tier(index_name, val),
                'is_forecast': True,
            })

        if prophet_result:
            logger.info(f'[Prophet] {index_name}: {len(prophet_result)} quarters → {[r["value"] for r in prophet_result]}')
            return prophet_result

    except ImportError:
        logger.warning('[Forecast] Prophet not installed — using seasonal naive.')
    except Exception as e:
        logger.error(f'[Prophet] {index_name} failed: {e}')

    return _seasonal_naive_forecast(df, index_name, periods)


def _is_forecast_empty(forecast_dict):
    if not forecast_dict:
        return True
    return all(len(v) == 0 for v in forecast_dict.values())


def _run_forecast_all(history_data, indices):
    result = {}
    for idx in indices:
        result[idx] = _prophet_forecast(history_data, idx, periods=4)
    return result


# ── LTV / geometry helpers ────────────────────────────────────────────────────

def _compute_area_ha_from_points(points):
    if not points or len(points) < 3:
        return 0.0, None
    try:
        from shapely.geometry import Polygon
        import pyproj
        from shapely.ops import transform as shapely_transform

        coords  = [(p.longitude, p.latitude) for p in points]
        polygon = Polygon(coords)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.is_empty:
            return 0.0, None

        cx   = polygon.centroid.x
        cy   = polygon.centroid.y
        zone = int((cx + 180) / 6) + 1
        hemi = 'north' if cy >= 0 else 'south'
        epsg = 32600 + zone if hemi == 'north' else 32700 + zone

        transformer = pyproj.Transformer.from_crs(
            pyproj.CRS('EPSG:4326'), pyproj.CRS(f'EPSG:{epsg}'), always_xy=True
        )
        projected = shapely_transform(transformer.transform, polygon)
        area_ha   = round(projected.area / 10_000, 4)
        logger.info(f'[Sentinel] GPS area computed: {area_ha} ha ({len(points)} points)')
        return area_ha, 'gps'

    except ImportError:
        logger.warning('[Sentinel] shapely/pyproj not installed.')
        return 0.0, None
    except Exception as e:
        logger.warning(f'[Sentinel] Area calculation failed: {e}')
        return 0.0, None


def _build_geometry(points, geolocation=None):
    if len(points) >= 3:
        coords = [[p.longitude, p.latitude] for p in points]
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        return {'type': 'Polygon', 'coordinates': [coords]}
    if geolocation:
        try:
            lat, lon = [float(x.strip()) for x in geolocation.split(',')]
            d = 0.005
            return {'type': 'Polygon', 'coordinates': [[
                [lon-d, lat-d], [lon+d, lat-d], [lon+d, lat+d],
                [lon-d, lat+d], [lon-d, lat-d],
            ]]}
        except Exception:
            pass
    return None


# ── Main entry point ──────────────────────────────────────────────────────────

def get_sat_index_full(entity_type, entity_id,
                       loan_amount=None, yield_t_per_ha=1.5, price_per_t=500,
                       force_refresh=False,
                       hist_yield_1=None, hist_yield_2=None):
    """
    Main entry point for Sat-Index data.

    LTV is always recomputed from live GPS points (pure arithmetic, no API call)
    using the full multi-index breakdown (compute_ltv_multi).
    """
    from app.models import Farm, Forest, Point, SentinelCache
    from app import db
    import json
    from datetime import timedelta

    indices = ['ndvi', 'ndmi', 'ndwi', 'nmdi', 'evi', 'savi', 'nbr', 'bsi']

    # ── Load entity ───────────────────────────────────────────────────────────
    if entity_type == 'farm':
        entity = Farm.query.filter_by(farm_id=entity_id).first()
        if not entity:
            return None, 'Farm not found'
        points   = Point.query.filter_by(owner_type='farmer', owner_id=str(entity_id)).order_by(Point.id).all()
        geometry = _build_geometry(points, entity.geolocation)
        name     = entity.name
        logger.info(f'[Sentinel] Farm {entity_id}: {len(points)} polygon points')
    else:
        entity = Forest.query.filter_by(id=entity_id).first()
        if not entity:
            return None, 'Forest not found'
        points   = Point.query.filter_by(owner_type='forest', owner_id=str(entity_id)).order_by(Point.id).all()
        geometry = _build_geometry(points)
        name     = entity.name
        logger.info(f'[Sentinel] Forest {entity_id}: {len(points)} polygon points')

    if not geometry:
        return None, 'No geometry available — add polygon points first'

    # ── Check cache ───────────────────────────────────────────────────────────
    cache = SentinelCache.query.filter_by(farm_id=entity_id).first() if entity_type == 'farm' else None

    if cache and not cache.is_stale() and not force_refresh:
        history_out  = cache.get_history()
        forecast_out = cache.get_forecast()

        if _is_forecast_empty(forecast_out) and history_out:
            logger.warning(f'[SentinelCache] Empty forecast for {entity_id} — recomputing.')
            forecast_out = _run_forecast_all(history_out, indices)
            if not _is_forecast_empty(forecast_out):
                try:
                    cache.forecast_json = json.dumps(forecast_out)
                    db.session.commit()
                except Exception as e:
                    logger.error(f'[SentinelCache] Could not save recomputed forecast: {e}')
                    db.session.rollback()

        # LTV: always recomputed from live GPS points using multi-index breakdown
        ltv_data = None
        if entity_type == 'farm':
            area_ha, _ = _compute_area_ha_from_points(points)
            if area_ha > 0:
                ltv_data = compute_ltv_multi(
                    history_out, area_ha,
                    yield_t_per_ha=yield_t_per_ha,
                    price_per_t=price_per_t,
                    loan_amount=loan_amount,
                    hist_yield_1=hist_yield_1,
                    hist_yield_2=hist_yield_2,
                )
            else:
                ltv_data = cache.get_ltv()

        return {
            'entity_id':        entity_id,
            'entity_type':      entity_type,
            'name':             name,
            'period':           {'from': cache.period_from, 'to': cache.period_to},
            'history':          history_out,
            'forecast':         forecast_out,
            'ltv':              ltv_data,
            'tiers_meta':       TIERS,
            'from_cache':       True,
            'cache_updated_at': cache.updated_at.isoformat() if cache.updated_at else None,
            'out_of_bounds':    [],
        }, None

    # ── Full Sentinel API call ────────────────────────────────────────────────
    now       = datetime.utcnow()
    date_to   = now.strftime('%Y-%m-%dT23:59:59Z')
    date_from = (now - relativedelta(years=5)).strftime('%Y-%m-%dT00:00:00Z')

    try:
        raw                       = _call_statistics(geometry, date_from, date_to)
        historical, out_of_bounds = _parse_response(raw)
    except Exception as e:
        logger.error(f'[Sentinel] API call failed for {entity_id}: {e}')
        if cache:
            history_out  = cache.get_history()
            forecast_out = cache.get_forecast()
            if _is_forecast_empty(forecast_out) and history_out:
                forecast_out = _run_forecast_all(history_out, indices)
            ltv_data = None
            if entity_type == 'farm':
                area_ha, _ = _compute_area_ha_from_points(points)
                if area_ha > 0:
                    ltv_data = compute_ltv_multi(
                        history_out, area_ha,
                        yield_t_per_ha=yield_t_per_ha,
                        price_per_t=price_per_t,
                        loan_amount=loan_amount,
                        hist_yield_1=hist_yield_1,
                        hist_yield_2=hist_yield_2,
                    )
                else:
                    ltv_data = cache.get_ltv()
            return {
                'entity_id':        entity_id,
                'entity_type':      entity_type,
                'name':             name,
                'period':           {'from': cache.period_from, 'to': cache.period_to},
                'history':          history_out,
                'forecast':         forecast_out,
                'ltv':              ltv_data,
                'tiers_meta':       TIERS,
                'from_cache':       True,
                'cache_stale':      True,
                'cache_updated_at': cache.updated_at.isoformat() if cache.updated_at else None,
                'out_of_bounds':    [],
            }, None
        return None, f'Sentinel API error: {e}'

    if not historical:
        return None, 'No satellite data for this location'

    # ── Enrich history ────────────────────────────────────────────────────────
    history_out = []
    for row in historical:
        out = {'date': row['date']}
        for idx in indices:
            val     = row.get(idx)
            raw_val = row.get(f'{idx}_raw')
            out[idx] = {
                'value': val,
                'raw':   raw_val,
                'oob':   raw_val is not None and (raw_val < -1.0 or raw_val > 1.0),
                'tier':  get_tier(idx, val),
            }
        history_out.append(out)

    # ── Forecast ─────────────────────────────────────────────────────────────
    forecast_out = _run_forecast_all(historical, indices)

    # ── Multi-index LTV ───────────────────────────────────────────────────────
    ltv_data = None
    if entity_type == 'farm':
        area_ha, _ = _compute_area_ha_from_points(points)
        if area_ha > 0:
            ltv_data = compute_ltv_multi(
                history_out, area_ha,
                yield_t_per_ha=yield_t_per_ha,
                price_per_t=price_per_t,
                loan_amount=loan_amount,
                hist_yield_1=hist_yield_1,
                hist_yield_2=hist_yield_2,
            )

    # ── Save to cache ─────────────────────────────────────────────────────────
    if entity_type == 'farm':
        try:
            if not cache:
                cache = SentinelCache(farm_id=entity_id)
                db.session.add(cache)
            cache.history_json  = json.dumps(history_out)
            cache.forecast_json = json.dumps(forecast_out)
            cache.ltv_json      = json.dumps(ltv_data) if ltv_data else None
            cache.period_from   = date_from[:10]
            cache.period_to     = date_to[:10]
            cache.stale_after   = now + timedelta(days=90)
            db.session.commit()
        except Exception as e:
            logger.error(f'[SentinelCache] Save error: {e}')
            db.session.rollback()

    return {
        'entity_id':     entity_id,
        'entity_type':   entity_type,
        'name':          name,
        'period':        {'from': date_from[:10], 'to': date_to[:10]},
        'history':       history_out,
        'forecast':      forecast_out,
        'ltv':           ltv_data,
        'tiers_meta':    TIERS,
        'from_cache':    False,
        'out_of_bounds': out_of_bounds,
    }, None
    
# ── Evalscripts de classification (image colorée avec seuils) ────────────────

# ── Evalscript générique de classification (tous indices, une seule bande active) ──
# On calcule tous les indices en JS et on ne colorie que celui demandé via un paramètre.

GENERIC_CLASSIFICATION_EVALSCRIPT = """//VERSION=3
function setup() {
  return {
    input: ['B02','B03','B04','B05','B08','B11','B12','dataMask'],
    output: { bands: 4 }
  };
}

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

function evaluatePixel(s) {
  if (s.dataMask === 0) return [0, 0, 0, 0];

  var indices = {};
  indices.ndvi = (s.B08 - s.B04) / (s.B08 + s.B04 + 1e-10);
  indices.ndmi = (s.B08 - s.B11) / (s.B08 + s.B11 + 1e-10);
  indices.ndwi = (s.B03 - s.B08) / (s.B03 + s.B08 + 1e-10);
  var nmdiD = s.B08 + (s.B11 - s.B12);
  indices.nmdi = Math.abs(nmdiD) > 1e-6 ? (s.B08 - (s.B11 - s.B12)) / nmdiD : 0;
  var eviD = s.B08 + 6*s.B04 - 7.5*s.B02 + 1;
  indices.evi = Math.abs(eviD) > 1e-6 ? 2.5*(s.B08 - s.B04) / eviD : 0;
  indices.savi = 1.5*(s.B08 - s.B04) / (s.B08 + s.B04 + 0.5 + 1e-10);
  indices.nbr = (s.B08 - s.B12) / (s.B08 + s.B12 + 1e-10);
  var bsiD = (s.B11 + s.B04) + (s.B08 + s.B02);
  indices.bsi = Math.abs(bsiD) > 1e-6 ? ((s.B11 + s.B04) - (s.B08 + s.B02)) / bsiD : 0;
  indices.ndre = (s.B08 - s.B05) / (s.B08 + s.B05 + 1e-10);

  var TARGET = '__INDEX_PLACEHOLDER__';
  var THRESHOLDS = __THRESHOLDS_PLACEHOLDER__;  // [{max, r, g, b}, ...] injecté en Python

  var val = clamp(indices[TARGET], -1, 1);

  for (var i = 0; i < THRESHOLDS.length; i++) {
    if (val <= THRESHOLDS[i].max) {
      return [THRESHOLDS[i].r, THRESHOLDS[i].g, THRESHOLDS[i].b, 1];
    }
  }
  var last = THRESHOLDS[THRESHOLDS.length - 1];
  return [last.r, last.g, last.b, 1];
}
"""

# Seuils + labels + couleurs, réutilisés pour calculer les surfaces et la légende
# Thresholds + labels + colors for the 9 satellite indices
CLASSIFICATION_THRESHOLDS = {
    'ndvi': [
        {'max': 0.1, 'label': 'Bare Soil / Newly Planted',      'color': '#dc1414'},
        {'max': 0.2, 'label': 'Very Sparse Vegetation',         'color': '#f28c1a'},
        {'max': 0.3, 'label': 'Sparse Vegetation',              'color': '#f2e633'},
        {'max': 0.5, 'label': 'Moderate Vegetation',            'color': '#8cbf40'},
        {'max': 1.0, 'label': 'Dense Vegetation',               'color': '#0d7319'},
    ],
    'evi': [
        {'max': 0.0, 'label': 'Bare Soil / Water',              'color': '#dc1414'},
        {'max': 0.2, 'label': 'Dry / Stressed Vegetation',      'color': '#f28c1a'},
        {'max': 0.4, 'label': 'Moderate Vegetation',            'color': '#f2e633'},
        {'max': 0.6, 'label': 'Healthy Vegetation',             'color': '#8cbf40'},
        {'max': 1.0, 'label': 'Very Healthy Vegetation',        'color': '#0d7319'},
    ],
    'savi': [
        {'max': 0.1, 'label': 'Non-Vegetated Area',             'color': '#dc1414'},
        {'max': 0.2, 'label': 'Very Sparse Vegetation',         'color': '#f28c1a'},
        {'max': 0.3, 'label': 'Sparse Vegetation',              'color': '#f2e633'},
        {'max': 0.5, 'label': 'Moderate Vegetation',            'color': '#8cbf40'},
        {'max': 1.0, 'label': 'Dense Vegetation',               'color': '#0d7319'},
    ],
    'ndmi': [
        {'max': -0.2, 'label': 'Very Dry / Non-Vegetated',      'color': '#dc1414'},
        {'max':  0.0, 'label': 'Low Moisture',                  'color': '#f28c1a'},
        {'max':  0.2, 'label': 'Moderate Moisture',             'color': '#f2e633'},
        {'max':  0.4, 'label': 'High Moisture',                 'color': '#8cbf40'},
        {'max':  1.0, 'label': 'Saturated',                     'color': '#0d7319'},
    ],
    'ndwi': [
        {'max': -0.3, 'label': 'Severe Water Stress',           'color': '#dc1414'},
        {'max':  0.0, 'label': 'Moderate Drought',              'color': '#f28c1a'},
        {'max':  0.15, 'label': 'Normal Moisture',              'color': '#f2e633'},
        {'max':  0.3, 'label': 'Wet Area',                      'color': '#8cbf40'},
        {'max':  1.0, 'label': 'Open Water',                    'color': '#0d7319'},
    ],
    'nmdi': [
        {'max': 0.6,  'label': 'Moist Soil',                    'color': '#0d7319'},
        {'max': 0.65, 'label': 'Adequate Moisture',             'color': '#8cbf40'},
        {'max': 0.7,  'label': 'Moderate Drought',              'color': '#f2e633'},
        {'max': 0.8,  'label': 'Severe Drought',                'color': '#f28c1a'},
        {'max': 1.0,  'label': 'Extreme Drought',               'color': '#dc1414'},
    ],
    'nbr': [
        {'max': -0.1, 'label': 'Burned Area',                   'color': '#dc1414'},
        {'max':  0.1, 'label': 'Bare / Dry Soil',               'color': '#f28c1a'},
        {'max':  0.3, 'label': 'Moderate Vegetation',           'color': '#f2e633'},
        {'max':  0.6, 'label': 'Healthy Vegetation',            'color': '#8cbf40'},
        {'max':  1.0, 'label': 'Very Healthy Vegetation',       'color': '#0d7319'},
    ],
    'bsi': [
        {'max': -0.3, 'label': 'Full Vegetation Cover',         'color': '#0d7319'},
        {'max':  0.0, 'label': 'Healthy Vegetation',            'color': '#8cbf40'},
        {'max':  0.1, 'label': 'Sparse Vegetation',             'color': '#f2e633'},
        {'max':  0.3, 'label': 'Partially Exposed Soil',        'color': '#f28c1a'},
        {'max':  1.0, 'label': 'Bare Soil',                     'color': '#dc1414'},
    ],
    'ndre': [
        {'max': 0.1, 'label': 'No Vegetation',                  'color': '#dc1414'},
        {'max': 0.2, 'label': 'Low Vegetation',                 'color': '#f28c1a'},
        {'max': 0.3, 'label': 'Moderate Vegetation',            'color': '#f2e633'},
        {'max': 0.4, 'label': 'High Vegetation',                'color': '#8cbf40'},
        {'max': 1.0, 'label': 'Very High Vegetation',           'color': '#0d7319'},
    ],
}

# For backward compatibility, we keep the name CLASSIFICATION_EVALSCRIPTS,
# but as a function that dynamically generates the evalscript for any index.
def _hex_to_rgb01(hexcolor):
    h = hexcolor.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


def _build_classification_evalscript(index_name):
    """Generate the JS evalscript for a given index by injecting its thresholds and colors."""
    thresholds = CLASSIFICATION_THRESHOLDS[index_name]
    js_thresholds = '[' + ','.join(
        '{{max:{},r:{:.4f},g:{:.4f},b:{:.4f}}}'.format(
            t['max'], *_hex_to_rgb01(t['color'])
        ) for t in thresholds
    ) + ']'

    return (
        GENERIC_CLASSIFICATION_EVALSCRIPT
        .replace('__INDEX_PLACEHOLDER__', index_name)
        .replace('__THRESHOLDS_PLACEHOLDER__', js_thresholds)
    )

def _call_process_image(geometry, date_from, date_to, index_name, width=1024, height=1024):
    """
    Appelle l'API Process de Copernicus pour obtenir une image PNG classifiée.
    """
    if index_name not in CLASSIFICATION_THRESHOLDS:
        raise ValueError(f'Index "{index_name}" non supporté pour la classification')

    token = _get_token()
    evalscript = _build_classification_evalscript(index_name)

    payload = {
        'input': {
            'bounds': {
                'geometry': geometry,
                'properties': {'crs': 'http://www.opengis.net/def/crs/EPSG/0/4326'}
            },
            'data': [{
                'type': 'sentinel-2-l2a',
                'dataFilter': {
                    'timeRange': {'from': date_from, 'to': date_to},
                    'maxCloudCoverage': 30,
                    'mosaickingOrder': 'leastCC',
                }
            }],
        },
        'output': {
            'width': width,
            'height': height,
            'responses': [{
                'identifier': 'default',
                'format': {'type': 'image/png'}
            }]
        },
        'evalscript': evalscript,
    }

    resp = requests.post(
        'https://sh.dataspace.copernicus.eu/api/v1/process',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.content

def _compute_class_areas(geometry, date_from, date_to, index_name, points=None, width=1024, height=1024):
    from PIL import Image
    import io
    import numpy as np

    png_bytes = _call_process_image(geometry, date_from, date_to, index_name, width, height)
    img = Image.open(io.BytesIO(png_bytes)).convert('RGBA')
    arr = np.array(img)

    thresholds = CLASSIFICATION_THRESHOLDS[index_name]

    # Surface réelle projetée (ha → km²)
    if points:
        area_ha, _ = _compute_area_ha_from_points(points)
        poly_area_km2 = area_ha / 100.0
    else:
        poly_area_km2 = 0.0

    valid_mask = arr[:, :, 3] > 0
    total_valid_px = valid_mask.sum()

    results = []
    for t in thresholds:
        color_rgb = tuple(int(t['color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        match = (
            (np.abs(arr[:, :, 0].astype(int) - color_rgb[0]) < 10) &
            (np.abs(arr[:, :, 1].astype(int) - color_rgb[1]) < 10) &
            (np.abs(arr[:, :, 2].astype(int) - color_rgb[2]) < 10) &
            valid_mask
        )
        px_count = int(match.sum())
        pct = px_count / total_valid_px if total_valid_px > 0 else 0
        results.append({
            'label':    t['label'],
            'color':    t['color'],
            'area_km2': round(pct * poly_area_km2, 4),
            'pct':      round(pct * 100, 2),
        })

    return results, png_bytes