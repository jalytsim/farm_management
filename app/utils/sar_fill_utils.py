"""
sar_fill_utils.py
──────────────────────────────────────────────────────────────────────────────
Comble les mois nuageux de Sentinel-2 avec Sentinel-1 (radar SAR, bande C),
qui voit à travers les nuages.

Méthode (calibration par parcelle, pas de coefficients importés) :
  1. Sentinel-1 GRD (IW, VV+VH, gamma0 terrain) agrégé par mois sur le même
     polygone et la même période que Sentinel-2 :
       VH (dB)  = 10·log10(VH)
       RVI      = 4·VH / (VV + VH)          (radar vegetation index)
  2. Pour chaque indice optique (NDVI, EVI, ...), régression linéaire sur les
     mois où les deux capteurs ont une valeur :
       indice = a + b·RVI + c·VH(dB)
  3. Mois sans valeur Sentinel-2 (trop nuageux) : valeur prédite par la
     régression, bornée à la plage observée de l'indice sur la parcelle.
     La ligne est marquée sar_filled = [indices comblés].

Un indice n'est comblé que si la régression est exploitable
(≥ MIN_PAIRS mois communs et R² ≥ MIN_R2) ; sinon le mois reste vide, comme
avant. Références : Filgueiras et al. (2019), « Crop NDVI monitoring based on
Sentinel 1 », Remote Sensing ; RVI double polarisation adapté de Kim & van Zyl (2009).
"""

import logging
import math

import numpy as np

logger = logging.getLogger(__name__)

MIN_PAIRS = 6
MIN_R2 = 0.3

S1_EVALSCRIPT = """//VERSION=3
function setup(){return{input:[{bands:['VV','VH','dataMask']}],output:[
  {id:'vv',bands:1},{id:'vh',bands:1},{id:'rvi',bands:1},{id:'dataMask',bands:1}
]};}
function evaluatePixel(s){
  if(s.dataMask===0||s.VV<=0||s.VH<=0){return{vv:[0],vh:[0],rvi:[0],dataMask:[0]};}
  return{vv:[s.VV],vh:[s.VH],rvi:[4*s.VH/(s.VV+s.VH)],dataMask:[1]};
}"""


def _mean(item, output):
    try:
        v = float(item['outputs'][output]['bands']['B0']['stats']['mean'])
        return None if v != v else v
    except (KeyError, TypeError, ValueError):
        return None


def fetch_s1_monthly(geometry, date_from, date_to):
    """{'YYYY-MM': {'rvi', 'vh_db'}} — moyennes Sentinel-1 mensuelles du polygone."""
    from app.utils.sentinel_utils import _call_statistics
    raw = _call_statistics(
        geometry, date_from, date_to, interval='P1M',
        evalscript=S1_EVALSCRIPT,
        data_type='sentinel-1-grd',
        data_filter={
            'timeRange':       {'from': date_from, 'to': date_to},
            'acquisitionMode': 'IW',
            'polarization':    'DV',
            'resolution':      'HIGH',
        },
        processing={'orthorectify': True, 'backCoeff': 'GAMMA0_TERRAIN', 'demInstance': 'COPERNICUS'},
    )
    out = {}
    for item in raw.get('data', []):
        vh, rvi = _mean(item, 'vh'), _mean(item, 'rvi')
        if vh is None or rvi is None or vh <= 0:
            continue
        out[item['interval']['from'][:7]] = {'rvi': rvi, 'vh_db': 10 * math.log10(vh)}
    return out


def _fit(pairs):
    """OLS indice ~ 1 + RVI + VH(dB). (coefs, r2) ou None."""
    X = np.array([[1.0, s['rvi'], s['vh_db']] for s, _ in pairs])
    y = np.array([v for _, v in pairs])
    coefs, *_ = np.linalg.lstsq(X, y, rcond=None)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    if ss_tot == 0:
        return None
    r2 = 1 - float(((y - X @ coefs) ** 2).sum()) / ss_tot
    return coefs, r2


def fill_with_sar(rows, s1_by_month, indices):
    """
    rows        : lignes Sentinel-2 mensuelles {date, idx, idx_raw, ...} (la
                  grille peut contenir des mois vides, idx = None).
    s1_by_month : sortie de fetch_s1_monthly.
    Ajoute les mois Sentinel-1 absents de rows, comble les indices manquants
    et renvoie (rows triées, info).
    """
    by_month = {r['date'][:7]: r for r in rows if r.get('date')}
    for month in s1_by_month:
        if month not in by_month:
            by_month[month] = {'date': f'{month}-01', **{i: None for i in indices},
                               **{f'{i}_raw': None for i in indices}}

    models, filled_months = {}, set()
    for idx in indices:
        pairs = [(s1_by_month[m], float(r[idx])) for m, r in by_month.items()
                 if r.get(idx) is not None and m in s1_by_month]
        if len(pairs) < MIN_PAIRS:
            continue
        fit = _fit(pairs)
        if not fit or fit[1] < MIN_R2:
            continue
        coefs, r2 = fit
        lo = min(v for _, v in pairs)
        hi = max(v for _, v in pairs)
        models[idx] = {'r2': round(r2, 3), 'n': len(pairs),
                       'coefs': [round(float(c), 5) for c in coefs]}
        for month, row in by_month.items():
            if row.get(idx) is not None or month not in s1_by_month:
                continue
            s1 = s1_by_month[month]
            val = float(coefs[0] + coefs[1] * s1['rvi'] + coefs[2] * s1['vh_db'])
            val = round(max(lo, min(hi, val)), 4)
            row[idx] = val
            row[f'{idx}_raw'] = val
            row.setdefault('sar_filled', []).append(idx)
            filled_months.add(month)

    info = {
        'source':        'Sentinel-1 GRD (VV/VH) regression on cloud-free Sentinel-2 months',
        'filled_months': sorted(filled_months),
        'models':        models,
    }
    if filled_months:
        logger.info(f'[SAR] {len(filled_months)} cloudy month(s) filled with Sentinel-1: {sorted(filled_months)}')
    return sorted(by_month.values(), key=lambda r: r['date']), info


def fill_rows_with_sar(rows, geometry, date_from, date_to, indices):
    """fetch_s1_monthly + fill_with_sar ; en cas d'échec Sentinel-1, rows inchangées."""
    try:
        s1 = fetch_s1_monthly(geometry, date_from, date_to)
    except Exception as e:
        logger.warning(f'[SAR] Sentinel-1 query failed, cloudy months left empty: {e}')
        return rows, None
    return fill_with_sar(rows, s1, indices)
