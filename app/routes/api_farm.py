from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import District, Farm, FarmerGroup, ProduceCategory, User
from app.utils import farm_utils
import logging

bp = Blueprint('api_farm', __name__, url_prefix='/api/farm')

@bp.route('/')
@jwt_required()
def index():
    user_id = get_jwt_identity()  # Retrieve the user ID from the JWT token
    page = request.args.get('page', 1, type=int)
    
    user = User.query.get(user_id)
    if user.is_admin:
        farms = Farm.query.paginate(page=page, per_page=6)
    else:
        farms = Farm.query.filter_by(created_by=user_id).paginate(page=page, per_page=6)

    farms_list = [{
        "id": farm.farm_id,
        "name": farm.name,
        "subcounty": farm.subcounty,
        "district_id": farm.district_id,
        "farmergroup_id": farm.farmergroup_id,
        "geolocation": farm.geolocation,
        "phonenumber1": farm.phonenumber,
        "phonenumber2": farm.phonenumber2,
    } for farm in farms.items]
    print(farms_list)
    return jsonify(farms=farms_list)

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_farm():
    user_id = get_jwt_identity()
    data = request.json
    logging.info("Form data received: %s", data)
    
    farm_utils.create_farm(
        farm_id=data['farm_id'],
        name=data['name'],
        subcounty=data['subcounty'],
        farmergroup_id=data['farmergroup_id'],
        district_id=data['district_id'],
        geolocation=f"{data['latitude']},{data['longitude']}",
        phonenumber1=data.get('phonenumber1'),
        phonenumber2=data.get('phonenumber2')
    )
    
    return jsonify(success=True)

@bp.route('/<int:farm_id>/update', methods=['POST'])
@jwt_required()
def update_farm_route(farm_id):
    data = request.json
    farm_utils.update_farm(
        farm_id=farm_id,
        name=data['name'],
        subcounty=data['subcounty'],
        farmergroup_id=data['farmergroup_id'],
        district_id=data['district_id'],
        geolocation=data['geolocation'],
        phonenumber1=data['phonenumber'],
        phonenumber2=data.get('phonenumber2')
    )
    return jsonify(success=True)

@bp.route('/<int:farm_id>/delete', methods=['POST'])
@jwt_required()
def delete_farm(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    farm_utils.delete_farm(farm.id)
    return jsonify(success=True)

@bp.route('/boundaries/<region_name>/<farm_id>')
@jwt_required()
def generate_polygon_map_specific_region(region_name, farm_id):
    choropleth_map = generate_choropleth_map(region_name, farm_id)
    return jsonify(choropleth_map=choropleth_map)

@bp.route('/map/all_points')
@jwt_required()
def display_all_points():
    choropleth_map = generate_choropleth_map()
    return jsonify(choropleth_map=choropleth_map)