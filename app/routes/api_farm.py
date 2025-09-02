from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Farm, User
from app.utils import farm_utils
import logging
from datetime import datetime, date
import datetime


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
    print( "+++++++++===========+++++++++",user_id,)

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
        "gender": farm.gender,
        "cin": farm.cin,
    } for farm in farms.items]
    
    # Return the response as JSON
    return jsonify(
        farms=farms_list,
        total_pages=farms.pages,  # Return the total number of pages
        current_page=farms.page,  # Return the current page
    )

@bp.route('/all')
@jwt_required()
def all():
    # Retrieve the user identity (which is a dictionary)
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id']  # Extract the 'id' from the identity dictionary

    # Query the user from the database
    user = User.query.get(user_id)
    print("+++++++++===========+++++++++", user_id)

    # Check if user is an admin or not
    if user.is_admin:
        farms = Farm.query.all()  # Retrieve all farms
    else:
        farms = Farm.query.filter_by(created_by=user_id).all()  # Retrieve farms created by the user

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
        "gender": farm.gender,
        "cin": farm.cin,
    } for farm in farms]

    # Return the response as JSON
    return jsonify(
        farms=farms_list,
        total_farms=len(farms_list),  # Return the total number of farms
    )

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_farm():
    identity = get_jwt_identity()
    user_id = identity['id']
    
    user = User.query.get(user_id)
    
    if not user or not user.id_start:
        return jsonify({"msg": "User id_start is not defined"}), 400
    
    data = request.json
    logging.info("Form data received: %s", data)

    try:
        geolocation = data['geolocation']
        if not geolocation:
            return jsonify({"msg": "Geolocation is required"}), 400
        
        # Check if farm already exists based on unique constraints
        existing_farm = Farm.query.filter_by(
            name=data['name'],
            district_id=data['district_id'],
            geolocation=geolocation,
            cin=data['cin'],
        ).first()

        if existing_farm:
            return jsonify({"msg": "Farm already exists", "farm_id": existing_farm.farm_id}), 409  # 409 Conflict
        
        # Call utility to create farm
        new_farm = farm_utils.create_farm(
            user=user,
            name=data['name'],
            subcounty=data['subcounty'],
            farmergroup_id=data['farmergroup_id'],
            district_id=data['district_id'],
            geolocation=geolocation,
            phonenumber1=data.get('phonenumber1'),
            phonenumber2=data.get('phonenumber2', ''),
            gender=data['gender'], 
            cin=data['cin'],
        )

        return jsonify({"success": True, "farm_id": new_farm.farm_id}), 201

    except Exception as e:
        logging.error(f"Error creating farm: {e}")
        return jsonify({"msg": "Error creating farm", "error": str(e)}), 500

@bp.route('/bulk_create', methods=['POST'])
@jwt_required()
def bulk_create_farms():
    identity = get_jwt_identity()
    user_id = identity['id']
    
    user = User.query.get(user_id)
    
    if not user or not user.id_start:
        return jsonify({"msg": "User id_start is not defined"}), 400
    
    data = request.json
    logging.info("Bulk form data received: %s", data)
    
    if not data:
        return jsonify({"msg": "Invalid data format. Expected a list of farm entries."}), 400

    created_farms = []
    existing_farms = []

    try:
        for entry in data:
            if 'geolocation' not in entry or not entry['geolocation']:
                return jsonify({"msg": "Geolocation is required for all farm entries"}), 400

            # Check if farm already exists
            existing_farm = Farm.query.filter_by(
                name=entry['name'],
                district_id=entry['district_id'],
                geolocation=entry['geolocation'],
                gender=entry['gender'],
                cin=entry['cin'],
            ).first()

            print(entry)

            if existing_farm:
                existing_farms.append({"name": entry['name'], "farm_id": existing_farm.farm_id})
                continue  # Skip duplicate entries

            # Create new farm
            new_farm = farm_utils.create_farm(
                user=user,
                name=entry['name'],
                subcounty=entry['subcounty'],
                farmergroup_id=entry['farmergroup_id'],
                district_id=entry['district_id'],
                geolocation=entry['geolocation'],
                phonenumber1=entry.get('phonenumber1'),
                phonenumber2=entry.get('phonenumber2', ''),
                gender=entry['gender'],
                cin=entry['cin'],
            )

            created_farms.append(new_farm.farm_id)

        return jsonify({"success": True, "created_farms": created_farms, "existing_farms": existing_farms}), 201

    except Exception as e:
        logging.error(f"Error creating farms: {e}")
        return jsonify({"msg": "Error creating farms", "error": str(e)}), 500


@bp.route('/<farm_id>/update', methods=['POST'])
@jwt_required()
def update_farm_route(farm_id):
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id']
    
    user = User.query.get(user_id)
    data = request.json
    farm_utils.update_farm(
        farm_id=farm_id,
        name=data['name'],
        subcounty=data['subcounty'],
        farmergroup_id=data['farmergroup_id'],
        district_id=data['district_id'],
        geolocation=data['geolocation'],
        phonenumber1=data['phonenumber1'],
        phonenumber2=data.get('phonenumber2'),
        gender=data['gender'],
        cin=data['cin'],
        user=user
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
    if farm :
        farm_data = {
            "id": farm.farm_id,
            "name": farm.name,
            "subcounty": farm.subcounty,
            "district_id": farm.district_id,
            "farmergroup_id": farm.farmergroup_id,
            "geolocation": farm.geolocation,
            "phonenumber1": farm.phonenumber,
            "phonenumber2": farm.phonenumber2,
            "gender": farm.gender,
            "cin":farm.cin,

        }
        return jsonify({
            'status': 'success',
            'data': farm_data
            })
    else:
        # Return an error message if no data is found
        return jsonify({
            'status': 'error',
            'message': 'No data found for the provided farm ID'
        }), 404
    

@bp.route('/<farm_id>/allprop', methods=['GET'])
def get_farm_props(farm_id):
    data = farm_utils.get_all_farm_properties(farm_id)

    if data:
        result = []
        for row in data:
            result.append({
                'farm_id': row[0],
                'farm_name': row[1],
                'subcounty': row[2],
                'geolocation': row[3],
                'farmergroup_name': row[4],
                'district_name': row[6],
                'district_region': row[6],
                'crop_name': row[7],
                'tilled_land_size': row[8],
                'land_type': row[9],
                'planting_date': row[10] if row[10] else None,
                'season': row[11],
                'quality': row[12],
                'produce_weight': row[13],
                'harvest_date': row[14] if row[14] else None,
                'expected_yield': row[15],
                'actual_yield': row[16],
                'timestamp': row[17].isoformat() if isinstance(row[17], (datetime.datetime, datetime.date)) else row[17],
                'channel_partner': row[18],
                'destination_country': row[19],
                'customer_name': row[20],
            })
        return jsonify({'status': 'success', 'data': result})
    else:
        return jsonify({'status': 'error', 'message': 'No data found for the provided farm ID'}), 404


@bp.route('/count/total', methods=['GET'])
@jwt_required()
def count_total_farms():
    total = Farm.query.count()
    return jsonify({
        'status': 'success',
        'total_farms': total
    })


@bp.route('/count/by-user', methods=['GET'])
@jwt_required()
def count_farms_by_user():
    identity = get_jwt_identity()
    user_id = identity['id']
    
    count = Farm.query.filter_by(created_by=user_id).count()
    return jsonify({
        'status': 'success',
        'user_id': user_id,
        'farm_count': count
    })

@bp.route('/count/by-month', methods=['GET'])
@jwt_required()
def api_count_farms_by_month():
    year = request.args.get('year', type=int)
    district_id = request.args.get('district_id', type=int)
    farmergroup_id = request.args.get('farmergroup_id', type=int)
    created_by = request.args.get('created_by', type=int)

    monthly_counts = farm_utils.count_farms_by_month(
        year=year,
        district_id=district_id,
        farmergroup_id=farmergroup_id,
        created_by=created_by
    )

    return jsonify({
        "status": "success",
        "year": year or datetime.utcnow().year,
        "filters_applied": {
            "district_id": district_id,
            "farmergroup_id": farmergroup_id,
            "created_by": created_by
        },
        "monthly_counts": monthly_counts
    })
