from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from alertspest import fetch_weather_data, detect_gdd_and_pest_alerts
from alerts import detect_anomalies

# IMPORTS MANQUANTS - AJOUTE CES LIGNES ⚠️
from app import db  # Import de l'instance SQLAlchemy
from sqlalchemy import func, case  # Import des fonctions SQLAlchemy

from app.models import Farm, User, FarmReport, District, FarmerGroup  # Ajoute FarmReport, District, FarmerGroup
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
@bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    from alertspest import fetch_weather_data, detect_gdd_and_pest_alerts
    from alerts import detect_anomalies

    farms = Farm.query.all()
    results = []

    for farm in farms:
        try:
            # Vérification géolocalisation
            if not farm.geolocation or ',' not in farm.geolocation:
                raise ValueError("Invalid geolocation format")

            parts = farm.geolocation.split(',')
            if len(parts) != 2:
                raise ValueError("Geolocation must contain exactly 2 parts")

            lat, lon = map(float, parts)
            print(f"[INFO] Processing farm: {farm.name} at ({lat}, {lon})")

            # Récupération des données météo
            weather_data = fetch_weather_data(lat, lon)

            # Vérification que les données sont bien une liste avec du contenu
            if not weather_data or not isinstance(weather_data, list):
                raise ValueError(f"Empty or invalid weather data for farm '{farm.name}'")

            # Affiche un aperçu des 3 premières données pour déboguer
            print(f"[DEBUG] {farm.name} weather data sample:", weather_data[:3])

            # Détection des alertes
            weather_alerts = detect_anomalies(weather_data)
            pest_alerts = detect_gdd_and_pest_alerts(weather_data)

            # Ajout au résultat
            results.append({
                "farm": {
                    "id": farm.farm_id,
                    "name": farm.name,
                    "geolocation": farm.geolocation,
                    "phonenumber": farm.phonenumber,
                },
                "weather_alerts": weather_alerts,
                "pest_alerts": pest_alerts
            })

        except ValueError as ve:
            print(f"[WARNING] {farm.name}: {ve}")
        except IndexError as ie:
            print(f"[ERROR] Index error with farm {farm.name}: {ie}")
        except Exception as e:
            print(f"[ERROR] Problem with farm {farm.name}: {e}")

    print("[DEBUG] Final results:", results)
    return jsonify(results)

# À ajouter dans api_farm.py

from sqlalchemy import func, case
from app.models import Farm, FarmReport, User, District, FarmerGroup

# Voici les modifications à apporter dans api_farm.py

# 1. Dans la route /stats/by-user - MODIFIER la requête principale (ligne ~290)
@bp.route('/stats/by-user', methods=['GET'])
@jwt_required()
def get_user_farm_statistics():
    """
    Statistiques des fermes par utilisateur (inclut comptage Compliance corrigé)
    """
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)

    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    # Déterminer si admin visualise plusieurs comptes ou un compte
    target_user_id = None
    if user.is_admin:
        if request.args.get('all_users') == 'true':
            target_user_id = None
        elif request.args.get('user_id'):
            target_user_id = int(request.args.get('user_id'))
        else:
            target_user_id = user_id
    else:
        target_user_id = user_id

    # ✅ Normalisation Compliance (supprime espaces et met tout en minuscule)
    normalized = func.replace(func.lower(FarmReport.eudr_compliance_assessment), ' ', '')

    query = db.session.query(
        User.id.label('user_id'),
        User.username.label('username'),
        User.email.label('email'),
        User.company_name.label('company_name'),
        User.user_type.label('user_type'),
        User.id_start.label('id_start'),
        func.count(Farm.id).label('total_farms'),

        # ✅ Comparaison inline (évitant la perte de contexte SQL)
        func.sum(
            case(
                (func.replace(func.lower(FarmReport.eudr_compliance_assessment), ' ', '') == '100%compliant', 1),
                else_=0
            )
        ).label('compliant_count'),

        func.sum(
            case(
                (func.replace(func.lower(FarmReport.eudr_compliance_assessment), ' ', '') == 'likelycompliant', 1),
                else_=0
            )
        ).label('likely_compliant_count'),

        func.sum(
            case(
                (func.replace(func.lower(FarmReport.eudr_compliance_assessment), ' ', '') == 'notcompliant', 1),
                else_=0
            )
        ).label('not_compliant_count'),

        func.sum(case((FarmReport.id.is_(None), 1), else_=0)).label('no_report_count'),

        func.sum(
            case(
                (FarmReport.project_area.isnot(None),
                func.cast(func.replace(FarmReport.project_area, ',', ''), db.Float)),
                else_=0
            )
        ).label('total_project_area'),

        func.sum(
            case(
                (FarmReport.tree_cover_loss.isnot(None),
                func.cast(func.replace(FarmReport.tree_cover_loss, ',', ''), db.Float)),
                else_=0
            )
        ).label('total_tree_cover_loss')
    ).select_from(User) \
    .join(Farm, Farm.created_by == User.id) \
    .outerjoin(FarmReport, FarmReport.farm_id == Farm.id)

    if target_user_id:
        query = query.filter(User.id == target_user_id)

    query = query.group_by(User.id, User.username, User.email, User.company_name, User.user_type)
    results = query.all()
    print("ato indray ny result", results)

    statistics = []
    for result in results:
        total_farms = result.total_farms or 0
        total_area = float(result.total_project_area or 0)

        statistics.append({
            'user_id': result.user_id,
            'username': result.username,
            'email': result.email,
            'company_name': result.company_name,
            'user_type': result.user_type,
            'id_start': result.id_start,
            'total_farms': total_farms,

            'compliance_status': {
                'compliant_100': result.compliant_count or 0,
                'not_compliant': result.not_compliant_count or 0,
                'likely_compliant': result.likely_compliant_count or 0,
                'no_report': result.no_report_count or 0
            },

            'environmental_metrics': {
                'total_project_area': round(total_area, 2),
                'total_tree_cover_loss': round(result.total_tree_cover_loss or 0, 2),
                'average_project_area_per_farm': round(total_area / total_farms, 2) if total_farms > 0 else 0,
                'average_tree_cover_loss_per_farm': round((result.total_tree_cover_loss or 0) / total_farms, 2) if total_farms > 0 else 0
            }
        })

    return jsonify({
        'status': 'success',
        'data': statistics,
        'total_users': len(statistics)
    })


# 2. Dans la route /stats/by-user/<int:target_user_id> - AJOUTER company_name (ligne ~435)
@bp.route('/stats/by-user/<int:target_user_id>', methods=['GET'])
@jwt_required()
def get_specific_user_farm_statistics(target_user_id):
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)

    if not user.is_admin and user_id != target_user_id:
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized: You can only access your own statistics'
        }), 403

    target_user = User.query.get_or_404(target_user_id)
    farms = Farm.query.filter_by(created_by=target_user_id).all()

    # ✅ Normalisation Compliance
    def normalize(val):
        if not val: return None
        return val.replace(" ", "").lower()

    result = {
        'user_id': target_user.id,
        'username': target_user.username,
        'email': target_user.email,
        'company_name': target_user.company_name,
        'user_type': target_user.user_type,
        'id_start': target_user.id_start,
        'total_farms': len(farms),
        'farms_detail': [],
        'compliance_status': {
            'compliant_100': 0,
            'not_compliant': 0,
            'likely_compliant': 0,
            'no_report': 0
        },
        'environmental_metrics': {
            'total_project_area': 0,
            'total_tree_cover_loss': 0
        }
    }

    for farm in farms:
        report = FarmReport.query.filter_by(farm_id=farm.id).first()
        status = normalize(report.eudr_compliance_assessment) if report else None
        print("status ao amn by user/id",status)

        if status == '100%compliant':
            result['compliance_status']['compliant_100'] += 1
        elif status == 'likelycompliant':
            result['compliance_status']['likely_compliant'] += 1
        elif status == 'notcompliant':
            result['compliance_status']['not_compliant'] += 1
        else:
            result['compliance_status']['no_report'] += 1

        # Aires
        if report and report.project_area:
            result['environmental_metrics']['total_project_area'] += float(str(report.project_area).replace(',', ''))

        if report and report.tree_cover_loss:
            result['environmental_metrics']['total_tree_cover_loss'] += float(str(report.tree_cover_loss).replace(',', ''))

    total_area = result['environmental_metrics']['total_project_area']
    result['environmental_metrics']['total_project_area'] = round(total_area, 2)
    result['environmental_metrics']['total_tree_cover_loss'] = round(result['environmental_metrics']['total_tree_cover_loss'], 2)

    return jsonify({'status': 'success', 'data': result})


# 3. Dans la route /stats/comparison - AJOUTER company_name (ligne ~740)
@bp.route('/stats/comparison', methods=['GET'])
@jwt_required()
def get_user_comparison():
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)

    if not user.is_admin:
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403

    user_ids_str = request.args.get('user_ids', '')
    user_ids = [int(uid.strip()) for uid in user_ids_str.split(',')]

    comparison = []

    def normalize(val):
        if not val: return None
        return val.replace(" ", "").lower()

    for uid in user_ids:
        target = User.query.get(uid)
        if not target: continue

        farms = Farm.query.filter_by(created_by=uid).all()

        stats = {
            'user_id': uid,
            'username': target.username,
            'company_name': target.company_name,
            'total_farms': len(farms),
            'compliant_100': 0,
            'not_compliant': 0,
            'likely_compliant': 0,
            'no_report': 0,
            'total_project_area': 0,
            'total_tree_cover_loss': 0
        }

        for farm in farms:
            report = FarmReport.query.filter_by(farm_id=farm.id).first()
            status = normalize(report.eudr_compliance_assessment) if report else None
            print(status)

            if status == '100%compliant':
                stats['compliant_100'] += 1
            elif status == 'likelycompliant':
                stats['likely_compliant'] += 1
            elif status == 'notcompliant':
                stats['not_compliant'] += 1
            else:
                stats['no_report'] += 1

            if report and report.project_area:
                stats['total_project_area'] += float(str(report.project_area).replace(',', ''))

            if report and report.tree_cover_loss:
                stats['total_tree_cover_loss'] += float(str(report.tree_cover_loss).replace(',', ''))

        stats['total_project_area'] = round(stats['total_project_area'], 2)
        stats['total_tree_cover_loss'] = round(stats['total_tree_cover_loss'], 2)

        comparison.append(stats)

    return jsonify({'status': 'success', 'data': comparison})


@bp.route('/stats/summary', methods=['GET'])
@jwt_required()
def get_global_summary():
    """
    Retourne un résumé global de toutes les statistiques
    avec comptage compliance corrigé (normalisation des valeurs).
    """
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)
    
    # Base query
    query = Farm.query
    
    # Admin → vue globale si demandé
    if not (user.is_admin and request.args.get('global') == 'true'):
        query = query.filter_by(created_by=user_id)
    
    # Filtres optionnels
    district_id = request.args.get('district_id', type=int)
    if district_id:
        query = query.filter_by(district_id=district_id)
    
    farmergroup_id = request.args.get('farmergroup_id', type=int)
    if farmergroup_id:
        query = query.filter_by(farmergroup_id=farmergroup_id)
    
    year = request.args.get('year', type=int)
    if year:
        query = query.filter(func.extract('year', Farm.date_created) == year)
    
    farms = query.all()

    # Structure initiale
    summary = {
        'total_farms': len(farms),
        'total_users': User.query.count() if user.is_admin else 1,
        'filters_applied': {
            'district_id': district_id,
            'farmergroup_id': farmergroup_id,
            'year': year
        },
        'compliance_summary': {
            'compliant_100': 0,
            'likely_compliant': 0,
            'not_compliant': 0,
            'no_report': 0
        },
        'environmental_summary': {
            'total_project_area': 0,
            'total_tree_cover_loss': 0,
            'average_project_area': 0,
            'average_tree_cover_loss': 0
        },
        'by_district': {},
        'by_farmer_group': {}
    }

    project_areas = []
    tree_cover_losses = []

    # ✅ Normalisation utilitaire
    def normalize(val):
        if not val:
            return None
        return val.replace(" ", "").lower()

    for farm in farms:
        report = FarmReport.query.filter_by(farm_id=farm.id).first()

        # District
        district = District.query.get(farm.district_id) if farm.district_id else None
        if district:
            d = summary['by_district'].setdefault(district.name, {'total_farms': 0, 'compliant_100': 0, 'likely_compliant': 0, 'not_compliant': 0})
            d['total_farms'] += 1

        # Farmer group
        farmer_group = FarmerGroup.query.get(farm.farmergroup_id) if farm.farmergroup_id else None
        if farmer_group:
            g = summary['by_farmer_group'].setdefault(farmer_group.name, {'total_farms': 0, 'compliant_100': 0, 'likely_compliant': 0, 'not_compliant': 0})
            g['total_farms'] += 1

        if report:
            status = normalize(report.eudr_compliance_assessment)

            if status == '100%compliant':
                summary['compliance_summary']['compliant_100'] += 1
                if district: summary['by_district'][district.name]['compliant_100'] += 1
                if farmer_group: summary['by_farmer_group'][farmer_group.name]['compliant_100'] += 1

            elif status == 'likelycompliant':
                summary['compliance_summary']['likely_compliant'] += 1
                if district: summary['by_district'][district.name]['likely_compliant'] += 1
                if farmer_group: summary['by_farmer_group'][farmer_group.name]['likely_compliant'] += 1

            elif status == 'notcompliant':
                summary['compliance_summary']['not_compliant'] += 1
                if district: summary['by_district'][district.name]['not_compliant'] += 1
                if farmer_group: summary['by_farmer_group'][farmer_group.name]['not_compliant'] += 1

            else:
                summary['compliance_summary']['no_report'] += 1

            # Aires
            try:
                if report.project_area:
                    area = float(str(report.project_area).replace(',', ''))
                    summary['environmental_summary']['total_project_area'] += area
                    project_areas.append(area)
            except: pass

            try:
                if report.tree_cover_loss:
                    loss = float(str(report.tree_cover_loss).replace(',', ''))
                    summary['environmental_summary']['total_tree_cover_loss'] += loss
                    tree_cover_losses.append(loss)
            except: pass

        else:
            summary['compliance_summary']['no_report'] += 1

    # Moyennes
    if project_areas:
        summary['environmental_summary']['average_project_area'] = round(sum(project_areas) / len(project_areas), 2)
    if tree_cover_losses:
        summary['environmental_summary']['average_tree_cover_loss'] = round(sum(tree_cover_losses) / len(tree_cover_losses), 2)

    # Arrondir totaux
    summary['environmental_summary']['total_project_area'] = round(summary['environmental_summary']['total_project_area'], 2)
    summary['environmental_summary']['total_tree_cover_loss'] = round(summary['environmental_summary']['total_tree_cover_loss'], 2)

    return jsonify({'status': 'success', 'data': summary})


@bp.route('/area/by-compliance', methods=['GET'])
@jwt_required()
def get_area_by_compliance():
    """
    Retourne la somme totale de project_area ET tree_cover_loss 
    groupée par eudr_compliance_assessment.
    """
    identity = get_jwt_identity()
    user_id = identity['id']

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    # Si admin → toutes les fermes, sinon seulement ses fermes
    query = db.session.query(
        FarmReport.eudr_compliance_assessment.label('compliance_status'),
        func.sum(
            case(
                (FarmReport.project_area.isnot(None),
                 func.cast(func.replace(FarmReport.project_area, ',', ''), db.Float)),
                else_=0
            )
        ).label('total_area'),
        func.sum(
            case(
                (FarmReport.tree_cover_loss.isnot(None),
                 func.cast(func.replace(FarmReport.tree_cover_loss, ',', ''), db.Float)),
                else_=0
            )
        ).label('total_tree_cover_loss')
    ).join(Farm, Farm.id == FarmReport.farm_id)

    if not user.is_admin:
        query = query.filter(Farm.created_by == user_id)

    query = query.group_by(FarmReport.eudr_compliance_assessment)

    results = query.all()

    data = []
    for row in results:
        data.append({
            'compliance_status': row.compliance_status or 'Unknown',
            'total_area': round(row.total_area or 0, 2),
            'total_tree_cover_loss': round(row.total_tree_cover_loss or 0, 2)
        })

    return jsonify({
        'status': 'success',
        'data': data
    })