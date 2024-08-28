from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import District, Farm, FarmerGroup, ProduceCategory, User
from app.utils import farm_utils
import logging

bp = Blueprint('api_farm', __name__, url_prefix='/api/farm')

@bp.route('/')
@jwt_required()
@cross_origin()
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
        'geolocation': farm.geolocation,
        "phonenumber1": farm.phonenumber,
        "phonenumber2": farm.phonenumber2,
    } for farm in farms.items]
    
    return jsonify(
        farms=farms_list,
        total_pages=farms.pages,  # Return the total number of pages
        current_page=farms.page,  # Return the current page
    )

@bp.route('/create', methods=['POST'])
@jwt_required()
@cross_origin()
def create_farm():
    user_id = get_jwt_identity()
    print(user_id)
    user = User.query.get(user_id)
    
    if not user or not user.id_start:
        return jsonify({"msg": "User id_start is not defined"}), 400
    
    data = request.json
    logging.info("Form data received: %s", data)
    
    try:
        new_farm = farm_utils.create_farm(
            user=user,
            name=data['name'],
            subcounty=data['subcounty'],
            farmergroup_id=data['farmergroup_id'],
            district_id=data['district_id'],
            geolocation=f"{data['latitude']},{data['longitude']}",
            phonenumber1=data.get('phonenumber1'),
            phonenumber2=data.get('phonenumber2')
        )
        return jsonify(success=True, farm_id=new_farm.farm_id)
    except Exception as e:
        logging.error(f"Error creating farm: {e}")
        return jsonify({"msg": "Error creating farm"}), 500

@bp.route('/<farm_id>/update', methods=['POST'])
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

@bp.route('/<farm_id>/delete', methods=['POST'])
@jwt_required()
def delete_farm(farm_id):
    farmId = farm_utils.getId(farm_id)
    print(farmId)
    print(farm_id)
    farm = Farm.query.get_or_404(farmId)
    print(farm.id)
    farm_utils.delete_farm(farm.id)
    return jsonify(success=True)

