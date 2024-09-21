
from flask import Blueprint, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Crop, Farm, FarmData, Forest, User
from app.routes.map import gfw
import logging
bp = Blueprint('api_gfw', __name__, url_prefix='/api/gfw')




@bp.route('/forests/<int:forest_id>/report', methods=['GET'])
def forestReport(forest_id):
    forest = Forest.query.filter_by(id=forest_id).first()
    if forest is None:
        return jsonify({"error": "Forest not found"}), 404

    forest_info = {
        'name': forest.name,
        'tree_type': forest.tree_type,
        'date_created': forest.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_updated': forest.date_updated.strftime('%Y-%m-%d %H:%M:%S'),
    }

    data, status_code = gfw(owner_type='forest', owner_id=str(forest_id))
    if status_code != 200:
        return jsonify(data), status_code

    return jsonify({
        "forest_info": forest_info,
        "report": data['dataset_results']
    }), 200


@bp.route('/farm/<string:farm_id>/report', methods=['GET'])
def farmerReport(farm_id):
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if farm is None:
        abort(404, description="Farm not found")
    
    farm_info = {
        'farm_id': farm.farm_id,
        'name': farm.name,
        'subcounty': farm.subcounty,
        'district_name': 'N/A',
        'district_region': 'N/A',
        'geolocation': farm.geolocation,
        'phonenumber': farm.phonenumber,
        'phonenumber2': farm.phonenumber2,
        'date_created': farm.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_updated': farm.date_updated.strftime('%Y-%m-%d %H:%M:%S'),
        'crops': [
            {
                'crop': Crop.query.get_or_404(data.crop_id).name,
                'land_type': data.land_type,
                'tilled_land_size': data.tilled_land_size,
                'planting_date': data.planting_date.strftime('%Y-%m-%d') if data.planting_date else 'N/A',
                'season': data.season,
                'quality': data.quality,
                'quantity': data.quantity,
                'harvest_date': data.harvest_date.strftime('%Y-%m-%d') if data.harvest_date else 'N/A',
                'expected_yield': data.expected_yield,
                'actual_yield': data.actual_yield,
                'timestamp': data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'channel_partner': data.channel_partner,
                'destination_country': data.destination_country,
                'customer_name': data.customer_name
            } for data in FarmData.query.filter_by(farm_id=farm_id).all()
        ]
    }
    
    data, status_code = gfw(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code
    
    return jsonify({
        "farm_info": farm_info,
        "report": data['dataset_results']
    }), 200
