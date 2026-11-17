from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app.models import db, Farm, FarmData, FarmerGroup, Point, User

bp = Blueprint('api_farmergroup', __name__, url_prefix='/api/farmergroup')


def _serialize(fg, owners=None, farm_counts=None):
    data = {
        'id':           fg.id,
        'name':         fg.name,
        'description':  fg.description,
        'owner_id':     fg.created_by,
        'date_created': fg.date_created.isoformat() if fg.date_created else None,
        'date_updated': fg.date_updated.isoformat() if fg.date_updated else None,
    }
    if owners is not None:          # vue admin : compte propriétaire + nombre de fermes
        owner = owners.get(fg.created_by)
        data['owner_username'] = owner.username if owner else None
        data['farm_count'] = (farm_counts or {}).get(fg.id, 0)
    return data


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
        owner_ids = {g.created_by for g in groups if g.created_by}
        owners = {u.id: u for u in User.query.filter(User.id.in_(owner_ids))} if owner_ids else {}
        farm_counts = dict(db.session.query(Farm.farmergroup_id, func.count(Farm.id))
                           .group_by(Farm.farmergroup_id))
        return jsonify([_serialize(fg, owners, farm_counts) for fg in groups])

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

# ── ASSIGN farmer group to an account (admin) ─────────────────
# Le groupe ET ses fermes (avec leurs points GPS et données de saison)
# passent au compte choisi : c'est ce compte qui les voit ensuite.
# Les farm_id ne changent pas (leur préfixe reste celui du compte d'origine).
@bp.route('/<int:fg_id>/assign', methods=['PUT'])
@jwt_required()
def assign_fg(fg_id):
    identity = get_jwt_identity()
    admin    = User.query.get(identity['id'])
    if not admin or not admin.is_admin:
        return jsonify({'msg': 'Admin access required'}), 403

    farmer_group = FarmerGroup.query.get_or_404(fg_id)
    target = User.query.get((request.json or {}).get('user_id') or 0)
    if not target:
        return jsonify({'msg': 'Target account not found'}), 404

    farm_ids = [fid for (fid,) in db.session.query(Farm.farm_id).filter_by(farmergroup_id=fg_id)]
    farmer_group.created_by  = target.id
    farmer_group.modified_by = admin.id
    Farm.query.filter_by(farmergroup_id=fg_id).update(
        {'created_by': target.id, 'modified_by': admin.id}, synchronize_session=False)
    for i in range(0, len(farm_ids), 1000):
        chunk = farm_ids[i:i + 1000]
        FarmData.query.filter(FarmData.farm_id.in_(chunk)).update(
            {'created_by': target.id, 'modified_by': admin.id}, synchronize_session=False)
        Point.query.filter(Point.owner_type == 'farmer', Point.owner_id.in_(chunk)).update(
            {'created_by': target.id, 'modified_by': admin.id}, synchronize_session=False)
    db.session.commit()

    return jsonify({
        'msg': f'"{farmer_group.name}" and its {len(farm_ids)} farm(s) now belong to {target.username}',
        'farmer_group': _serialize(farmer_group, {target.id: target}, {fg_id: len(farm_ids)}),
    })
