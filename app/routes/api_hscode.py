from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from app.models import HSCode, Crop, db
from flask_jwt_extended import jwt_required
from app.utils.decorators import admin_required
from app.utils.hscode_sync import (
    populate_subheadings, start_background_sync, sync_status, summary,
)

bp = Blueprint('api_hscode', __name__, url_prefix='/api/hscode')


def _serialize(h):
    return {
        "id": h.id,
        "code": h.code,
        "description": h.description,
        "eudr_commodity": h.eudr_commodity,
        "is_ex_code": h.is_ex_code,
        "crop_ids": [c.id for c in h.crops],
        # Verdict TRACES (True / False / None = pas encore vérifié) et sous-positions
        # à 6 chiffres déclarables. Les codes refusés par TRACES ne sont pas renvoyés.
        "traces_valid": h.traces_valid,
        "subheadings": [
            {"code": sub.code, "description": sub.description, "traces_valid": sub.traces_valid}
            for sub in h.subheadings if sub.traces_valid is not False
        ],
        "date_created": h.date_created,
        "date_updated": h.date_updated,
    }


# Get all HS codes (support ?commodity=Cocoa filter)
@bp.route('/', methods=['GET'])
def index():
    commodity = request.args.get('commodity')
    query = HSCode.query
    if commodity:
        query = query.filter_by(eudr_commodity=commodity)
    codes = query.order_by(HSCode.eudr_commodity, HSCode.code).all()
    return jsonify(hscodes=[_serialize(h) for h in codes])


def _refresh_traces(hscode):
    """Sous-positions créées tout de suite ; vérification TRACES en arrière-plan."""
    populate_subheadings(hscode)
    start_background_sync(current_app._get_current_object(), hscode_ids=[hscode.id])


# Synchronise les sous-positions et les verdicts TRACES de toute la table
# (plusieurs minutes : tourne en arrière-plan). ?recheck=true revérifie tout.
@bp.route('/sync-traces', methods=['POST'])
@admin_required
def sync_traces():
    recheck = request.args.get('recheck', '').lower() == 'true'
    started = start_background_sync(current_app._get_current_object(), recheck=recheck)
    return jsonify({"started": started, "status": sync_status(), "summary": summary()}), 202 if started else 409


@bp.route('/sync-traces/status', methods=['GET'])
@admin_required
def sync_traces_status():
    return jsonify({"status": sync_status(), "summary": summary()})


# Create a new HS code
@bp.route('/create', methods=['POST'])
@jwt_required()  # écran HSCodeManager ouvert aux rôles admin + farmer
def create_hscode():
    data = request.json
    new_hscode = HSCode(
        code=data.get('code'),
        description=data.get('description'),
        eudr_commodity=data.get('eudr_commodity'),
        is_ex_code=bool(data.get('is_ex_code', False)),
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )
    db.session.add(new_hscode)
    db.session.commit()
    _refresh_traces(new_hscode)
    return jsonify({"msg": "HS code created successfully!", "id": new_hscode.id}), 201


# Edit an existing HS code
@bp.route('/<int:id>/edit', methods=['PUT'])
@jwt_required()  # écran HSCodeManager ouvert aux rôles admin + farmer
def edit_hscode(id):
    h = HSCode.query.get_or_404(id)
    data = request.json
    code_changed = data.get('code') is not None and data.get('code') != h.code
    h.code = data.get('code', h.code)
    h.description = data.get('description', h.description)
    h.eudr_commodity = data.get('eudr_commodity', h.eudr_commodity)
    h.is_ex_code = bool(data.get('is_ex_code', h.is_ex_code))
    h.date_updated = datetime.utcnow()
    if code_changed:
        h.traces_valid = None
        h.traces_checked_at = None
    db.session.commit()
    if code_changed:
        _refresh_traces(h)
    return jsonify({"msg": "HS code updated successfully!"})


# Get one HS code
@bp.route('/<int:id>', methods=['GET'])
def get_hscode(id):
    h = HSCode.query.get_or_404(id)
    return jsonify(_serialize(h))


# Delete an HS code
@bp.route('/<int:id>/delete', methods=['DELETE'])
@jwt_required()  # écran HSCodeManager ouvert aux rôles admin + farmer
def delete_hscode(id):
    h = HSCode.query.get_or_404(id)
    db.session.delete(h)
    db.session.commit()
    return jsonify({"msg": "HS code deleted successfully!"})


# List distinct EUDR commodities (for dropdowns)
@bp.route('/commodities', methods=['GET'])
def list_commodities():
    rows = db.session.query(HSCode.eudr_commodity).distinct().order_by(HSCode.eudr_commodity).all()
    return jsonify(commodities=[r[0] for r in rows])


# Get HS codes linked to a given crop
@bp.route('/getbycrop/<int:crop_id>', methods=['GET'])
def get_by_crop_id(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    return jsonify({
        'status': 'success',
        'hscodes': [_serialize(h) for h in crop.hs_codes],
    })


# Link a crop to an HS code
@bp.route('/<int:id>/link/<int:crop_id>', methods=['POST'])
@jwt_required()  # écran HSCodeManager ouvert aux rôles admin + farmer
def link_crop(id, crop_id):
    h = HSCode.query.get_or_404(id)
    crop = Crop.query.get_or_404(crop_id)
    if crop not in h.crops:
        h.crops.append(crop)
        db.session.commit()
    return jsonify({"msg": "Crop linked to HS code successfully!"})


# Unlink a crop from an HS code
@bp.route('/<int:id>/unlink/<int:crop_id>', methods=['DELETE'])
@jwt_required()  # écran HSCodeManager ouvert aux rôles admin + farmer
def unlink_crop(id, crop_id):
    h = HSCode.query.get_or_404(id)
    crop = Crop.query.get_or_404(crop_id)
    if crop in h.crops:
        h.crops.remove(crop)
        db.session.commit()
    return jsonify({"msg": "Crop unlinked from HS code successfully!"})
