"""
forest_calibration_utils.py
──────────────────────────────────────────────────────────────────────────────
Calibration locale de la relation indice Sentinel-2 → biomasse aérienne des
forêts, à partir de parcelles d'inventaire mesurées sur le terrain.

Sans calibration, les forêts utilisent le modèle NDVI générique
AGB = NDVI_AGB_A × exp(NDVI_AGB_B × NDVI) (tree_co2_utils), illustratif.

  1. Parcelle d'inventaire (ForestCalibrationPlot) : surface (m²) + diamètre
     et hauteur de chaque arbre mesuré, densité du bois.
       AGB arbre (kg)   = 0.0673 × (ρ D² H)^0.976          (Chave et al. 2014)
       AGB parcelle     = Σ AGB arbres / surface → t/ha
  2. Indices Sentinel-2 (NDVI, EVI, SAVI, NDRE) du polygone de la forêt sur
     ± WINDOW_DAYS jours autour de la mesure (même requête que les cultures).
  3. Régression AGB = a + b × indice, indice retenu au meilleur R² en
     validation croisée leave-one-out (même ajustement que les cultures :
     crop_calibration_utils.fit_family).
  4. Le modèle remplace le modèle générique de toutes les forêts dès qu'il a
     MIN_PLOTS parcelles et un R² LOO ≥ MIN_LOO_R2, pente positive.
"""

import json
import logging
from datetime import date, datetime

from app.utils.crop_biomass_utils import _chave
from app.utils.crop_calibration_utils import (
    CANDIDATE_INDICES, MIN_LOO_R2, MIN_PLOTS, WINDOW_DAYS, fetch_plot_indices, fit_family,
)

logger = logging.getLogger(__name__)

# Densité de bois moyenne des forêts tropicales d'Afrique (g/cm³), utilisée si
# elle n'est pas mesurée (Reyes et al. 1992, reprise par le GIEC 2006 vol. 4).
DEFAULT_FOREST_WOOD_DENSITY = 0.58
MAX_TREES = 2000
MAX_DBH_CM = 400
MAX_HEIGHT_M = 90


def parse_trees(raw):
    """
    Arbres mesurés : liste [[D, H], ...] ou texte « D, H » une ligne par arbre
    (séparateurs virgule, point-virgule, tabulation ou espace ; collé d'Excel).
    Retourne (liste de (D cm, H m), erreur).
    """
    trees = []
    if isinstance(raw, list):
        items = raw
    else:
        items = []
        for n, line in enumerate(str(raw or '').splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            parts = [p for p in line.replace(';', ' ').replace(',', ' ').replace('\t', ' ').split() if p]
            if len(parts) != 2:
                return None, f'Line {n}: enter the diameter and the height, e.g. "32.5, 18".'
            items.append(parts + [n])
    for i, item in enumerate(items, start=1):
        line = item[2] if len(item) > 2 else i
        try:
            d, h = float(item[0]), float(item[1])
        except (TypeError, ValueError, IndexError):
            return None, f'Line {line}: diameter and height must be numbers.'
        if not 0 < d <= MAX_DBH_CM:
            return None, f'Line {line}: diameter {d} cm is outside 0–{MAX_DBH_CM} cm.'
        if not 0 < h <= MAX_HEIGHT_M:
            return None, f'Line {line}: height {h} m is outside 0–{MAX_HEIGHT_M} m.'
        trees.append((d, h))
    if not trees:
        return None, 'Enter at least one measured tree.'
    if len(trees) > MAX_TREES:
        return None, f'At most {MAX_TREES} trees per plot.'
    return trees, None


def plot_agb_t_ha(trees, plot_area_m2, wood_density):
    """AGB (t/ha) d'une parcelle : Σ Chave 2014 (kg) / surface (m²) × 10 000 / 1 000."""
    total_kg = sum(_chave(d, h, wood_density) for d, h in trees)
    return total_kg / plot_area_m2 * 10.0


def calibration_status():
    """État du modèle forêt (dict de fit_family) ; None si la table est indisponible."""
    from app.models import ForestCalibrationPlot
    try:
        plots = ForestCalibrationPlot.query.all()
    except Exception as e:
        logger.warning(f'[ForestCalibration] plots unavailable: {e}')
        return None
    status = fit_family(plots)
    if status.get('formula'):
        status['formula'] = status['formula'].replace('Nkusu field plots', 'forest inventory plots')
    return status


def active_model():
    """
    Modèle forêt calibré au format de carbon_index_utils
    ({key, formula, indices, fn(ix) → t/ha}), ou (None, raison).
    """
    status = calibration_status()
    if not status:
        return None, None
    if not status['active']:
        return None, f"Forest index model not calibrated yet ({status['reason']})"
    m = status['model']
    return {
        'key':     'calibrated_forest',
        'formula': status['formula'],
        'indices': (m['index'],),
        # Une droite peut passer sous zéro aux indices très bas : borne à 0.
        'fn':      lambda ix, a=m['a'], b=m['b'], idx=m['index']: max(0.0, a + b * ix[idx]),
    }, None


def create_plot(forest, data, user_id=None):
    """
    data : measured_on (YYYY-MM-DD), plot_area_m2, trees (texte ou liste
    [[D, H]]), wood_density?, notes?. Retourne (plot, erreur).
    """
    from app import db
    from app.models import ForestCalibrationPlot, Point
    from app.utils.sentinel_utils import _build_geometry

    try:
        measured_on = datetime.strptime(data.get('measured_on') or '', '%Y-%m-%d').date()
    except ValueError:
        return None, 'measured_on must be a date (YYYY-MM-DD).'
    if measured_on > date.today():
        return None, 'measured_on cannot be in the future.'
    try:
        area = float(data.get('plot_area_m2'))
    except (TypeError, ValueError):
        return None, 'plot_area_m2 must be a number.'
    if area <= 0:
        return None, 'plot_area_m2 must be above 0.'
    rho = data.get('wood_density')
    try:
        rho = float(rho) if rho not in (None, '') else DEFAULT_FOREST_WOOD_DENSITY
    except (TypeError, ValueError):
        return None, 'wood_density must be a number.'
    if not 0.1 <= rho <= 1.5:
        return None, 'wood_density must be between 0.1 and 1.5 g/cm³.'
    trees, error = parse_trees(data.get('trees'))
    if error:
        return None, error

    points = Point.query.filter_by(owner_type='forest', owner_id=str(forest.id)).order_by(Point.id).all()
    geometry = _build_geometry(points)
    if not geometry:
        return None, 'This forest has no polygon: add its GPS points first.'
    try:
        indices, index_date = fetch_plot_indices(geometry, measured_on)
    except Exception as e:
        logger.exception('[ForestCalibration] Sentinel query failed')
        return None, f'Sentinel query failed: {e}'
    if not indices:
        return None, (f'No cloud-free Sentinel-2 image within {WINDOW_DAYS} days of '
                      f'{measured_on.isoformat()} for this forest.')

    agb = plot_agb_t_ha(trees, area, rho)
    plot = ForestCalibrationPlot(
        forest_id=forest.id, measured_on=measured_on, plot_area_m2=area, n_trees=len(trees),
        mean_dbh_cm=round(sum(d for d, _ in trees) / len(trees), 2),
        mean_height_m=round(sum(h for _, h in trees) / len(trees), 2),
        wood_density=rho, trees_json=json.dumps(trees), agb_t_ha=round(agb, 4),
        index_date=index_date, notes=(data.get('notes') or '')[:255] or None,
        created_by=user_id, **{idx: indices.get(idx) for idx in CANDIDATE_INDICES},
    )
    db.session.add(plot)
    db.session.commit()
    return plot, None


RULES = {'min_plots': MIN_PLOTS, 'min_loo_r2': MIN_LOO_R2, 'window_days': WINDOW_DAYS,
         'default_wood_density': DEFAULT_FOREST_WOOD_DENSITY}
