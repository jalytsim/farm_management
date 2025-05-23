from flask import Blueprint, json, jsonify, request
from app.models import Crop, Farm, FarmData, Forest
from app.routes.map import gfw_async, gfw_async_carbon, gfw_async_from_geojson
bp = Blueprint('api_gfw', __name__, url_prefix='/api/gfw')




@bp.route('/forests/<int:forest_id>/report', methods=['GET'])
async def forestReport(forest_id):
    forest = Forest.query.filter_by(id=forest_id).first()
    if forest is None:
        return jsonify({"error": "Forest not found"}), 404

    forest_info = {
        'name': forest.name,
        'tree_type': forest.tree_type,
        'date_created': forest.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_updated': forest.date_updated.strftime('%Y-%m-%d %H:%M:%S'),
    }

    data, status_code = await gfw_async(owner_type='forest', owner_id=str(forest_id))
    if status_code != 200:
        return jsonify(data), status_code


    return jsonify({
        "forest_info": forest_info,
        "report": data['dataset_results']
    }), 200


@bp.route('/farm/<string:farm_id>/report', methods=['GET'])
async def farmerReport(farm_id):
    # Fetch farm information synchronously
    print(farm_id)
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if farm is None:
        return jsonify({"error": "Farm not found"}), 404

    # Create farm info dictionary
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
        'crops': []
    }

    # Fetch crops data synchronously
    crops_data = FarmData.query.filter_by(farm_id=farm_id).all()

    # Populate crops information
    for data in crops_data:
        crop_name = Crop.query.get(data.crop_id).name if data.crop_id else 'N/A'
        farm_info['crops'].append({
            'crop': crop_name,
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
        })

    # Fetch additional data asynchronously
    data, status_code = await gfw_async(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code

    # ✅ Regrouper les résultats par dataset
    report_by_dataset = {}
    for item in data['dataset_results']:
        dataset = item['dataset']
        if dataset not in report_by_dataset:
            report_by_dataset[dataset] = []
        report_by_dataset[dataset].append({
            "pixel": item["pixel"],
            "data_fields": item["data_fields"],
            "coordinates": item["coordinates"]
        })
    return jsonify({
    "farm_info": farm_info,
    "report": report_by_dataset  # <-- format dict au lieu de liste
}), 200



@bp.route('/farm/<string:farm_id>/CarbonReport', methods=['GET'])
async def CarbonReport(farm_id):
    # Fetch farm information synchronously
    print(farm_id)
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if farm is None:
        return jsonify({"error": "Farm not found"}), 404

    # Create farm info dictionary
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
        'crops': []
    }

    # Fetch crops data synchronously
    crops_data = FarmData.query.filter_by(farm_id=farm_id).all()

    # Populate crops information
    for data in crops_data:
        crop_name = Crop.query.get(data.crop_id).name if data.crop_id else 'N/A'
        farm_info['crops'].append({
            'crop': crop_name,
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
        })

    # Fetch additional data asynchronously
    data, status_code = await gfw_async_carbon(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code
    print(farm_info)
    return jsonify({
        "farm_info": farm_info,
        "report": data['dataset_results']
    }), 200


@bp.route('/forest/<string:forest_id>/CarbonReport', methods=['GET'])
async def CarbonReportforest(forest_id):
    # Fetch farm information synchronously
    forest = Forest.query.filter_by(id=forest_id).first()
    if forest is None:
        return jsonify({"error": "Forest not found"}), 404

    # Create farm info dictionary
    forest_info = {
        'name': forest.name,
        'tree_type': forest.tree_type,
        'date_created': forest.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_updated': forest.date_updated.strftime('%Y-%m-%d %H:%M:%S'),
    }


    
    # Fetch additional data asynchronously
    data, status_code = await gfw_async_carbon(owner_type='forest', owner_id=forest_id)
    if status_code != 200:
        return jsonify(data), status_code
    print(forest_info)
    return jsonify({
        "forest_info": forest_info,
        "report": data['dataset_results']
    }), 200
    
    
@bp.route('/Geojson/ReportFromFile', methods=['POST'])
async def carbon_report_from_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    try:
        geojson_data = json.load(file)
    except Exception as e:
        return jsonify({'error': f'Invalid GeoJSON file: {str(e)}'}), 400

    # Appel de la fonction asynchrone avec le GeoJSON
    report, status_code = await gfw_async_from_geojson(geojson_data)
    return jsonify(report), status_code