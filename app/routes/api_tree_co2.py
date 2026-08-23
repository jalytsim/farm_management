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

from app.models import Forest
from app.utils.tree_co2_utils import compute_forest_co2_summary
from app.utils.pdf_reports import build_tree_co2_pdf

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