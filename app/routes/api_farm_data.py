from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.utils import farmdata_utils
from app.models import Farm, Crop, FarmData, User

# ALTER TABLE farmdata
# ADD COLUMN hs_code VARCHAR(10) NULL;

bp = Blueprint('api_farmdata', __name__, url_prefix='/api/farmdata')

@bp.route('/', methods=['GET'])
def index():
    farm_id = request.args.get('farm_id')
    
    if farm_id:
        farmdata_list = FarmData.query.filter_by(farm_id=farm_id).all()
    else:
        farmdata_list = FarmData.query.all()

    farmdata_json = [
        {
            'id': data.id,
            'farm_id': data.farm_id,
            'crop_id': data.crop_id,
            'land_type': data.land_type,
            'tilled_land_size': data.tilled_land_size,
            'planting_date': data.planting_date,
            'season': data.season,
            'quality': data.quality,
            'quantity': data.quantity,
            'harvest_date': data.harvest_date,
            'expected_yield': data.expected_yield,
            'actual_yield': data.actual_yield,
            'timestamp': data.timestamp,
            'channel_partner': data.channel_partner,
            'destination_country': data.destination_country,
            'customer_name': data.customer_name,
            'number_of_tree': data.number_of_tree,
            'hs_code': data.hs_code  # Include hs_code in the response
        } for data in farmdata_list
    ]
    
    return jsonify(farmdata_list=farmdata_json)

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_farmdata():
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id']
    user = User.query.get(user_id)

    data = request.json
    farm_id = data.get('farm_id')

    # Include hs_code in the data to be processed
    hs_code = data.get('hs_code')
    data['hs_code'] = hs_code  # Ensure hs_code is part of the data

    farmdata_utils.create_farmdata(data, user)
    return jsonify({"msg": "FarmData created successfully."}), 201

@bp.route('/<int:id>/edit', methods=['PUT'])
def edit_farmdata(id):
    farmdata = farmdata_utils.get_farmdata_by_id(id)
    data = request.json

    # Include hs_code in the updated data if provided
    if 'hs_code' in data:
        farmdata.hs_code = data['hs_code']

    farmdata_utils.update_farmdata(farmdata, data)
    return jsonify({"msg": "FarmData updated successfully."})

@bp.route('/<int:id>', methods=['GET'])
def get_farmdata(id):
    farmdata = farmdata_utils.get_farmdata_by_id(id)
    farmdata_json = {
        'id': farmdata.id,
        'farm_id': farmdata.farm_id,
        'crop_id': farmdata.crop_id,
        'land_type': farmdata.land_type,
        'tilled_land_size': farmdata.tilled_land_size,
        'planting_date': farmdata.planting_date,
        'season': farmdata.season,
        'quality': farmdata.quality,
        'quantity': farmdata.quantity,
        'harvest_date': farmdata.harvest_date,
        'expected_yield': farmdata.expected_yield,
        'actual_yield': farmdata.actual_yield,
        'timestamp': farmdata.timestamp,
        'channel_partner': farmdata.channel_partner,
        'destination_country': farmdata.destination_country,
        'customer_name': farmdata.customer_name,
        'number_of_tree': farmdata.number_of_tree,
        'hs_code': farmdata.hs_code,  # Include hs_code in the response
    }

    return jsonify(farmdata_json)

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_farmdata(id):
    farmdata = farmdata_utils.get_farmdata_by_id(id)
    farmdata_utils.delete_farmdata(farmdata)
    return jsonify({"msg": "FarmData deleted successfully."})

@bp.route('/count/total', methods=['GET'])
def count_total_farmdata():
    total = FarmData.query.count()
    return jsonify({
        'status': 'success',
        'total_farmdata': total
    })


@bp.route('/count/by-farm/<int:farm_id>', methods=['GET'])
def count_farmdata_by_farm(farm_id):
    count = FarmData.query.filter_by(farm_id=farm_id).count()
    return jsonify({
        'status': 'success',
        'farm_id': farm_id,
        'farmdata_count': count
    })
