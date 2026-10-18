"""
crop_calibration_utils.py
──────────────────────────────────────────────────────────────────────────────
Calibration, par culture pérenne, de la relation indice Sentinel-2 → biomasse
aérienne à partir des parcelles mesurées sur le terrain par Nkusu.

Aucune équation « indice → biomasse » n'est publiée pour le café, le cacao,
l'avocat Hass ou le palmier à huile : on la construit avec nos propres mesures.

  1. Parcelle de mesure (CropCalibrationPlot) : diamètre / hauteur moyens des
     plants + densité de plantation (plants/ha), à une date donnée.
       AGB (t/ha) = équation allométrique de la culture (kg/plant,
                    crop_biomass_utils.ALLOMETRIC_MODELS) × plants/ha / 1000
  2. Indices Sentinel-2 (NDVI, EVI, SAVI, NDRE) de la ferme sur la fenêtre
     de ± WINDOW_DAYS jours autour de la mesure (nuages masqués).
  3. Pour chaque famille de culture, régression linéaire AGB = a + b × indice
     pour chaque indice candidat ; on retient l'indice au meilleur R² en
     validation croisée (leave-one-out).
  4. Le modèle remplace le modèle générique dans les rapports carbone dès
     qu'il a au moins MIN_PLOTS parcelles et un R² LOO ≥ MIN_LOO_R2, avec une
     pente positive. Sinon le rapport indique combien de parcelles manquent.
"""

import logging
from datetime import date, datetime, timedelta

import numpy as np

from app.utils.crop_biomass_utils import (
    ALLOMETRIC_MODELS, allometric_agb_per_plant_kg, is_coffee, resolve_crop_key,
)

logger = logging.getLogger(__name__)

CANDIDATE_INDICES = ('ndvi', 'evi', 'savi', 'ndre')
MIN_PLOTS = 6
MIN_LOO_R2 = 0.4
WINDOW_DAYS = 45

FAMILY_LABELS = {
    'coffee': 'Coffee', 'cocoa': 'Cocoa', 'avocado': 'Hass Avocado',
    'oil_palm': 'Oil Palm', 'rubber': 'Rubber', 'macadamia': 'Macadamia',
}


def crop_family(crop_key):
    """Toutes les variétés de café partagent un même modèle satellite."""
    if not crop_key:
        return None
    return 'coffee' if is_coffee(crop_key) else crop_key


def calibratable_family(crop_name):
    family = crop_family(resolve_crop_key(crop_name))
    return family if family in FAMILY_LABELS else None


def plot_agb_t_ha(crop_key, dbh_cm, height_m, plants_per_ha, wood_density=None):
    """AGB (t/ha) d'une parcelle : kg/plant (allométrie) × plants/ha / 1000."""
    per_plant_kg = allometric_agb_per_plant_kg(crop_key, dbh_cm, height_m, wood_density)
    return per_plant_kg * plants_per_ha / 1000.0


def fetch_plot_indices(geometry, measured_on):
    """
    Indices Sentinel-2 moyens de la ferme sur [mesure − WINDOW_DAYS, mesure +
    WINDOW_DAYS] (borné à aujourd'hui) : (dict indices, date de début) ou
    (None, None) si aucune image dégagée.
    """
    from app.utils.sentinel_utils import _call_statistics, _parse_response

    start = measured_on - timedelta(days=WINDOW_DAYS)
    # Fin exclusive à minuit : l'intervalle d'agrégation doit tenir exactement
    # dans la fenêtre, sinon l'API Statistics ne renvoie aucune donnée.
    end = min(measured_on + timedelta(days=WINDOW_DAYS), date.today()) + timedelta(days=1)
    raw = _call_statistics(
        geometry,
        start.strftime('%Y-%m-%dT00:00:00Z'),
        end.strftime('%Y-%m-%dT00:00:00Z'),
        interval=f'P{(end - start).days}D',
    )
    rows, _ = _parse_response(raw)
    rows = [r for r in rows if r.get('ndvi') is not None]
    if not rows:
        return None, None
    return {idx: rows[0].get(idx) for idx in CANDIDATE_INDICES}, rows[0]['date']


def _ols(x, y):
    X = np.column_stack([np.ones(len(x)), x])
    coefs, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coefs


def _fit_index(points):
    """(a, b, r2, loo_r2, rmse) de AGB = a + b × indice sur [(indice, agb)]."""
    x = np.array([p[0] for p in points], dtype=float)
    y = np.array([p[1] for p in points], dtype=float)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    if ss_tot == 0 or np.ptp(x) == 0:
        return None
    a, b = _ols(x, y)
    resid = y - (a + b * x)
    r2 = 1 - float((resid ** 2).sum()) / ss_tot
    loo_err = []
    for i in range(len(x)):
        keep = np.arange(len(x)) != i
        if np.ptp(x[keep]) == 0:
            return None
        ai, bi = _ols(x[keep], y[keep])
        loo_err.append(y[i] - (ai + bi * x[i]))
    loo_r2 = 1 - float(np.square(loo_err).sum()) / ss_tot
    rmse = float(np.sqrt(np.mean(resid ** 2)))
    return float(a), float(b), r2, loo_r2, rmse


def fit_family(plots):
    """
    plots : CropCalibrationPlot d'une même famille.
    Retourne l'état de calibration (meilleur indice, coefficients, qualité, actif ?).
    """
    best = None
    for idx in CANDIDATE_INDICES:
        points = [(getattr(p, idx), p.agb_t_ha) for p in plots
                  if getattr(p, idx) is not None and p.agb_t_ha is not None]
        if len(points) < 3:
            continue
        fit = _fit_index(points)
        if not fit:
            continue
        a, b, r2, loo_r2, rmse = fit
        if best is None or loo_r2 > best['loo_r2']:
            best = {'index': idx, 'a': round(a, 4), 'b': round(b, 4), 'r2': round(r2, 3),
                    'loo_r2': round(loo_r2, 3), 'rmse_t_ha': round(rmse, 3), 'n': len(points)}
    n = len(plots)
    status = {'n_plots': n, 'min_plots': MIN_PLOTS, 'min_loo_r2': MIN_LOO_R2, 'model': best}
    if n < MIN_PLOTS:
        status['active'] = False
        status['reason'] = f'{n} of {MIN_PLOTS} field plots measured'
    elif not best:
        status['active'] = False
        status['reason'] = 'no index varies enough between plots'
    elif best['b'] <= 0:
        status['active'] = False
        status['reason'] = f"biomass does not increase with {best['index'].upper()} on these plots"
    elif best['loo_r2'] < MIN_LOO_R2:
        status['active'] = False
        status['reason'] = f"cross-validated R² {best['loo_r2']} < {MIN_LOO_R2}"
    else:
        status['active'] = True
        status['reason'] = None
    if best:
        status['formula'] = (f"AGB (t/ha) = {best['a']} + {best['b']} × {best['index'].upper()} "
                             f"(calibrated on {best['n']} Nkusu field plots, LOO R² {best['loo_r2']}, "
                             f"RMSE {best['rmse_t_ha']} t/ha)")
    return status


def calibration_status(family):
    """État de calibration d'une famille (requête DB). None hors contexte applicatif."""
    from app.models import CropCalibrationPlot
    try:
        plots = CropCalibrationPlot.query.filter_by(family=family).all()
    except Exception as e:
        logger.warning(f'[Calibration] plots unavailable for {family}: {e}')
        return None
    return fit_family(plots)


def all_calibration_status():
    from app.models import CropCalibrationPlot
    plots = CropCalibrationPlot.query.all()
    out = []
    for family, label in FAMILY_LABELS.items():
        status = fit_family([p for p in plots if p.family == family])
        status.update({'family': family, 'label': label})
        out.append(status)
    return out


def active_model(crop_name):
    """
    Modèle calibré actif pour la culture, au format attendu par
    carbon_index_utils : {key, formula, indices, fn(row) → t/ha} ; sinon
    (None, raison) pour le message d'avertissement du rapport.
    """
    family = calibratable_family(crop_name)
    if not family:
        return None, None
    status = calibration_status(family)
    if not status:
        return None, None
    if not status['active']:
        return None, f"{FAMILY_LABELS[family]} index model not calibrated yet ({status['reason']})"
    m = status['model']
    return {
        'key':     f'calibrated_{family}',
        'formula': status['formula'],
        'indices': (m['index'],),
        'fn':      lambda ix, a=m['a'], b=m['b'], idx=m['index']: a + b * ix[idx],
    }, None


def create_plot(farm, data, user_id=None):
    """
    Enregistre une parcelle de mesure. data : crop, measured_on (YYYY-MM-DD),
    mean_dbh_cm, mean_height_m, plants_per_ha, wood_density, notes.
    Retourne (plot, error).
    """
    from app import db
    from app.models import CropCalibrationPlot, Point
    from app.utils.sentinel_utils import _build_geometry

    crop_name = (data.get('crop') or '').strip()
    crop_key = resolve_crop_key(crop_name)
    family = crop_family(crop_key)
    if family not in FAMILY_LABELS or crop_key not in ALLOMETRIC_MODELS:
        return None, f"'{crop_name}' is not a perennial crop with an allometric equation " \
                     f"({', '.join(FAMILY_LABELS.values())})."
    try:
        measured_on = datetime.strptime(data.get('measured_on') or '', '%Y-%m-%d').date()
    except ValueError:
        return None, 'measured_on must be a date (YYYY-MM-DD).'
    if measured_on > date.today():
        return None, 'measured_on cannot be in the future.'

    def num(key):
        v = data.get(key)
        if v in (None, ''):
            return None
        return float(v)
    try:
        dbh, height = num('mean_dbh_cm'), num('mean_height_m')
        plants, rho = num('plants_per_ha'), num('wood_density')
    except (TypeError, ValueError):
        return None, 'Measurements must be numbers.'
    if not plants or plants <= 0:
        return None, 'plants_per_ha is required.'
    try:
        agb = plot_agb_t_ha(crop_key, dbh, height, plants, rho)
    except ValueError as e:
        labels = {'dbh_cm': 'mean stem diameter (cm)', 'height_m': 'mean height (m)'}
        return None, f"{crop_name} needs: {', '.join(labels[n] for n in str(e).split(', '))}."

    points = Point.query.filter_by(owner_type='farmer', owner_id=str(farm.farm_id)).order_by(Point.id).all()
    geometry = _build_geometry(points, farm.geolocation)
    if not geometry:
        return None, 'This farm has no polygon: add its GPS points first.'
    try:
        indices, index_date = fetch_plot_indices(geometry, measured_on)
    except Exception as e:
        logger.exception('[Calibration] Sentinel query failed')
        return None, f'Sentinel query failed: {e}'
    if not indices:
        return None, (f'No cloud-free Sentinel-2 image within {WINDOW_DAYS} days of '
                      f'{measured_on.isoformat()} for this farm.')

    plot = CropCalibrationPlot(
        farm_id=farm.farm_id, crop_name=crop_name, crop_key=crop_key, family=family,
        measured_on=measured_on, mean_dbh_cm=dbh, mean_height_m=height,
        plants_per_ha=plants, wood_density=rho, agb_t_ha=round(agb, 4),
        index_date=index_date, notes=(data.get('notes') or '')[:255] or None,
        created_by=user_id, **{idx: indices.get(idx) for idx in CANDIDATE_INDICES},
    )
    db.session.add(plot)
    db.session.commit()
    return plot, None
