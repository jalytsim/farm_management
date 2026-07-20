from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import HSCode, Crop, db

bp = Blueprint('api_hscode', __name__, url_prefix='/api/hscode')


def _serialize(h):
    return {
        "id": h.id,
        "code": h.code,
        "description": h.description,
        "eudr_commodity": h.eudr_commodity,
        "is_ex_code": h.is_ex_code,
        "crop_ids": [c.id for c in h.crops],
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


# Create a new HS code
@bp.route('/create', methods=['POST'])
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
    return jsonify({"msg": "HS code created successfully!", "id": new_hscode.id}), 201


# Edit an existing HS code
@bp.route('/<int:id>/edit', methods=['PUT'])
def edit_hscode(id):
    h = HSCode.query.get_or_404(id)
    data = request.json
    h.code = data.get('code', h.code)
    h.description = data.get('description', h.description)
    h.eudr_commodity = data.get('eudr_commodity', h.eudr_commodity)
    h.is_ex_code = bool(data.get('is_ex_code', h.is_ex_code))
    h.date_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "HS code updated successfully!"})


# Get one HS code
@bp.route('/<int:id>', methods=['GET'])
def get_hscode(id):
    h = HSCode.query.get_or_404(id)
    return jsonify(_serialize(h))


# Delete an HS code
@bp.route('/<int:id>/delete', methods=['DELETE'])
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
def link_crop(id, crop_id):
    h = HSCode.query.get_or_404(id)
    crop = Crop.query.get_or_404(crop_id)
    if crop not in h.crops:
        h.crops.append(crop)
        db.session.commit()
    return jsonify({"msg": "Crop linked to HS code successfully!"})


# Unlink a crop from an HS code
@bp.route('/<int:id>/unlink/<int:crop_id>', methods=['DELETE'])
def unlink_crop(id, crop_id):
    h = HSCode.query.get_or_404(id)
    crop = Crop.query.get_or_404(crop_id)
    if crop in h.crops:
        h.crops.remove(crop)
        db.session.commit()
    return jsonify({"msg": "Crop unlinked from HS code successfully!"})
