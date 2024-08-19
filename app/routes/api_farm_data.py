from flask import Blueprint, jsonify, request
from app.utils import farmdata_utils
from app.models import Farm, Crop, FarmData

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
            'customer_name': data.customer_name
        } for data in farmdata_list
    ]
    
    return jsonify(farmdata_list=farmdata_json)

@bp.route('/create', methods=['POST'])
def create_farmdata():
    data = request.json
    farm_id = data.get('farm_id')

    farmdata_utils.create_farmdata(data)
    return jsonify({"msg": "FarmData created successfully."}), 201

@bp.route('/<int:id>/edit', methods=['PUT'])
def edit_farmdata(id):
    farmdata = farmdata_utils.get_farmdata_by_id(id)
    data = request.json

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
        'customer_name': farmdata.customer_name
    }

    return jsonify(farmdata_json)

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_farmdata(id):
    farmdata = farmdata_utils.get_farmdata_by_id(id)
    farmdata_utils.delete_farmdata(farmdata)
    return jsonify({"msg": "FarmData deleted successfully."})
