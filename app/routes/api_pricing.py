# app/routes/api_pricing.py
# =============================================================================
#  Régions de prix.
#    GET /api/pricing/regions        public : régions, coefficients, pays
#    PUT /api/pricing/regions/<id>   admin  : { "multiplier": 1.3, "name": "Europe" }
# =============================================================================

from decimal import Decimal, InvalidOperation
from datetime import datetime

from flask import Blueprint, jsonify, request

from app import db
from app.models import PriceRegion
from app.utils.decorators import admin_required
from app.utils.pricing import regions_payload

bp = Blueprint('api_pricing', __name__, url_prefix='/api/pricing')

MIN_MULTIPLIER = Decimal('0.5')
MAX_MULTIPLIER = Decimal('5')


@bp.route('/regions', methods=['GET'])
def list_regions():
    return jsonify(regions_payload())


@bp.route('/regions/<int:id>', methods=['PUT'])
@admin_required
def update_region(id):
    region = PriceRegion.query.get_or_404(id)
    data = request.get_json(silent=True) or {}

    if 'multiplier' in data:
        try:
            multiplier = Decimal(str(data.get('multiplier')))
        except (InvalidOperation, ValueError, TypeError):
            return jsonify({"msg": "The coefficient must be a number."}), 400
        if not (MIN_MULTIPLIER <= multiplier <= MAX_MULTIPLIER):
            return jsonify({"msg": f"The coefficient must be between {MIN_MULTIPLIER} and {MAX_MULTIPLIER}."}), 400
        region.multiplier = multiplier

    if (data.get('name') or '').strip():
        region.name = data['name'].strip()[:100]

    region.date_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Region updated", **regions_payload()})