"""
api_tree_co2.py
──────────────────────────────────────────────────────────────────────────────
Routes pour le rapport de séquestration CO2 par arbre (AGB + sigmoid).
À placer dans app/routes/api_tree_co2.py et enregistrer le blueprint dans
app/__init__.py, ex: app.register_blueprint(api_tree_co2.bp)
"""

import os
import tempfile
from flask import Blueprint, jsonify, send_file

from app.models import Forest, Point
from app.utils.tree_co2_utils import compute_forest_co2_summary, compute_forest_biomass_from_index
from app.utils.pdf_reports import build_tree_co2_pdf, build_forest_biomass_index_pdf

bp = Blueprint('api_tree_co2', __name__, url_prefix='/api/tree-co2')

_STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
LOGO_PARROT = os.path.join(_STATIC_DIR, 'parrotlogo.png')
LOGO_AGRI   = os.path.join(_STATIC_DIR, 'logo.jpg')


def _send_pdf(pdf_bytes: bytes, filename: str):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp.write(pdf_bytes)
    tmp.close()
    return send_file(tmp.name, mimetype='application/pdf',
                      as_attachment=True, download_name=filename)


@bp.route('/species-params', methods=['GET'])
def species_growth_params():
    """
    Paramètres de croissance sigmoid (km, t_half, mmax) par espèce.
    GET /api/tree-co2/species-params
    Utilisé par TreeList.jsx (Tree Manager) pour tracer la courbe sigmoid
    d'un arbre directement depuis la liste générale, sans passer par le
    rapport CO2 complet d'une forêt (qui suppose un forest_id unique).
    """
    from app.models import SpeciesGrowthParams
    from app.utils.tree_co2_utils import DEFAULT_GROWTH_PARAMS

    rows = SpeciesGrowthParams.query.all()
    species = {r.species_name: {'km': r.km, 't_half': r.t_half, 'mmax': r.mmax} for r in rows}
    return jsonify({'default': DEFAULT_GROWTH_PARAMS, 'species': species}), 200


@bp.route('/forest/<int:forest_id>/report', methods=['GET'])
def forest_co2_report(forest_id):
    """
    Rapport CO2 (JSON) — détail par arbre + totaux.
    GET /api/tree-co2/forest/<forest_id>/report
    """
    forest = Forest.query.filter_by(id=forest_id).first()
    if not forest:
        return jsonify({"error": "Forest not found"}), 404

    try:
        result = compute_forest_co2_summary(forest_id)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    return jsonify(result), 200


@bp.route('/forest/<int:forest_id>/co2-pdf', methods=['GET'])
def forest_co2_pdf(forest_id):
    """
    Rapport CO2 (PDF).
    GET /api/tree-co2/forest/<forest_id>/co2-pdf
    """
    forest = Forest.query.filter_by(id=forest_id).first()
    if not forest:
        return jsonify({"error": "Forest not found"}), 404

    forest_info = {
        'name':      forest.name,
        'tree_type': forest.tree_type,
    }

    try:
        co2_report = compute_forest_co2_summary(forest_id)
        pdf_bytes = build_tree_co2_pdf(
            forest_id   = forest_id,
            forest_info = forest_info,
            co2_report  = co2_report,
            logo_parrot = LOGO_PARROT,
            logo_agri   = LOGO_AGRI,
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    return _send_pdf(pdf_bytes, f'Tree_CO2_Report_{forest_id}.pdf')


def _compute_forest_biomass_index(forest_id):
    """
    Helper partagé par les routes JSON et PDF ci-dessous : estimation AGB/BGB/CO2
    de la forêt ENTIÈRE à partir du NDVI moyen (Sentinel-2), sans dépendre des
    mesures diamètre/hauteur arbre par arbre (compute_forest_co2_summary reste
    la source "mesurée" quand les arbres sont inventoriés). Remplace la vue GFW
    pré-calculée de CarbonReportForest.jsx par un calcul AGB/BGB dérivé des indices.

    Retourne (result_dict, error_message, status_code). result_dict est None
    en cas d'erreur.
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    from app.utils.sentinel_utils import _build_geometry, _compute_area_ha_from_points, _call_statistics, _parse_response

    forest = Forest.query.filter_by(id=forest_id).first()
    if not forest:
        return None, "Forest not found", 404

    points = Point.query.filter_by(owner_type='forest', owner_id=str(forest_id)).order_by(Point.id).all()
    geometry = _build_geometry(points)
    if not geometry:
        return None, "No polygon found for this forest — add polygon points first", 400

    area_ha, _ = _compute_area_ha_from_points(points)
    if not area_ha:
        return None, "Could not compute forest area from polygon", 400

    now = datetime.utcnow()
    date_to = now.strftime('%Y-%m-%dT23:59:59Z')
    date_from = (now - relativedelta(months=6)).strftime('%Y-%m-%dT00:00:00Z')

    try:
        raw = _call_statistics(geometry, date_from, date_to, interval='P1M')
        rows, out_of_bounds = _parse_response(raw)
    except Exception as e:
        import traceback; traceback.print_exc()
        return None, f"Sentinel query failed: {str(e)}", 500

    # Valeur NDVI la plus récente disponible sur les 6 derniers mois (mensuel).
    ndvi_rows = [r for r in rows if r.get('ndvi') is not None]
    if not ndvi_rows:
        return None, "No cloud-free NDVI reading available for this forest in the last 6 months", 404
    latest = max(ndvi_rows, key=lambda r: r['date'])

    try:
        biomass = compute_forest_biomass_from_index(latest['ndvi'], area_ha, index_date=latest['date'])
    except Exception as e:
        import traceback; traceback.print_exc()
        return None, str(e), 500

    return {
        'forest_id':    forest_id,
        'forest_name':  forest.name,
        'tree_type':    forest.tree_type,
        'area_ha':      round(area_ha, 4),
        'biomass':      biomass,
        'ndvi_history': rows,
        # anneau extérieur du polygone, pour la carte statique du frontend
        # (évite un second aller-retour réseau vers /export/polygon)
        'coordinates':  geometry['coordinates'][0],
    }, None, 200


@bp.route('/forest/<int:forest_id>/biomass-index', methods=['GET'])
def forest_biomass_from_index(forest_id):
    """
    GET /api/tree-co2/forest/<forest_id>/biomass-index
    Estimation AGB/BGB/CO2 de la forêt entière à partir du NDVI (JSON, écran).
    """
    result, error, code = _compute_forest_biomass_index(forest_id)
    if error:
        return jsonify({"error": error}), code
    return jsonify(result), 200


@bp.route('/forest/<int:forest_id>/biomass-index-pdf', methods=['GET'])
def forest_biomass_from_index_pdf(forest_id):
    """
    GET /api/tree-co2/forest/<forest_id>/biomass-index-pdf
    Même estimation AGB/BGB/CO2, en PDF (bouton "Download PDF Report").
    """
    result, error, code = _compute_forest_biomass_index(forest_id)
    if error:
        return jsonify({"error": error}), code

    try:
        pdf_bytes = build_forest_biomass_index_pdf(
            forest_id   = forest_id,
            forest_name = result['forest_name'],
            area_ha     = result['area_ha'],
            biomass     = result['biomass'],
            tree_type   = result.get('tree_type'),
            logo_parrot = LOGO_PARROT,
            logo_agri   = LOGO_AGRI,
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    return _send_pdf(pdf_bytes, f'Forest_Biomass_Index_Report_{forest_id}.pdf')