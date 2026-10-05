from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from app.models import CropVariety, Crop, User, db

bp = Blueprint('api_crop_variety', __name__, url_prefix='/api/crop-variety')


# -----------------------------------------------------------
# Helpers
# -----------------------------------------------------------
def _current_user_id():
    identity = get_jwt_identity()
    return identity['id'] if isinstance(identity, dict) else identity


def _is_admin(user_id):
    """Checks is_admin in the database, independently of the JWT content."""
    user = User.query.get(user_id)
    return bool(user and user.is_admin)


def _admin_forbidden():
    return jsonify({"message": "Only administrators can manage varieties."}), 403


def _validate_payload(data):
    """Returns (crop_id, name, description, error_response)."""
    crop_id = data.get('crop_id')
    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip() or None

    if not crop_id:
        return None, None, None, (jsonify({"message": "crop_id is required."}), 400)
    if not name:
        return None, None, None, (jsonify({"message": "name is required."}), 400)
    if len(name) > 100:
        return None, None, None, (jsonify({"message": "name must be 100 characters or less."}), 400)

    try:
        crop_id = int(crop_id)
    except (TypeError, ValueError):
        return None, None, None, (jsonify({"message": "crop_id must be a number."}), 400)

    if not Crop.query.get(crop_id):
        return None, None, None, (jsonify({"message": "Crop not found."}), 404)

    return crop_id, name, description, None


def _name_taken(crop_id, name, exclude_id=None):
    """Case-insensitive duplicate check within the same crop."""
    q = CropVariety.query.filter(
        CropVariety.crop_id == crop_id,
        db.func.lower(CropVariety.name) == name.lower(),
    )
    if exclude_id:
        q = q.filter(CropVariety.id != exclude_id)
    return db.session.query(q.exists()).scalar()


# -----------------------------------------------------------
# Read
# -----------------------------------------------------------
@bp.route('/', methods=['GET'])
@jwt_required()
def index():
    """All varieties. Optional filters: ?crop_id=1&active=1"""
    q = CropVariety.query
    crop_id = request.args.get('crop_id', type=int)
    if crop_id:
        q = q.filter_by(crop_id=crop_id)
    if request.args.get('active') == '1':
        q = q.filter_by(is_active=True)

    varieties = q.order_by(CropVariety.crop_id, CropVariety.name).all()
    return jsonify(varieties=[v.to_dict() for v in varieties])


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_variety(id):
    variety = CropVariety.query.get_or_404(id)
    return jsonify(variety.to_dict())


@bp.route('/getbycrop/<int:crop_id>', methods=['GET'])
@jwt_required()
def get_by_crop(crop_id):
    """Active varieties of one crop. Returns an empty list (not 404) when none exist,
    so dropdowns can simply show 'no variety'."""
    varieties = (CropVariety.query
                 .filter_by(crop_id=crop_id, is_active=True)
                 .order_by(CropVariety.name)
                 .all())
    return jsonify(varieties=[v.to_dict() for v in varieties])


# -----------------------------------------------------------
# Write (admin only)
# -----------------------------------------------------------
@bp.route('/create', methods=['POST'])
@jwt_required()
def create_variety():
    user_id = _current_user_id()
    if not _is_admin(user_id):
        return _admin_forbidden()

    data = request.get_json(silent=True) or {}
    crop_id, name, description, error = _validate_payload(data)
    if error:
        return error

    if _name_taken(crop_id, name):
        return jsonify({"message": f"The variety '{name}' already exists for this crop."}), 409

    variety = CropVariety(
        crop_id=crop_id,
        name=name,
        description=description,
        is_active=bool(data.get('is_active', True)),
        created_by=user_id,
        modified_by=user_id,
    )
    db.session.add(variety)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": f"The variety '{name}' already exists for this crop."}), 409

    return jsonify({"message": "Variety created successfully.", "variety": variety.to_dict()}), 201


@bp.route('/<int:id>/edit', methods=['PUT'])
@jwt_required()
def edit_variety(id):
    user_id = _current_user_id()
    if not _is_admin(user_id):
        return _admin_forbidden()

    variety = CropVariety.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    crop_id, name, description, error = _validate_payload(data)
    if error:
        return error

    if _name_taken(crop_id, name, exclude_id=id):
        return jsonify({"message": f"The variety '{name}' already exists for this crop."}), 409

    variety.crop_id = crop_id
    variety.name = name
    variety.description = description
    if 'is_active' in data:
        variety.is_active = bool(data.get('is_active'))
    variety.modified_by = user_id
    variety.date_updated = datetime.utcnow()

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": f"The variety '{name}' already exists for this crop."}), 409

    return jsonify({"message": "Variety updated successfully.", "variety": variety.to_dict()})


@bp.route('/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_variety(id):
    user_id = _current_user_id()
    if not _is_admin(user_id):
        return _admin_forbidden()

    variety = CropVariety.query.get_or_404(id)
    db.session.delete(variety)
    try:
        db.session.commit()
    except IntegrityError:
        # Will happen later once warehouse receipts reference varieties:
        # a used variety must be deactivated, not deleted.
        db.session.rollback()
        return jsonify({"message": "This variety is already in use. Deactivate it instead of deleting it."}), 409

    return jsonify({"message": "Variety deleted successfully."})