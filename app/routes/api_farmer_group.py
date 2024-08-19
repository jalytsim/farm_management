from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import db, FarmerGroup
from app.routes.farm import farmer_or_admin_required

bp = Blueprint('api_farmergroup', __name__, url_prefix='/api/farmergroup')

@bp.route('/', methods=['GET'])
def index():
    farmer_groups = FarmerGroup.query.all()
    farmer_groups_json = [
        {
            'id': fg.id,
            'name': fg.name,
            'description': fg.description,
            'date_created': fg.date_created,
            'date_updated': fg.date_updated
        } for fg in farmer_groups
    ]
    return jsonify(farmer_groups_json)

@bp.route('/create', methods=['POST'])
def create_fg():
    data = request.json
    name = data.get('name')
    description = data.get('description')

    new_fg = FarmerGroup(name=name, description=description)
    db.session.add(new_fg)
    db.session.commit()

    return jsonify({'msg': 'Farmer Group created successfully', 'farmer_group': {
        'id': new_fg.id,
        'name': new_fg.name,
        'description': new_fg.description,
        'date_created': new_fg.date_created,
        'date_updated': new_fg.date_updated
    }}), 201

@bp.route('/<int:fg_id>', methods=['PUT'])
def edit_fg(fg_id):
    farmer_group = FarmerGroup.query.get_or_404(fg_id)

    data = request.json
    farmer_group.name = data.get('name')
    farmer_group.description = data.get('description')

    db.session.commit()

    return jsonify({'msg': 'Farmer Group updated successfully', 'farmer_group': {
        'id': farmer_group.id,
        'name': farmer_group.name,
        'description': farmer_group.description,
        'date_created': farmer_group.date_created,
        'date_updated': farmer_group.date_updated
    }})

@bp.route('/<int:fg_id>', methods=['DELETE'])
def delete_fg(fg_id):
    farmer_group = FarmerGroup.query.get_or_404(fg_id)

    db.session.delete(farmer_group)
    db.session.commit()

    return jsonify({'msg': 'Farmer Group deleted successfully'})
