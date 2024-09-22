from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Farm, User
from app.utils import farm_utils
import logging

bp = Blueprint('api_farm', __name__, url_prefix='/api/farm')

@bp.route('/')
@jwt_required()
def index():
    # Retrieve the user identity (which is a dictionary)
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id']  # Extract the 'id' from the identity dictionary

    # Pagination
    page = request.args.get('page', 1, type=int)
    
    # Query the user from the database
    user = User.query.get(user_id)

    # Check if user is an admin or not
    if user.is_admin:
        farms = Farm.query.paginate(page=page, per_page=6)
    else:
        farms = Farm.query.filter_by(created_by=user_id).paginate(page=page, per_page=6)

    # Format the farm data
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
    
    # Return the response as JSON
    return jsonify(
        farms=farms_list,
        total_pages=farms.pages,  # Return the total number of pages
        current_page=farms.page,  # Return the current page
    )

@bp.route('/create', methods=['POST'])
@jwt_required()
@cross_origin()
def create_farm():
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id'] 
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

@bp.route('/<farm_id>', methods=['GET'])
@jwt_required()
def get_farm_by_id(farm_id):
    farm = Farm.query.filter_by(farm_id=farm_id).first_or_404()

    farm_data = {
        "id": farm.farm_id,
        "name": farm.name,
        "subcounty": farm.subcounty,
        "district_id": farm.district_id,
        "farmergroup_id": farm.farmergroup_id,
        "geolocation": farm.geolocation,
        "phonenumber1": farm.phonenumber,
        "phonenumber2": farm.phonenumber2,
    }

    return jsonify(farm=farm_data)

@bp.route('/<farm_id>/allprop', methods=['GET'])
def get_farm_props(farm_id):
    # Retrieve farm properties using the utility function
    data = farm_utils.get_all_farm_properties(farm_id)

    # Check if data is found
    if data:
        # Manually construct the list of dictionaries
        result = []
        for row in data:
            result.append({
                'farm_id': row[0],
                'farm_name': row[1],
                'subcounty': row[2],
                'geolocation': row[3],
                'farmergroup_name': row[4],
                'district_name': row[5],
                'district_region': row[6],
                'crop_name': row[7],
                'tilled_land_size': row[8],
                'land_type': row[9],
                'planting_date': row[10].isoformat() if row[10] else None,
                'season': row[11],
                'quality': row[12],
                'produce_weight': row[13],
                'harvest_date': row[14].isoformat() if row[14] else None,
                'expected_yield': row[15],
                'actual_yield': row[16],
                'timestamp': row[17].isoformat() if row[17] else None,
                'channel_partner': row[18],
                'destination_country': row[19],
                'customer_name': row[20],
            })

        # Return the data as JSON
        return jsonify({
            'status': 'success',
            'data': result
        })
    else:
        # Return an error message if no data is found
        return jsonify({
            'status': 'error',
            'message': 'No data found for the provided farm ID'
        }), 404
