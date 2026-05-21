"""
sentinel_utils.py — Sentinel-2 + Prophet ML Forecast

Changes in this version:
  - _parse_response returns (data, out_of_bounds_log) tuple
    · stores raw value alongside clamped value for every index
    · logs and records every value that exceeded [-1, 1] before clamping
  - get_sat_index_full — cache branch:
    · LTV is always recomputed from live GPS points (pure math, no API call)
    · no longer guarded by "if loan_amount or yield != default" condition
    · out_of_bounds: [] included in all return paths for API consistency
  - get_sat_index_full — fresh data branch:
    · history_out includes 'raw' and 'oob' fields per index
    · out_of_bounds list returned to frontend
  - All stale-cache fallback paths also include out_of_bounds: []
"""

import os, time, warnings, logging
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

SENTINEL_CLIENT_ID     = os.environ.get('SENTINEL_CLIENT_ID',     '0bfcba08-1240-451e-bf8f-93aa71eff6c1')
SENTINEL_CLIENT_SECRET = os.environ.get('SENTINEL_CLIENT_SECRET', '2iJGb9PNYtCABXZOXHhWAxICOmTs4D9X')
TOKEN_URL = 'https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token'
STATS_URL = 'https://services.sentinel-hub.com/api/v1/statistics'

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

    For each index and each time interval:
      - Stores the raw float value from the API
      - Detects values outside [-1, 1] (out-of-bounds) BEFORE clamping
      - Logs and records every OOB occurrence in out_of_bounds_log
      - Clamps the stored value to [-1, 1]

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
                    row[f'{idx}_raw'] = round(raw_val, 4)  # raw value always preserved

            except Exception:
                row[idx]          = None
                row[f'{idx}_raw'] = None

        result.append(row)

    return result, out_of_bounds_log


# ── Tiers ────────────────────────────────────────────────────────────────────
TIERS = {
    # NDVI — Normalized Difference Vegetation Index [-1, 1]
    'ndvi': [
        {'max': -0.10, 'label': 'Water / Ice',          'color': '#0284c7', 'bg': '#eff6ff'},
        {'max':  0.10, 'label': 'Barren Land',           'color': '#92400e', 'bg': '#fef3c7'},
        {'max':  0.30, 'label': 'Sparse / Stressed',     'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  0.60, 'label': 'Moderate Vegetation',   'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  1.00, 'label': 'Dense / Healthy',       'color': '#15803d', 'bg': '#dcfce7'},
    ],
    # EVI — Enhanced Vegetation Index [-1, 1]
    'evi': [
        {'max':  0.00, 'label': 'Water / Barren',        'color': '#0284c7', 'bg': '#eff6ff'},
        {'max':  0.20, 'label': 'Dry / Stressed',        'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  1.00, 'label': 'Healthy Vegetation',    'color': '#15803d', 'bg': '#dcfce7'},
    ],
    # SAVI — Soil Adjusted Vegetation Index [-1, 1]
    'savi': [
        {'max':  0.10, 'label': 'Non-Vegetated',         'color': '#92400e', 'bg': '#fef3c7'},
        {'max':  0.30, 'label': 'Sparse / Stressed',     'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  1.00, 'label': 'Dense / Healthy',       'color': '#15803d', 'bg': '#dcfce7'},
    ],
    # NDMI — Normalized Difference Moisture Index [-1, 1]
    'ndmi': [
        {'max': -0.60, 'label': 'Bare Soil / Severe Drought', 'color': '#7f1d1d', 'bg': '#fef2f2'},
        {'max': -0.20, 'label': 'Dry / Sparse Canopy',        'color': '#dc2626', 'bg': '#fef2f2'},
        {'max':  0.00, 'label': 'Water Stress',                'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  0.20, 'label': 'Initial Water Stress',        'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  0.40, 'label': 'Low Water Stress',            'color': '#16a34a', 'bg': '#f0fdf4'},
        {'max':  1.00, 'label': 'High Moisture',               'color': '#0284c7', 'bg': '#eff6ff'},
    ],
    # NDWI — Normalized Difference Water Index [-1, 1]
    'ndwi': [
        {'max': -0.30, 'label': 'High Water Stress',     'color': '#dc2626', 'bg': '#fef2f2'},
        {'max':  0.00, 'label': 'Moderate Drought',      'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  0.30, 'label': 'Shallow / Wetland',     'color': '#16a34a', 'bg': '#f0fdf4'},
        {'max':  1.00, 'label': 'Clear Water',           'color': '#0284c7', 'bg': '#eff6ff'},
    ],
    # NMDI — Normalized Multi-band Drought Index [-1, 1]
    'nmdi': [
        {'max':  0.60, 'label': 'Wet Soil',              'color': '#0284c7', 'bg': '#eff6ff'},
        {'max':  0.70, 'label': 'Moderate Drought',      'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  1.00, 'label': 'Extremely Dry',         'color': '#dc2626', 'bg': '#fef2f2'},
    ],
    # NBR — Normalized Burn Ratio [-1, 1]
    'nbr': [
        {'max': -0.10, 'label': 'Burned Area',           'color': '#7f1d1d', 'bg': '#fef2f2'},
        {'max':  0.10, 'label': 'Bare / Dry Soil',       'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  1.00, 'label': 'Healthy Vegetation',    'color': '#15803d', 'bg': '#dcfce7'},
    ],
    # BSI — Bare Soil Index [-1, 1]
    'bsi': [
        {'max':  0.00, 'label': 'Good Vegetation',       'color': '#15803d', 'bg': '#dcfce7'},
        {'max':  0.10, 'label': 'Sparse / Mixed',        'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  1.00, 'label': 'Bare Soil',             'color': '#92400e', 'bg': '#fef3c7'},
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


# ── Forecast ─────────────────────────────────────────────────────────────────

def _extract_rows(data, index_name):
    """Extract (date_str, float_value) pairs from raw or enriched history."""
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
    """
    Seasonal naive forecast.
    Predicts each future quarter as the historical average of that same
    quarter-of-year, blended with a small linear trend (10% weight).
    Confidence intervals come from per-quarter standard deviation.
    Always stays within the historical data range.
    """
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
        ci  = max(q_std * 1.28, 0.01)  # 80% CI  (z = 1.28)
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
    """
    Two-stage forecast:
      Stage 1 — Prophet with data-driven logistic cap/floor.
      Stage 2 — Seasonal naive fallback (Prophet not installed, error, or wild prediction).
    """
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


# ── LTV ──────────────────────────────────────────────────────────────────────

def _compute_area_ha_from_points(points):
    """
    Compute farm area in hectares from GPS polygon points.
    Returns (area_ha, 'gps') or (0.0, None).
    """
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
        logger.warning('[Sentinel] shapely/pyproj not installed. Run: pip install shapely pyproj')
        return 0.0, None
    except Exception as e:
        logger.warning(f'[Sentinel] Area calculation failed: {e}')
        return 0.0, None


def compute_ltv(ndvi_mean, area_ha, yield_t_per_ha=1.5,
                price_per_t=500, loan_amount=None):
    ndvi_factor    = max(0.3, min(1.0, ndvi_mean / 0.7))
    adjusted_yield = yield_t_per_ha * ndvi_factor
    crop_value     = round(area_ha * adjusted_yield * price_per_t, 2)
    ltv_ratio      = round(loan_amount / crop_value * 100, 1) if loan_amount and crop_value > 0 else None

    base          = 3.0
    n_risk        = max(0, (0.5 - ndvi_mean) * 10)
    l_risk        = max(0, ((ltv_ratio or 60) - 60) * 0.05)
    insurance_pct = round(base + n_risk + l_risk, 2)

    return {
        'area_ha':                  round(area_ha, 2),
        'ndvi_factor':              round(ndvi_factor, 3),
        'adjusted_yield_t_ha':      round(adjusted_yield, 3),
        'estimated_crop_value_usd': crop_value,
        'loan_amount_usd':          loan_amount,
        'ltv_ratio_pct':            ltv_ratio,
        'insurance_premium_pct':    insurance_pct,
    }


# ── Geometry ─────────────────────────────────────────────────────────────────

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
                       force_refresh=False):
    """
    Main entry point for Sat-Index data.

    Flow:
      1. Load entity + GPS points from DB.
      2. Check SentinelCache:
         a. Valid cache → serve history + recomputed forecast (if empty) + fresh LTV.
         b. Stale / missing → call Sentinel Statistics API → enrich → forecast → LTV → save.
      3. All return paths include out_of_bounds list (empty [] for cache paths).

    LTV is always recomputed from live GPS points (pure arithmetic, no API call),
    so area_ha, crop_value, and insurance_pct are always up to date even from cache.
    ltv_ratio_pct requires loan_amount — it is None when no loan is provided.
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
        logger.info(f'[Sentinel] Farm {entity_id}: {len(points)} polygon points (pk={entity.id})')
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

        # Cache poison fix: recompute forecast if empty (Prophet was missing when cached)
        if _is_forecast_empty(forecast_out) and history_out:
            logger.warning(
                f'[SentinelCache] Empty forecast for {entity_id} — recomputing from '
                f'{len(history_out)} cached history points (no API call).'
            )
            forecast_out = _run_forecast_all(history_out, indices)
            if not _is_forecast_empty(forecast_out):
                try:
                    cache.forecast_json = json.dumps(forecast_out)
                    db.session.commit()
                    logger.info(f'[SentinelCache] Recomputed forecast saved for {entity_id}.')
                except Exception as e:
                    logger.error(f'[SentinelCache] Could not save recomputed forecast: {e}')
                    db.session.rollback()

        # LTV: always recomputed from live GPS points (cheap — no API call)
        ltv_data = None
        if entity_type == 'farm':
            area_ha, _ = _compute_area_ha_from_points(points)
            if area_ha > 0:
                recent_ndvi = next(
                    (r.get('ndvi', {}).get('value') if isinstance(r.get('ndvi'), dict)
                     else r.get('ndvi')
                     for r in reversed(history_out) if r.get('ndvi') is not None),
                    0.4,
                )
                ltv_data = compute_ltv(recent_ndvi, area_ha, yield_t_per_ha, price_per_t, loan_amount)
            else:
                # No GPS polygon → fall back to cached LTV (may be None)
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
            'out_of_bounds':    [],  # No new Sentinel data → no new OOB events
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
        # Serve stale cache rather than an empty error response
        if cache:
            history_out  = cache.get_history()
            forecast_out = cache.get_forecast()
            if _is_forecast_empty(forecast_out) and history_out:
                forecast_out = _run_forecast_all(history_out, indices)
            return {
                'entity_id':        entity_id,
                'entity_type':      entity_type,
                'name':             name,
                'period':           {'from': cache.period_from, 'to': cache.period_to},
                'history':          history_out,
                'forecast':         forecast_out,
                'ltv':              cache.get_ltv(),
                'tiers_meta':       TIERS,
                'from_cache':       True,
                'cache_stale':      True,
                'cache_updated_at': cache.updated_at.isoformat() if cache.updated_at else None,
                'out_of_bounds':    [],
            }, None
        return None, f'Sentinel API error: {e}'

    if not historical:
        return None, 'No satellite data for this location'

    # ── Enrich history (add tier + raw + oob flag per index) ─────────────────
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
    if _is_forecast_empty(forecast_out):
        logger.warning(
            f'[SentinelForecast] All forecasts empty for {entity_id}. '
            f'Install Prophet: pip install prophet'
        )

    # ── LTV ──────────────────────────────────────────────────────────────────
    ltv_data = None
    if entity_type == 'farm':
        area_ha, _ = _compute_area_ha_from_points(points)
        recent_ndvi = next(
            (r.get('ndvi') for r in reversed(historical) if r.get('ndvi') is not None),
            0.4,
        )
        if area_ha > 0:
            ltv_data = compute_ltv(recent_ndvi, area_ha, yield_t_per_ha, price_per_t, loan_amount)

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
            logger.info(
                f'[SentinelCache] Saved for {entity_id}. '
                f'OOB events: {len(out_of_bounds)}. '
                f'Forecast empty: {_is_forecast_empty(forecast_out)}.'
            )
        except Exception as e:
            logger.error(f'[SentinelCache] Save error: {e}')
            db.session.rollback()

    return {
        'entity_id':    entity_id,
        'entity_type':  entity_type,
        'name':         name,
        'period':       {'from': date_from[:10], 'to': date_to[:10]},
        'history':      history_out,
        'forecast':     forecast_out,
        'ltv':          ltv_data,
        'tiers_meta':   TIERS,
        'from_cache':   False,
        'out_of_bounds': out_of_bounds,  # list of {date, index, raw, clamped_to}
    }, None