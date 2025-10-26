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

@bp.route('/stats/by-user', methods=['GET'])
@jwt_required()
def get_user_farm_statistics():
    """
    Retourne les statistiques détaillées des fermes par utilisateur
    incluant le statut EUDR compliance, project area et tree cover loss
    
    Query params:
    - all_users=true : (admin only) Obtenir les stats de tous les utilisateurs
    - user_id=<id> : Filtrer par un utilisateur spécifique (admin only)
    """
    identity = get_jwt_identity()
    user_id = identity['id']
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # Déterminer le filtre utilisateur
    target_user_id = None
    if user.is_admin:
        # Admin peut voir tous les utilisateurs ou un utilisateur spécifique
        if request.args.get('all_users') == 'true':
            target_user_id = None  # Tous
        elif request.args.get('user_id'):
            target_user_id = int(request.args.get('user_id'))
        else:
            target_user_id = user_id  # Ses propres stats par défaut
    else:
        # Utilisateur normal : uniquement ses propres stats
        target_user_id = user_id
    
    # Requête principale avec jointure
    query = db.session.query(
        User.id.label('user_id'),
        User.username.label('username'),
        User.email.label('email'),
        User.user_type.label('user_type'),
        func.count(Farm.id).label('total_farms'),
        
        # Comptage par statut EUDR compliance
        func.sum(
            case(
                (FarmReport.eudr_compliance_assessment == '100% Compliant', 1),
                else_=0
            )
        ).label('compliant_count'),
        
        func.sum(
            case(
                (FarmReport.eudr_compliance_assessment == 'Not Compliant', 1),
                else_=0
            )
        ).label('not_compliant_count'),
        
        func.sum(
            case(
                (FarmReport.eudr_compliance_assessment == 'Likely Compliant', 1),
                else_=0
            )
        ).label('likely_compliant_count'),
        
        # Farms sans rapport
        func.sum(
            case(
                (FarmReport.id.is_(None), 1),
                else_=0
            )
        ).label('no_report_count'),
        
        # Somme des project areas
        func.sum(
            case(
                (FarmReport.project_area.isnot(None), 
                 func.cast(func.replace(FarmReport.project_area, ',', ''), db.Float)),
                else_=0
            )
        ).label('total_project_area'),
        
        # Somme des tree cover loss
        func.sum(
            case(
                (FarmReport.tree_cover_loss.isnot(None), 
                 func.cast(func.replace(FarmReport.tree_cover_loss, ',', ''), db.Float)),
                else_=0
            )
        ).label('total_tree_cover_loss')
        
    ).select_from(User)\
     .join(Farm, Farm.created_by == User.id)\
     .outerjoin(FarmReport, FarmReport.farm_id == Farm.id)
    
    # Filtrer par utilisateur si nécessaire
    if target_user_id:
        query = query.filter(User.id == target_user_id)
    
    # Grouper par utilisateur
    query = query.group_by(User.id, User.username, User.email, User.user_type)
    
    results = query.all()
    
    # Formater les résultats
    statistics = []
    for result in results:
        total_farms = result.total_farms or 0
        
        statistics.append({
            'user_id': result.user_id,
            'username': result.username,
            'email': result.email,
            'user_type': result.user_type,
            'total_farms': total_farms,
            'compliance_status': {
                'compliant_100': result.compliant_count or 0,
                'not_compliant': result.not_compliant_count or 0,
                'likely_compliant': result.likely_compliant_count or 0,
                'no_report': result.no_report_count or 0
            },
            'compliance_percentages': {
                'compliant_100_percent': round((result.compliant_count or 0) / total_farms * 100, 2) if total_farms > 0 else 0,
                'not_compliant_percent': round((result.not_compliant_count or 0) / total_farms * 100, 2) if total_farms > 0 else 0,
                'likely_compliant_percent': round((result.likely_compliant_count or 0) / total_farms * 100, 2) if total_farms > 0 else 0,
                'no_report_percent': round((result.no_report_count or 0) / total_farms * 100, 2) if total_farms > 0 else 0
            },
            'environmental_metrics': {
                'total_project_area': round(result.total_project_area or 0, 2),
                'total_tree_cover_loss': round(result.total_tree_cover_loss or 0, 2),
                'average_project_area_per_farm': round((result.total_project_area or 0) / total_farms, 2) if total_farms > 0 else 0,
                'average_tree_cover_loss_per_farm': round((result.total_tree_cover_loss or 0) / total_farms, 2) if total_farms > 0 else 0
            }
        })
    
    return jsonify({
        'status': 'success',
        'data': statistics,
        'total_users': len(statistics)
    })


@bp.route('/stats/by-user/<int:target_user_id>', methods=['GET'])
@jwt_required()
def get_specific_user_farm_statistics(target_user_id):
    """
    Retourne les statistiques détaillées pour un utilisateur spécifique
    avec la liste complète de ses fermes
    """
    identity = get_jwt_identity()
    user_id = identity['id']
    
    user = User.query.get(user_id)
    
    # Vérifier les permissions
    if not user.is_admin and user_id != target_user_id:
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized: You can only access your own statistics'
        }), 403
    
    # Récupérer l'utilisateur cible
    target_user = User.query.get_or_404(target_user_id)
    
    # Récupérer toutes les fermes de l'utilisateur
    farms = Farm.query.filter_by(created_by=target_user_id).all()
    
    result = {
        'user_id': target_user.id,
        'username': target_user.username,
        'email': target_user.email,
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
    
    # Parcourir toutes les fermes et leurs rapports
    for farm in farms:
        report = FarmReport.query.filter_by(farm_id=farm.id).first()
        
        # Récupérer district et farmer group
        district = District.query.get(farm.district_id) if farm.district_id else None
        farmer_group = FarmerGroup.query.get(farm.farmergroup_id) if farm.farmergroup_id else None
        
        farm_info = {
            'farm_id': farm.farm_id,
            'name': farm.name,
            'subcounty': farm.subcounty,
            'geolocation': farm.geolocation,
            'district': district.name if district else None,
            'farmer_group': farmer_group.name if farmer_group else None,
            'date_created': farm.date_created.isoformat() if farm.date_created else None,
            'compliance_status': None,
            'project_area': None,
            'tree_cover_loss': None,
            'forest_cover_2020': None,
            'radd_alert': None
        }
        
        if report:
            compliance = report.eudr_compliance_assessment
            farm_info['compliance_status'] = compliance
            farm_info['project_area'] = report.project_area
            farm_info['tree_cover_loss'] = report.tree_cover_loss
            farm_info['forest_cover_2020'] = report.forest_cover_2020
            farm_info['radd_alert'] = report.radd_alert
            farm_info['protected_area_status'] = report.protected_area_status
            
            # Comptage par statut
            if compliance == '100% Compliant':
                result['compliance_status']['compliant_100'] += 1
            elif compliance == 'Not Compliant':
                result['compliance_status']['not_compliant'] += 1
            elif compliance == 'Likely Compliant':
                result['compliance_status']['likely_compliant'] += 1
            
            # Sommes des métriques (gérer les virgules comme séparateurs décimaux)
            try:
                if report.project_area:
                    area_str = str(report.project_area).replace(',', '')
                    result['environmental_metrics']['total_project_area'] += float(area_str)
            except (ValueError, TypeError) as e:
                print(f"Error converting project_area for farm {farm.farm_id}: {e}")
            
            try:
                if report.tree_cover_loss:
                    loss_str = str(report.tree_cover_loss).replace(',', '')
                    result['environmental_metrics']['total_tree_cover_loss'] += float(loss_str)
            except (ValueError, TypeError) as e:
                print(f"Error converting tree_cover_loss for farm {farm.farm_id}: {e}")
        else:
            result['compliance_status']['no_report'] += 1
        
        result['farms_detail'].append(farm_info)
    
    # Calculer les pourcentages
    total = result['total_farms']
    result['compliance_percentages'] = {
        'compliant_100_percent': round(result['compliance_status']['compliant_100'] / total * 100, 2) if total > 0 else 0,
        'not_compliant_percent': round(result['compliance_status']['not_compliant'] / total * 100, 2) if total > 0 else 0,
        'likely_compliant_percent': round(result['compliance_status']['likely_compliant'] / total * 100, 2) if total > 0 else 0,
        'no_report_percent': round(result['compliance_status']['no_report'] / total * 100, 2) if total > 0 else 0
    }
    
    # Arrondir les totaux
    result['environmental_metrics']['total_project_area'] = round(
        result['environmental_metrics']['total_project_area'], 2
    )
    result['environmental_metrics']['total_tree_cover_loss'] = round(
        result['environmental_metrics']['total_tree_cover_loss'], 2
    )
    
    # Ajouter les moyennes
    result['environmental_metrics']['average_project_area_per_farm'] = round(
        result['environmental_metrics']['total_project_area'] / total, 2
    ) if total > 0 else 0
    
    result['environmental_metrics']['average_tree_cover_loss_per_farm'] = round(
        result['environmental_metrics']['total_tree_cover_loss'] / total, 2
    ) if total > 0 else 0
    
    return jsonify({
        'status': 'success',
        'data': result
    })


@bp.route('/stats/summary', methods=['GET'])
@jwt_required()
def get_global_summary():
    """
    Retourne un résumé global de toutes les statistiques
    
    Query params:
    - global=true : (admin only) Stats globales de tous les utilisateurs
    - district_id=<id> : Filtrer par district
    - farmergroup_id=<id> : Filtrer par groupe d'agriculteurs
    - year=<YYYY> : Filtrer par année de création
    """
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)
    
    # Construire la requête de base
    query = Farm.query
    
    # Filtres selon les permissions
    if user.is_admin and request.args.get('global') == 'true':
        # Admin avec vue globale : pas de filtre utilisateur
        pass
    else:
        # Utilisateur normal : seulement ses fermes
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
            'not_compliant': 0,
            'likely_compliant': 0,
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
    
    for farm in farms:
        report = FarmReport.query.filter_by(farm_id=farm.id).first()
        
        # Stats par district
        district = District.query.get(farm.district_id) if farm.district_id else None
        if district:
            district_name = district.name
            if district_name not in summary['by_district']:
                summary['by_district'][district_name] = {
                    'total_farms': 0,
                    'compliant_100': 0,
                    'not_compliant': 0,
                    'likely_compliant': 0
                }
            summary['by_district'][district_name]['total_farms'] += 1
        
        # Stats par farmer group
        farmer_group = FarmerGroup.query.get(farm.farmergroup_id) if farm.farmergroup_id else None
        if farmer_group:
            fg_name = farmer_group.name
            if fg_name not in summary['by_farmer_group']:
                summary['by_farmer_group'][fg_name] = {
                    'total_farms': 0,
                    'compliant_100': 0,
                    'not_compliant': 0,
                    'likely_compliant': 0
                }
            summary['by_farmer_group'][fg_name]['total_farms'] += 1
        
        if report:
            compliance = report.eudr_compliance_assessment
            
            # Comptage global
            if compliance == '100% Compliant':
                summary['compliance_summary']['compliant_100'] += 1
                if district_name in summary['by_district']:
                    summary['by_district'][district_name]['compliant_100'] += 1
                if fg_name in summary['by_farmer_group']:
                    summary['by_farmer_group'][fg_name]['compliant_100'] += 1
            elif compliance == 'Not Compliant':
                summary['compliance_summary']['not_compliant'] += 1
                if district_name in summary['by_district']:
                    summary['by_district'][district_name]['not_compliant'] += 1
                if fg_name in summary['by_farmer_group']:
                    summary['by_farmer_group'][fg_name]['not_compliant'] += 1
            elif compliance == 'Likely Compliant':
                summary['compliance_summary']['likely_compliant'] += 1
                if district_name in summary['by_district']:
                    summary['by_district'][district_name]['likely_compliant'] += 1
                if fg_name in summary['by_farmer_group']:
                    summary['by_farmer_group'][fg_name]['likely_compliant'] += 1
            
            # Métriques environnementales
            try:
                if report.project_area:
                    area_str = str(report.project_area).replace(',', '')
                    area = float(area_str)
                    summary['environmental_summary']['total_project_area'] += area
                    project_areas.append(area)
            except (ValueError, TypeError):
                pass
            
            try:
                if report.tree_cover_loss:
                    loss_str = str(report.tree_cover_loss).replace(',', '')
                    loss = float(loss_str)
                    summary['environmental_summary']['total_tree_cover_loss'] += loss
                    tree_cover_losses.append(loss)
            except (ValueError, TypeError):
                pass
        else:
            summary['compliance_summary']['no_report'] += 1
    
    # Calculer les moyennes
    if project_areas:
        summary['environmental_summary']['average_project_area'] = round(
            sum(project_areas) / len(project_areas), 2
        )
    
    if tree_cover_losses:
        summary['environmental_summary']['average_tree_cover_loss'] = round(
            sum(tree_cover_losses) / len(tree_cover_losses), 2
        )
    
    # Arrondir les totaux
    summary['environmental_summary']['total_project_area'] = round(
        summary['environmental_summary']['total_project_area'], 2
    )
    summary['environmental_summary']['total_tree_cover_loss'] = round(
        summary['environmental_summary']['total_tree_cover_loss'], 2
    )
    
    return jsonify({
        'status': 'success',
        'data': summary
    })


@bp.route('/stats/comparison', methods=['GET'])
@jwt_required()
def get_user_comparison():
    """
    Compare les statistiques entre plusieurs utilisateurs (admin only)
    
    Query params:
    - user_ids=1,2,3 : Liste des IDs utilisateurs à comparer
    """
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({
            'status': 'error',
            'message': 'Admin access required'
        }), 403
    
    user_ids_str = request.args.get('user_ids', '')
    if not user_ids_str:
        return jsonify({
            'status': 'error',
            'message': 'user_ids parameter is required (comma-separated list)'
        }), 400
    
    try:
        user_ids = [int(uid.strip()) for uid in user_ids_str.split(',')]
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid user_ids format'
        }), 400
    
    comparison = []
    
    for uid in user_ids:
        target_user = User.query.get(uid)
        if not target_user:
            continue
        
        farms = Farm.query.filter_by(created_by=uid).all()
        
        user_stats = {
            'user_id': uid,
            'username': target_user.username,
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
            
            if report:
                compliance = report.eudr_compliance_assessment
                if compliance == '100% Compliant':
                    user_stats['compliant_100'] += 1
                elif compliance == 'Not Compliant':
                    user_stats['not_compliant'] += 1
                elif compliance == 'Likely Compliant':
                    user_stats['likely_compliant'] += 1
                
                try:
                    if report.project_area:
                        user_stats['total_project_area'] += float(str(report.project_area).replace(',', ''))
                except (ValueError, TypeError):
                    pass
                
                try:
                    if report.tree_cover_loss:
                        user_stats['total_tree_cover_loss'] += float(str(report.tree_cover_loss).replace(',', ''))
                except (ValueError, TypeError):
                    pass
            else:
                user_stats['no_report'] += 1
        
        # Arrondir
        user_stats['total_project_area'] = round(user_stats['total_project_area'], 2)
        user_stats['total_tree_cover_loss'] = round(user_stats['total_tree_cover_loss'], 2)
        
        comparison.append(user_stats)
    
    return jsonify({
        'status': 'success',
        'data': comparison
    })
