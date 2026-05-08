from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, FarmerGroup, User

bp = Blueprint('api_farmergroup', __name__, url_prefix='/api/farmergroup')


def _serialize(fg):
    return {
        'id':           fg.id,
        'name':         fg.name,
        'description':  fg.description,
        'date_created': fg.date_created.isoformat() if fg.date_created else None,
        'date_updated': fg.date_updated.isoformat() if fg.date_updated else None,
    }


# ── GET all farmer groups (filtered by account) ───────────────
@bp.route('/', methods=['GET'])
@jwt_required()
def index():
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)

    # Admin → voit tout / sinon → seulement les siens
    if user.is_admin:
        groups = FarmerGroup.query.all()
    else:
        groups = FarmerGroup.query.filter_by(created_by=user_id).all()

    return jsonify([_serialize(fg) for fg in groups])


# ── CREATE farmer group ───────────────────────────────────────
@bp.route('/create', methods=['POST'])
@jwt_required()
def create_fg():
    identity = get_jwt_identity()
    user_id  = identity['id']
    data     = request.json

    new_fg = FarmerGroup(
        name        = data.get('name'),
        description = data.get('description'),
        created_by  = user_id,    # ← lie le groupe au compte créateur
        modified_by = user_id,
    )
    db.session.add(new_fg)
    db.session.commit()

    return jsonify({
        'msg': 'Farmer Group created successfully',
        'farmer_group': _serialize(new_fg),
    }), 201


# ── EDIT farmer group ─────────────────────────────────────────
@bp.route('/<int:fg_id>', methods=['PUT'])
@jwt_required()
def edit_fg(fg_id):
    identity     = get_jwt_identity()
    user_id      = identity['id']
    user         = User.query.get(user_id)
    farmer_group = FarmerGroup.query.get_or_404(fg_id)

    # Seul le propriétaire ou un admin peut modifier
    if not user.is_admin and farmer_group.created_by != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403

    data = request.json
    farmer_group.name        = data.get('name',        farmer_group.name)
    farmer_group.description = data.get('description', farmer_group.description)
    farmer_group.modified_by = user_id

    db.session.commit()
    return jsonify({
        'msg': 'Farmer Group updated successfully',
        'farmer_group': _serialize(farmer_group),
    })


# ── DELETE farmer group ───────────────────────────────────────
@bp.route('/<int:fg_id>', methods=['DELETE'])
@jwt_required()
def delete_fg(fg_id):
    identity     = get_jwt_identity()
    user_id      = identity['id']
    user         = User.query.get(user_id)
    farmer_group = FarmerGroup.query.get_or_404(fg_id)

    if not user.is_admin and farmer_group.created_by != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403

    db.session.delete(farmer_group)
    db.session.commit()
    return jsonify({'msg': 'Farmer Group deleted successfully'})