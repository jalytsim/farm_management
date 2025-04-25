# routes/crop_routes.py
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.routes.admin import admin_required
from app.routes.farm import farmer_or_admin_required
from app.utils.district_utils import create_district, delete_district, get_all_districts, get_district_by_id, update_district

bp = Blueprint('api_district', __name__, url_prefix='/api/district')
@bp.route('/', methods=['GET'])
def api_list_districts():
    districts = get_all_districts()
    districts_list = [{"id": district.id, "name": district.name, "region": district.region} for district in districts]
    return jsonify(districts=districts_list)

@bp.route('/<int:district_id>', methods=['GET'])
def api_view_district(district_id):
    district = get_district_by_id(district_id)
    if district:
        return jsonify({"id": district.id, "name": district.name, "region": district.region})
    else:
        return jsonify({"msg": "District not found"}), 404

@bp.route('/', methods=['POST'])
def api_create_district_route():
    data = request.json
    name = data.get('name')
    region = data.get('region')
    create_district(name, region)
    return jsonify({"msg": "District created successfully"}), 201

@bp.route('/<int:district_id>', methods=['PUT'])
def api_dit_district_route(district_id):
    data = request.json
    name = data.get('name')
    region = data.get('region')
    updated = update_district(district_id, name, region)
    if updated:
        return jsonify({"msg": "District updated successfully"})
    else:
        return jsonify({"msg": "District not found"}), 404

@bp.route('/<int:district_id>', methods=['DELETE'])
def api_delete_district_route(district_id):
    deleted = delete_district(district_id)
    if deleted:
        return jsonify({"msg": "District deleted successfully"})
    else:
        return jsonify({"msg": "District not found"}), 404
    
@bp.route('/count/by-region/<string:region>', methods=['GET'])
def api_count_districts_by_region(region):
    districts = get_all_districts()
    filtered = [d for d in districts if d.region.lower() == region.lower()]
    return jsonify({
        'status': 'success',
        'region': region,
        'district_count': len(filtered)
    })


@bp.route('/count/total', methods=['GET'])
def api_count_all_districts():
    districts = get_all_districts()
    total = len(districts)
    return jsonify({
        'status': 'success',
        'total_districts': total
    })
