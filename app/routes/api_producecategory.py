from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import ProduceCategory, db

bp = Blueprint('api_producecategory', __name__, url_prefix='/api/producecategory')


def _serialize(category):
    return {
        "id":           category.id,
        "name":         category.name,
        "date_created": category.date_created,
        "date_updated": category.date_updated,
        "created_by":   category.created_by,
        "modified_by":  category.modified_by,
    }


# ── GET all ──────────────────────────────────────────────────────────────────
@bp.route('/', methods=['GET'])
@jwt_required()
def index():
    categories = ProduceCategory.query.all()
    return jsonify(categories=[_serialize(c) for c in categories])


# ── CREATE ───────────────────────────────────────────────────────────────────
@bp.route('/create', methods=['POST'])
@jwt_required()
def create_category():
    identity   = get_jwt_identity()          # dict with 'id', 'user_type', etc.
    user_id    = identity.get('id')

    data = request.json
    name = data.get('name', '').strip()

    if not name:
        return jsonify({"msg": "Name is required"}), 400

    new_category = ProduceCategory(
        name=name,
        created_by=user_id,                  # ✅ integer from JWT, not a string
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow(),
    )
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"msg": "Produce category created successfully!"}), 201


# ── EDIT ─────────────────────────────────────────────────────────────────────
@bp.route('/<int:id>/edit', methods=['PUT'])
@jwt_required()
def edit_category(id):
    identity  = get_jwt_identity()
    user_id   = identity.get('id')

    category  = ProduceCategory.query.get_or_404(id)
    data      = request.json

    name = data.get('name', '').strip()
    if not name:
        return jsonify({"msg": "Name is required"}), 400

    category.name        = name
    category.modified_by = user_id           # ✅ integer from JWT
    category.date_updated = datetime.utcnow()

    db.session.commit()
    return jsonify({"msg": "Produce category updated successfully!"})


# ── GET by ID ────────────────────────────────────────────────────────────────
@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_category(id):
    category = ProduceCategory.query.get_or_404(id)
    return jsonify(_serialize(category))


# ── DELETE ───────────────────────────────────────────────────────────────────
@bp.route('/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_category(id):
    category = ProduceCategory.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"msg": "Produce category deleted successfully!"})


# ── GET by crop ──────────────────────────────────────────────────────────────
@bp.route('/getbycrop/<int:crop_id>', methods=['GET'])
@jwt_required()
def get_by_crop_id(crop_id):
    from app.models import Crop  # local import to avoid circular dependency
    categories = ProduceCategory.query.join(Crop).filter(Crop.id == crop_id).all()
    if not categories:
        return jsonify({'status': 'error', 'message': 'No data found for the provided crop ID'}), 404
    return jsonify({'status': 'success', 'categories': [_serialize(c) for c in categories]})