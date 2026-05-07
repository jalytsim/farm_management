"""
sentinel_utils.py — Sentinel-2 + Prophet ML Forecast

Fixes vs previous version:
  - Prophet ImportError is now VISIBLE (logged, not silent)
  - Cache poison detection: if cached forecast is empty, Prophet is re-run
    directly from cached history (no Sentinel API call needed)
  - _prophet_forecast now logs the exact failure reason
  - force_refresh=True always recomputes forecast regardless of cache
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
        'grant_type': 'client_credentials',
        'client_id': SENTINEL_CLIENT_ID,
        'client_secret': SENTINEL_CLIENT_SECRET,
    }, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=15)
    resp.raise_for_status()
    d = resp.json()
    _token_cache['token'] = d['access_token']
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
    token = _get_token()
    payload = {
        'input': {
            'bounds': {'geometry': geometry},
            'data': [{'type': 'sentinel-2-l2a', 'dataFilter': {
                'timeRange': {'from': date_from, 'to': date_to},
                'maxCloudCoverage': 30,
            }}]
        },
        'aggregation': {
            'timeRange': {'from': date_from, 'to': date_to},
            'aggregationInterval': {'of': 'P3M'},
            'resx': 0.0001, 'resy': 0.0001,
            'evalscript': EVALSCRIPT,
        },
        'calculations': {'default': {}}
    }
    resp = requests.post(STATS_URL, json=payload,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        timeout=90)
    resp.raise_for_status()
    return resp.json()

def _parse_response(api_response):
    result = []
    for item in api_response.get('data', []):
        date = item['interval']['from'][:10]
        row = {'date': date}
        for idx, idx_data in item.get('outputs', {}).items():
            if idx == 'dataMask':
                continue
            try:
                val = float(idx_data['bands']['B0']['stats']['mean'])
                if val != val or abs(val) > 1e6:
                    val = None
            except Exception:
                val = None
            row[idx] = val
        result.append(row)
    return result

# ── Tiers ─────────────────────────────────────────────────────
TIERS = {
    'ndvi': [
        {'max': 0.20, 'label': 'Very Low',  'color': '#dc2626', 'bg': '#fef2f2'},
        {'max': 0.35, 'label': 'Low',       'color': '#f97316', 'bg': '#fff7ed'},
        {'max': 0.50, 'label': 'Medium',    'color': '#ca8a04', 'bg': '#fefce8'},
        {'max': 0.65, 'label': 'High',      'color': '#16a34a', 'bg': '#f0fdf4'},
        {'max': 1.00, 'label': 'Very High', 'color': '#15803d', 'bg': '#dcfce7'},
    ],
    'ndmi': [
        {'max': -0.20, 'label': 'Severe Drought', 'color': '#dc2626', 'bg': '#fef2f2'},
        {'max':  0.00, 'label': 'Dry',            'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  0.20, 'label': 'Normal',          'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  0.40, 'label': 'Moist',           'color': '#16a34a', 'bg': '#f0fdf4'},
        {'max':  1.00, 'label': 'Very Wet',        'color': '#0284c7', 'bg': '#eff6ff'},
    ],
    'ndwi': [
        {'max': -0.30, 'label': 'Dry / Built-up', 'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  0.00, 'label': 'Bare Soil',       'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  0.20, 'label': 'Low Water',       'color': '#16a34a', 'bg': '#f0fdf4'},
        {'max':  1.00, 'label': 'Water Body',      'color': '#0284c7', 'bg': '#eff6ff'},
    ],
    'nmdi': [
        {'max': 0.45, 'label': 'Very Wet',       'color': '#0284c7', 'bg': '#eff6ff'},
        {'max': 0.55, 'label': 'Good',           'color': '#16a34a', 'bg': '#f0fdf4'},
        {'max': 0.65, 'label': 'Moderate',       'color': '#ca8a04', 'bg': '#fefce8'},
        {'max': 0.75, 'label': 'Drought Risk',   'color': '#f97316', 'bg': '#fff7ed'},
        {'max': 1.00, 'label': 'Severe Drought', 'color': '#dc2626', 'bg': '#fef2f2'},
    ],
    'evi': [
        {'max': 0.15, 'label': 'Very Low',  'color': '#dc2626', 'bg': '#fef2f2'},
        {'max': 0.25, 'label': 'Low',       'color': '#f97316', 'bg': '#fff7ed'},
        {'max': 0.35, 'label': 'Medium',    'color': '#ca8a04', 'bg': '#fefce8'},
        {'max': 0.45, 'label': 'High',      'color': '#16a34a', 'bg': '#f0fdf4'},
        {'max': 1.00, 'label': 'Very High', 'color': '#15803d', 'bg': '#dcfce7'},
    ],
    'savi': [
        {'max': 0.15, 'label': 'Very Low',  'color': '#dc2626', 'bg': '#fef2f2'},
        {'max': 0.25, 'label': 'Low',       'color': '#f97316', 'bg': '#fff7ed'},
        {'max': 0.35, 'label': 'Medium',    'color': '#ca8a04', 'bg': '#fefce8'},
        {'max': 0.45, 'label': 'High',      'color': '#16a34a', 'bg': '#f0fdf4'},
        {'max': 1.00, 'label': 'Very High', 'color': '#15803d', 'bg': '#dcfce7'},
    ],
    'nbr': [
        {'max': -0.10, 'label': 'High Severity Burn', 'color': '#7f1d1d', 'bg': '#fef2f2'},
        {'max':  0.10, 'label': 'Moderate Burn',      'color': '#dc2626', 'bg': '#fef2f2'},
        {'max':  0.27, 'label': 'Low Severity Burn',  'color': '#f97316', 'bg': '#fff7ed'},
        {'max':  0.44, 'label': 'Unburned',           'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  1.00, 'label': 'Healthy Forest',     'color': '#15803d', 'bg': '#dcfce7'},
    ],
    'bsi': [
        {'max': -0.20, 'label': 'Dense Vegetation', 'color': '#15803d', 'bg': '#dcfce7'},
        {'max':  0.00, 'label': 'Vegetation Cover', 'color': '#16a34a', 'bg': '#f0fdf4'},
        {'max':  0.20, 'label': 'Partially Bare',   'color': '#ca8a04', 'bg': '#fefce8'},
        {'max':  1.00, 'label': 'Bare Soil',        'color': '#92400e', 'bg': '#fff7ed'},
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


# ── Prophet Forecast ──────────────────────────────────────────
# FIX: errors are now logged explicitly instead of silently swallowed.
def _prophet_forecast(data, index_name, periods=4):
    """
    data: list of dicts — can be either:
      - raw format:      [{date, ndvi: float, ...}]     (from _parse_response)
      - enriched format: [{date, ndvi: {value, tier}}]  (from history_out / cache)
    Both formats are handled.
    """
    # ── Check Prophet availability FIRST — fail loudly ────────────────────
    try:
        from prophet import Prophet
    except ImportError:
        logger.error(
            '[SentinelForecast] Prophet is NOT installed on this server. '
            'Run: pip install prophet  (or: pip install neuralprophet). '
            'Forecast will be empty until Prophet is installed.'
        )
        return []

    # ── Extract (date, value) pairs — handle both data formats ────────────
    rows = []
    for d in data:
        raw = d.get(index_name)
        if raw is None:
            continue
        # Enriched format: {value: float, tier: {...}}
        if isinstance(raw, dict):
            val = raw.get('value')
        else:
            # Raw format: float
            val = raw
        if val is not None:
            rows.append((d['date'], val))

    if len(rows) < 8:
        logger.warning(
            f'[SentinelForecast] Not enough data for {index_name}: '
            f'{len(rows)} points (need ≥ 8). Forecast skipped.'
        )
        return []

    try:
        df = pd.DataFrame({
            'ds': pd.to_datetime([r[0] for r in rows]),
            'y':  [r[1] for r in rows],
        })
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='additive',
            interval_width=0.80,
        )
        model.fit(df)
        future   = model.make_future_dataframe(periods=periods, freq='QS')
        forecast = model.predict(future)
        pred     = forecast[forecast['ds'] > df['ds'].max()]

        result = []
        for _, row in pred.iterrows():
            val = round(float(row['yhat']), 4)
            lo  = round(float(row['yhat_lower']), 4)
            hi  = round(float(row['yhat_upper']), 4)
            result.append({
                'date':        row['ds'].strftime('%Y-%m-%d'),
                'quarter':     row['ds'].strftime('%Y-Q') + str((row['ds'].month - 1) // 3 + 1),
                'value':       val,
                'lower_80':    lo,
                'upper_80':    hi,
                'tier':        get_tier(index_name, val),
                'is_forecast': True,
            })

        logger.info(f'[SentinelForecast] {index_name}: {len(result)} forecast quarters generated.')
        return result

    except Exception as e:
        logger.error(f'[SentinelForecast] Prophet failed for {index_name}: {e}', exc_info=True)
        return []


def _is_forecast_empty(forecast_dict):
    """True if all indices have empty forecast lists — indicates cache poison."""
    if not forecast_dict:
        return True
    return all(len(v) == 0 for v in forecast_dict.values())


def _run_forecast_all(history_data, indices):
    """
    Run Prophet forecast for all indices from history data.
    history_data: list of dicts (raw OR enriched format both accepted)
    Returns: {idx: [forecast_items]}
    """
    result = {}
    for idx in indices:
        result[idx] = _prophet_forecast(history_data, idx, periods=4)
    return result


# ── LTV ───────────────────────────────────────────────────────
def compute_ltv(ndvi_mean, area_ha, yield_t_per_ha=1.5,
                price_per_t=500, loan_amount=None):
    ndvi_factor    = max(0.3, min(1.0, ndvi_mean / 0.7))
    adjusted_yield = yield_t_per_ha * ndvi_factor
    crop_value     = round(area_ha * adjusted_yield * price_per_t, 2)
    ltv_ratio      = round(loan_amount / crop_value * 100, 1) if loan_amount and crop_value > 0 else None

    base   = 3.0
    n_risk = max(0, (0.5 - ndvi_mean) * 10)
    l_risk = max(0, ((ltv_ratio or 60) - 60) * 0.05)
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

# ── Geometry helpers ──────────────────────────────────────────
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
                [lon-d,lat-d],[lon+d,lat-d],[lon+d,lat+d],[lon-d,lat+d],[lon-d,lat-d]
            ]]}
        except Exception:
            pass
    return None


# ── Main entry point ──────────────────────────────────────────
def get_sat_index_full(entity_type, entity_id,
                       loan_amount=None, yield_t_per_ha=1.5, price_per_t=500,
                       force_refresh=False):
    """
    Main entry point for Sat-Index.
    - Checks DB cache first (SentinelCache)
    - FIX: if cached forecast is empty (cache poison), recomputes forecast
      from cached history WITHOUT calling Sentinel API again
    - force_refresh=True forces a full Sentinel API call
    """
    from app.models import Farm, Forest, Point, SentinelCache
    from app import db
    import json
    from datetime import timedelta

    indices = ['ndvi', 'ndmi', 'ndwi', 'nmdi', 'evi', 'savi', 'nbr', 'bsi']

    if entity_type == 'farm':
        entity = Farm.query.filter_by(farm_id=entity_id).first()
        if not entity:
            return None, 'Farm not found'
        points   = Point.query.filter_by(owner_type='farmer', owner_id=str(entity.id)).order_by(Point.id).all()
        geometry = _build_geometry(points, entity.geolocation)
        name     = entity.name
    else:
        entity = Forest.query.filter_by(id=entity_id).first()
        if not entity:
            return None, 'Forest not found'
        points   = Point.query.filter_by(owner_type='forest', owner_id=str(entity_id)).order_by(Point.id).all()
        geometry = _build_geometry(points)
        name     = entity.name

    if not geometry:
        return None, 'No geometry available — add polygon points first'

    # ── Check cache ────────────────────────────────────────────────────────
    cache = None
    if entity_type == 'farm':
        cache = SentinelCache.query.filter_by(farm_id=entity_id).first()

    if cache and not cache.is_stale() and not force_refresh:
        history_out  = cache.get_history()
        forecast_out = cache.get_forecast()

        # ── FIX: Cache poison detection ───────────────────────────────────
        # If forecast is empty (Prophet wasn't installed when cache was created),
        # recompute it from cached history — no Sentinel API call needed.
        if _is_forecast_empty(forecast_out) and history_out:
            logger.warning(
                f'[SentinelCache] Cached forecast for {entity_id} is empty (likely Prophet was '
                f'missing when cache was created). Recomputing forecast from {len(history_out)} '
                f'cached history points...'
            )
            forecast_out = _run_forecast_all(history_out, indices)

            # Persist the recomputed forecast back to cache
            if not _is_forecast_empty(forecast_out):
                try:
                    cache.forecast_json = json.dumps(forecast_out)
                    db.session.commit()
                    logger.info(f'[SentinelCache] Forecast recomputed and saved for {entity_id}.')
                except Exception as e:
                    logger.error(f'[SentinelCache] Could not save recomputed forecast: {e}')
                    db.session.rollback()
        # ── end fix ───────────────────────────────────────────────────────

        ltv_data = None
        if loan_amount or yield_t_per_ha != 1.5 or price_per_t != 500:
            recent_ndvi = next(
                (r.get('ndvi', {}).get('value') if isinstance(r.get('ndvi'), dict) else r.get('ndvi')
                 for r in reversed(history_out) if r.get('ndvi') is not None),
                0.4
            )
            try:
                from app.utils.dashboard_utils import (
                    _build_area_map_from_points, _get_fallback_acreage_map, get_farm_area_ha
                )
                area_map     = _build_area_map_from_points()
                fallback_map = _get_fallback_acreage_map()
                area_ha, _   = get_farm_area_ha(entity.id, area_map, fallback_map, entity_id)
                if area_ha > 0:
                    ltv_data = compute_ltv(recent_ndvi, area_ha, yield_t_per_ha, price_per_t, loan_amount)
            except Exception:
                ltv_data = cache.get_ltv()
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
        }, None

    # ── Full Sentinel API call ─────────────────────────────────────────────
    now       = datetime.utcnow()
    date_to   = now.strftime('%Y-%m-%dT23:59:59Z')
    date_from = (now - relativedelta(years=5)).strftime('%Y-%m-%dT00:00:00Z')

    try:
        raw        = _call_statistics(geometry, date_from, date_to)
        historical = _parse_response(raw)
    except Exception as e:
        logger.error(f'[Sentinel] API call failed for {entity_id}: {e}')
        # Serve stale cache if available rather than empty response
        if cache:
            history_out  = cache.get_history()
            forecast_out = cache.get_forecast()
            # Even on API failure, try to fix empty forecast from stale history
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
            }, None
        return None, f'Sentinel API error: {e}'

    if not historical:
        return None, 'No satellite data for this location'

    # ── Enrich history ────────────────────────────────────────────────────
    history_out = []
    for row in historical:
        out = {'date': row['date']}
        for idx in indices:
            val = row.get(idx)
            out[idx] = {'value': val, 'tier': get_tier(idx, val)}
        history_out.append(out)

    # ── Run Prophet forecast ───────────────────────────────────────────────
    # Pass raw `historical` (float values) — _prophet_forecast handles both formats
    forecast_out = _run_forecast_all(historical, indices)

    if _is_forecast_empty(forecast_out):
        logger.warning(
            f'[SentinelForecast] All forecasts empty for {entity_id}. '
            f'Check Prophet installation: pip install prophet'
        )

    # ── LTV ───────────────────────────────────────────────────────────────
    ltv_data = None
    if entity_type == 'farm':
        try:
            from app.utils.dashboard_utils import (
                _build_area_map_from_points, _get_fallback_acreage_map, get_farm_area_ha
            )
            area_map     = _build_area_map_from_points()
            fallback_map = _get_fallback_acreage_map()
            area_ha, _   = get_farm_area_ha(entity.id, area_map, fallback_map, entity_id)
        except Exception:
            area_ha = 0

        recent_ndvi = next(
            (r.get('ndvi') for r in reversed(historical) if r.get('ndvi') is not None), 0.4
        )
        if area_ha > 0:
            ltv_data = compute_ltv(recent_ndvi, area_ha, yield_t_per_ha, price_per_t, loan_amount)

    # ── Save to cache ──────────────────────────────────────────────────────
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
            logger.info(f'[SentinelCache] Saved for {entity_id}. Forecast empty: {_is_forecast_empty(forecast_out)}')
        except Exception as e:
            logger.error(f'[SentinelCache] Save error: {e}')
            db.session.rollback()

    return {
        'entity_id':   entity_id,
        'entity_type': entity_type,
        'name':        name,
        'period':      {'from': date_from[:10], 'to': date_to[:10]},
        'history':     history_out,
        'forecast':    forecast_out,
        'ltv':         ltv_data,
        'tiers_meta':  TIERS,
        'from_cache':  False,
    }, None