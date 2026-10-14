"""
forest_area_utils.py
──────────────────────────────────────────────────────────────────────────────
Surface boisée mensuelle d'une forêt (Sentinel-2) pour suivre la dégradation
et la déforestation.

Méthode :
  - un pixel (10 m) est « forêt » si NDVI > FOREST_NDVI_THRESHOLD (0.30 : seuil
    forêt / non-forêt courant dans les études Sentinel-2 en Afrique tropicale) ;
  - nuages, ombres et cirrus sont exclus via la couche SCL (classes 3, 8, 9, 10)
    pour qu'un mois nuageux ne passe pas pour une perte ; un mois dont moins de
    la moitié du polygone est dégagée est ignoré ;
  - fraction boisée = part « forêt et dégagé » / part « dégagé » ;
    surface boisée = fraction × surface ;
  - variation mensuelle = surface du mois − surface du mois précédent disponible.

Le seuil est à calibrer localement : une baisse ponctuelle peut venir d'une
saison sèche (feuillage caduc), une baisse qui se maintient signale une perte.
"""

import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

FOREST_NDVI_THRESHOLD = 0.30
MIN_VALID_FRACTION = 0.5   # en dessous, le mois est trop couvert de nuages

FOREST_EVALSCRIPT = """//VERSION=3
function setup(){return{input:[{bands:['B04','B08','SCL','dataMask']}],output:[
  {id:'forest',bands:1},{id:'clear',bands:1},{id:'dataMask',bands:1}
]};}
function evaluatePixel(s){
  if(s.dataMask===0){return{forest:[0],clear:[0],dataMask:[0]};}
  var clear = !(s.SCL===3||s.SCL===8||s.SCL===9||s.SCL===10);
  var ndvi=(s.B08-s.B04)/(s.B08+s.B04+1e-10);
  return{forest:[clear&&ndvi>%(threshold)s?1:0],clear:[clear?1:0],dataMask:[1]};
}""" % {'threshold': FOREST_NDVI_THRESHOLD}


def _stat(item, output, key):
    try:
        v = float(item['outputs'][output]['bands']['B0']['stats'][key])
        return None if v != v else v
    except (KeyError, TypeError, ValueError):
        return None


def compute_forest_area_change(geometry, area_ha, months=12):
    """
    geometry : Polygon GeoJSON (EPSG:4326), area_ha : surface du polygone.
    Retourne (result, error). result['months'] : liste chronologique de
    {month, forest_fraction, forest_area_ha, change_ha, change_pct, cloud_limited}.
    """
    from app.utils.sentinel_utils import _call_statistics

    if not area_ha or area_ha <= 0:
        return None, 'Could not compute forest area'
    months = max(2, min(int(months or 12), 60))
    now = datetime.utcnow()
    try:
        raw = _call_statistics(
            geometry,
            (now - relativedelta(months=months)).strftime('%Y-%m-01T00:00:00Z'),
            now.strftime('%Y-%m-%dT23:59:59Z'),
            interval='P1M',
            evalscript=FOREST_EVALSCRIPT,
        )
    except Exception as e:
        logger.exception('[ForestArea] Sentinel query failed')
        return None, f'Sentinel query failed: {e}'

    out, prev_area = [], None
    for item in raw.get('data', []):
        month = item['interval']['from'][:7]
        # Moyennes sur les pixels du polygone (hors polygone = noData) :
        # clear = part sans nuage, forest = part boisée ET sans nuage.
        forest_share = _stat(item, 'forest', 'mean')
        valid_share = _stat(item, 'clear', 'mean') or 0
        fraction = forest_share / valid_share if forest_share is not None and valid_share else None
        if fraction is None or valid_share < MIN_VALID_FRACTION:
            out.append({'month': month, 'forest_fraction': None, 'forest_area_ha': None,
                        'change_ha': None, 'change_pct': None, 'cloud_limited': True,
                        'valid_share': round(valid_share, 3)})
            continue
        forest_area = fraction * area_ha
        change = None if prev_area is None else forest_area - prev_area
        out.append({
            'month':           month,
            'forest_fraction': round(fraction, 4),
            'forest_area_ha':  round(forest_area, 4),
            'change_ha':       round(change, 4) if change is not None else None,
            'change_pct':      round(change / prev_area * 100, 2) if change is not None and prev_area else None,
            'cloud_limited':   False,
            'valid_share':     round(valid_share, 3),
        })
        prev_area = forest_area

    usable = [m for m in out if m['forest_area_ha'] is not None]
    if not usable:
        return None, 'No cloud-free Sentinel-2 month available for this forest'
    first, last = usable[0], usable[-1]
    net = last['forest_area_ha'] - first['forest_area_ha']
    return {
        'area_ha':         round(area_ha, 4),
        'ndvi_threshold':  FOREST_NDVI_THRESHOLD,
        'period_from':     first['month'],
        'period_to':       last['month'],
        'current_forest_area_ha': last['forest_area_ha'],
        'net_change_ha':   round(net, 4),
        'net_change_pct':  round(net / first['forest_area_ha'] * 100, 2) if first['forest_area_ha'] else None,
        'largest_monthly_loss_ha': min((m['change_ha'] for m in usable if m['change_ha'] is not None), default=None),
        'months':          out,
        'method':          f'Pixel counted as forest when NDVI > {FOREST_NDVI_THRESHOLD} '
                           '(Sentinel-2, 10 m, clouds masked with SCL); area = forest share × polygon area.',
    }, None
