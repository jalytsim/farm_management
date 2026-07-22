from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from alertspest import fetch_weather_data, detect_gdd_and_pest_alerts
from alerts import detect_anomalies

from app import db
from sqlalchemy import func, case

from app.models import Farm, User, FarmReport, District, FarmerGroup
from app.utils import farm_utils
import logging
from datetime import datetime, date
import datetime
from app.models import Point


bp = Blueprint('api_farm', __name__, url_prefix='/api/farm')

@bp.route('/')
@jwt_required()
def index():
    identity = get_jwt_identity()
    user_id  = identity['id']
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)
    search   = request.args.get('search', '').strip()

    user = User.query.get(user_id)

    # Base query selon le rôle
    if user.is_admin:
        query = Farm.query
    else:
        query = Farm.query.filter_by(created_by=user_id)

    # ── Recherche serveur sur plusieurs colonnes ───────────────────────────
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Farm.name.ilike(like),
                Farm.subcounty.ilike(like),
                Farm.farm_id.ilike(like),
                Farm.cin.ilike(like),
            )
        )

    farms = query.paginate(page=page, per_page=per_page, error_out=False)

    farms_list = [{
        "id":           farm.farm_id,
        "name":         farm.name,
        "subcounty":    farm.subcounty,
        "district_id":  farm.district_id,
        "farmergroup_id": farm.farmergroup_id,
        "geolocation":  farm.geolocation,
        "phonenumber1": farm.phonenumber,
        "phonenumber2": farm.phonenumber2,
        "gender":       farm.gender,
        "cin":          farm.cin,
    } for farm in farms.items]

    return jsonify(
        farms=farms_list,
        total_pages=farms.pages,
        current_page=farms.page,
        total_farms=farms.total,
        search=search,
    )

@bp.route('/all')
@jwt_required()
def all():
    identity = get_jwt_identity()
    user_id = identity['id']

    user = User.query.get(user_id)
    print("+++++++++===========+++++++++", user_id)

    if user.is_admin:
        farms = Farm.query.all()
    else:
        farms = Farm.query.filter_by(created_by=user_id).all()

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

    return jsonify(
        farms=farms_list,
        total_farms=len(farms_list),
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

        existing_farm = Farm.query.filter_by(
            name=data['name'],
            district_id=data['district_id'],
            geolocation=geolocation,
            cin=data['cin'],
        ).first()

        if existing_farm:
            return jsonify({"msg": "Farm already exists", "farm_id": existing_farm.farm_id}), 409

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
                continue

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
    identity = get_jwt_identity()
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
    if farm:
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
            "cin": farm.cin,
        }
        return jsonify({
            'status': 'success',
            'data': farm_data
        })
    else:
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
    farms = Farm.query.all()
    results = []

    for farm in farms:
        try:
            if not farm.geolocation or ',' not in farm.geolocation:
                raise ValueError("Invalid geolocation format")

            parts = farm.geolocation.split(',')
            if len(parts) != 2:
                raise ValueError("Geolocation must contain exactly 2 parts")

            lat, lon = map(float, parts)
            print(f"[INFO] Processing farm: {farm.name} at ({lat}, {lon})")

            weather_data = fetch_weather_data(lat, lon)

            if not weather_data or not isinstance(weather_data, list):
                raise ValueError(f"Empty or invalid weather data for farm '{farm.name}'")

            print(f"[DEBUG] {farm.name} weather data sample:", weather_data[:3])

            weather_alerts = detect_anomalies(weather_data)
            pest_alerts = detect_gdd_and_pest_alerts(weather_data)

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


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: normalise une valeur eudr_compliance_assessment (Python-side)
# Utilisé dans toutes les routes qui itèrent sur les fermes.
# ─────────────────────────────────────────────────────────────────────────────
def _normalize_compliance(val):
    """
    Normalise une valeur de compliance pour la comparaison.
    "100% Compliant" → "100%compliant"
    "Likely Compliant" → "likelycompliant"
    "Not Compliant"   → "notcompliant"
    None / ""         → None
    """
    if not val:
        return None
    return val.replace(" ", "").lower()


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: incrémente les compteurs de compliance dans un dict
# ─────────────────────────────────────────────────────────────────────────────
def _increment_compliance(status_dict, normalized_status):
    if normalized_status == '100%compliant':
        status_dict['compliant_100'] += 1
    elif normalized_status == 'likelycompliant':
        status_dict['likely_compliant'] += 1
    elif normalized_status == 'notcompliant':
        status_dict['not_compliant'] += 1
    else:
        status_dict['no_report'] += 1


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: calcule les pourcentages à partir des compteurs
# ─────────────────────────────────────────────────────────────────────────────
def _compute_percentages(compliance_status, total_farms):
    if total_farms == 0:
        return {
            'compliant_100_percent': 0,
            'likely_compliant_percent': 0,
            'not_compliant_percent': 0,
            'no_report_percent': 0,
            'overall_rate': 0,
        }
    c   = compliance_status['compliant_100']
    lc  = compliance_status['likely_compliant']
    nc  = compliance_status['not_compliant']
    nr  = compliance_status['no_report']
    return {
        'compliant_100_percent':    round(c  / total_farms * 100, 2),
        'likely_compliant_percent': round(lc / total_farms * 100, 2),
        'not_compliant_percent':    round(nc / total_farms * 100, 2),
        'no_report_percent':        round(nr / total_farms * 100, 2),
        'overall_rate':             round((c + lc) / total_farms * 100, 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/farm/stats/by-user
# Statistiques agrégées — liste de tous les utilisateurs (admin) ou soi-même
# ─────────────────────────────────────────────────────────────────────────────
@bp.route('/stats/by-user', methods=['GET'])
@jwt_required()
def get_user_farm_statistics():
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)

    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    # Déterminer le périmètre
    if user.is_admin:
        if request.args.get('all_users') == 'true':
            target_user_id = None          # tous les utilisateurs
        elif request.args.get('user_id'):
            target_user_id = int(request.args.get('user_id'))
        else:
            target_user_id = user_id       # l'admin lui-même
    else:
        target_user_id = user_id

    # Récupérer les utilisateurs concernés
    if target_user_id:
        users = User.query.filter_by(id=target_user_id).all()
    else:
        users = User.query.all()

    statistics = []

    for target_user in users:
        farms = Farm.query.filter_by(created_by=target_user.id).all()
        total_farms = len(farms)

        compliance_status = {
            'compliant_100':    0,
            'likely_compliant': 0,
            'not_compliant':    0,
            'no_report':        0,
        }
        total_project_area    = 0.0
        total_tree_cover_loss = 0.0

        for farm in farms:
            report = FarmReport.query.filter_by(farm_id=farm.id).first()
            _increment_compliance(
                compliance_status,
                _normalize_compliance(report.eudr_compliance_assessment if report else None)
            )
            if report:
                if report.project_area:
                    try:
                        total_project_area += float(str(report.project_area).replace(',', ''))
                    except (ValueError, TypeError):
                        pass
                if report.tree_cover_loss:
                    try:
                        total_tree_cover_loss += float(str(report.tree_cover_loss).replace(',', ''))
                    except (ValueError, TypeError):
                        pass

        statistics.append({
            'user_id':      target_user.id,
            'username':     target_user.username,
            'email':        target_user.email,
            'company_name': target_user.company_name,
            'user_type':    target_user.user_type,
            'id_start':     target_user.id_start,
            'total_farms':  total_farms,
            'compliance_status':      compliance_status,
            'compliance_percentages': _compute_percentages(compliance_status, total_farms),
            'environmental_metrics': {
                'total_project_area':               round(total_project_area, 2),
                'total_tree_cover_loss':            round(total_tree_cover_loss, 2),
                'average_project_area_per_farm':    round(total_project_area    / total_farms, 2) if total_farms > 0 else 0,
                'average_tree_cover_loss_per_farm': round(total_tree_cover_loss / total_farms, 2) if total_farms > 0 else 0,
            },
        })

    return jsonify({
        'status':      'success',
        'data':        statistics,
        'total_users': len(statistics),
    })


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/farm/stats/by-user/<target_user_id>
# Statistiques détaillées d'un utilisateur précis
# ─────────────────────────────────────────────────────────────────────────────
@bp.route('/stats/by-user/<int:target_user_id>', methods=['GET'])
@jwt_required()
def get_specific_user_farm_statistics(target_user_id):
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)

    if not user.is_admin and user_id != target_user_id:
        return jsonify({
            'status':  'error',
            'message': 'Unauthorized: You can only access your own statistics'
        }), 403

    target_user = User.query.get_or_404(target_user_id)
    farms       = Farm.query.filter_by(created_by=target_user_id).all()
    total_farms = len(farms)

    compliance_status = {
        'compliant_100':    0,
        'likely_compliant': 0,
        'not_compliant':    0,
        'no_report':        0,
    }
    total_project_area    = 0.0
    total_tree_cover_loss = 0.0
    farms_detail          = []

    for farm in farms:
        report         = FarmReport.query.filter_by(farm_id=farm.id).first()
        raw_status     = report.eudr_compliance_assessment if report else None
        norm_status    = _normalize_compliance(raw_status)

        print(f"[DEBUG] farm_id={farm.id} raw_status={raw_status!r} norm={norm_status!r}")

        _increment_compliance(compliance_status, norm_status)

        farm_area = 0.0
        farm_loss = 0.0

        if report:
            if report.project_area:
                try:
                    farm_area = float(str(report.project_area).replace(',', ''))
                    total_project_area += farm_area
                except (ValueError, TypeError):
                    pass
            if report.tree_cover_loss:
                try:
                    farm_loss = float(str(report.tree_cover_loss).replace(',', ''))
                    total_tree_cover_loss += farm_loss
                except (ValueError, TypeError):
                    pass

        farms_detail.append({
            'farm_id':                     farm.farm_id,
            'farm_name':                   farm.name,
            'eudr_compliance_assessment':  raw_status,
            'project_area':                round(farm_area, 2),
            'tree_cover_loss':             round(farm_loss, 2),
        })

    result = {
        'user_id':      target_user.id,
        'username':     target_user.username,
        'email':        target_user.email,
        'company_name': target_user.company_name,
        'user_type':    target_user.user_type,
        'id_start':     target_user.id_start,
        'total_farms':  total_farms,
        'farms_detail': farms_detail,
        'compliance_status':      compliance_status,
        'compliance_percentages': _compute_percentages(compliance_status, total_farms),
        'environmental_metrics': {
            'total_project_area':               round(total_project_area, 2),
            'total_tree_cover_loss':            round(total_tree_cover_loss, 2),
            'average_project_area_per_farm':    round(total_project_area    / total_farms, 2) if total_farms > 0 else 0,
            'average_tree_cover_loss_per_farm': round(total_tree_cover_loss / total_farms, 2) if total_farms > 0 else 0,
        },
    }

    return jsonify({'status': 'success', 'data': result})


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/farm/stats/comparison
# Comparaison multi-utilisateurs (admin uniquement)
# ─────────────────────────────────────────────────────────────────────────────
@bp.route('/stats/comparison', methods=['GET'])
@jwt_required()
def get_user_comparison():
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)

    if not user.is_admin:
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403

    user_ids_str = request.args.get('user_ids', '')
    user_ids     = [int(uid.strip()) for uid in user_ids_str.split(',') if uid.strip()]

    comparison = []

    for uid in user_ids:
        target = User.query.get(uid)
        if not target:
            continue

        farms       = Farm.query.filter_by(created_by=uid).all()
        total_farms = len(farms)

        compliance_status = {
            'compliant_100':    0,
            'likely_compliant': 0,
            'not_compliant':    0,
            'no_report':        0,
        }
        total_project_area    = 0.0
        total_tree_cover_loss = 0.0

        for farm in farms:
            report = FarmReport.query.filter_by(farm_id=farm.id).first()
            _increment_compliance(
                compliance_status,
                _normalize_compliance(report.eudr_compliance_assessment if report else None)
            )
            if report:
                if report.project_area:
                    try:
                        total_project_area += float(str(report.project_area).replace(',', ''))
                    except (ValueError, TypeError):
                        pass
                if report.tree_cover_loss:
                    try:
                        total_tree_cover_loss += float(str(report.tree_cover_loss).replace(',', ''))
                    except (ValueError, TypeError):
                        pass

        comparison.append({
            'user_id':                  uid,
            'username':                 target.username,
            'company_name':             target.company_name,
            'total_farms':              total_farms,
            'compliance_status':        compliance_status,
            'compliance_percentages':   _compute_percentages(compliance_status, total_farms),
            'total_project_area':       round(total_project_area, 2),
            'total_tree_cover_loss':    round(total_tree_cover_loss, 2),
        })

    return jsonify({'status': 'success', 'data': comparison})


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/farm/stats/summary
# Résumé global (avec filtres optionnels)
# ─────────────────────────────────────────────────────────────────────────────
@bp.route('/stats/summary', methods=['GET'])
@jwt_required()
def get_global_summary():
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)

    query = Farm.query

    if not (user.is_admin and request.args.get('global') == 'true'):
        query = query.filter_by(created_by=user_id)

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

    compliance_summary = {
        'compliant_100':    0,
        'likely_compliant': 0,
        'not_compliant':    0,
        'no_report':        0,
    }
    environmental_summary = {
        'total_project_area':       0.0,
        'total_tree_cover_loss':    0.0,
        'average_project_area':     0.0,
        'average_tree_cover_loss':  0.0,
    }
    by_district     = {}
    by_farmer_group = {}
    project_areas   = []
    tree_cover_losses = []

    for farm in farms:
        report      = FarmReport.query.filter_by(farm_id=farm.id).first()
        norm_status = _normalize_compliance(report.eudr_compliance_assessment if report else None)

        _increment_compliance(compliance_summary, norm_status)

        # District
        district = District.query.get(farm.district_id) if farm.district_id else None
        if district:
            d = by_district.setdefault(district.name, {
                'total_farms': 0, 'compliant_100': 0,
                'likely_compliant': 0, 'not_compliant': 0
            })
            d['total_farms'] += 1
            if norm_status == '100%compliant':
                d['compliant_100'] += 1
            elif norm_status == 'likelycompliant':
                d['likely_compliant'] += 1
            elif norm_status == 'notcompliant':
                d['not_compliant'] += 1

        # Farmer group
        farmer_group = FarmerGroup.query.get(farm.farmergroup_id) if farm.farmergroup_id else None
        if farmer_group:
            g = by_farmer_group.setdefault(farmer_group.name, {
                'total_farms': 0, 'compliant_100': 0,
                'likely_compliant': 0, 'not_compliant': 0
            })
            g['total_farms'] += 1
            if norm_status == '100%compliant':
                g['compliant_100'] += 1
            elif norm_status == 'likelycompliant':
                g['likely_compliant'] += 1
            elif norm_status == 'notcompliant':
                g['not_compliant'] += 1

        if report:
            try:
                if report.project_area:
                    area = float(str(report.project_area).replace(',', ''))
                    environmental_summary['total_project_area'] += area
                    project_areas.append(area)
            except (ValueError, TypeError):
                pass
            try:
                if report.tree_cover_loss:
                    loss = float(str(report.tree_cover_loss).replace(',', ''))
                    environmental_summary['total_tree_cover_loss'] += loss
                    tree_cover_losses.append(loss)
            except (ValueError, TypeError):
                pass

    if project_areas:
        environmental_summary['average_project_area'] = round(
            sum(project_areas) / len(project_areas), 2)
    if tree_cover_losses:
        environmental_summary['average_tree_cover_loss'] = round(
            sum(tree_cover_losses) / len(tree_cover_losses), 2)

    environmental_summary['total_project_area']    = round(environmental_summary['total_project_area'], 2)
    environmental_summary['total_tree_cover_loss'] = round(environmental_summary['total_tree_cover_loss'], 2)

    total_farms = len(farms)

    summary = {
        'total_farms':              total_farms,
        'total_users':              User.query.count() if user.is_admin else 1,
        'filters_applied': {
            'district_id':      district_id,
            'farmergroup_id':   farmergroup_id,
            'year':             year,
        },
        'compliance_summary':       compliance_summary,
        'compliance_percentages':   _compute_percentages(compliance_summary, total_farms),
        'environmental_summary':    environmental_summary,
        'by_district':              by_district,
        'by_farmer_group':          by_farmer_group,
    }

    return jsonify({'status': 'success', 'data': summary})


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/farm/area/by-compliance
# Aires + comptage de fermes groupés par statut de compliance
# SOURCE DE VÉRITÉ pour le certificat (pas de normalisation SQL fragile)
# ─────────────────────────────────────────────────────────────────────────────
@bp.route('/area/by-compliance', methods=['GET'])
@jwt_required()
def get_area_by_compliance():
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)

    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    # Requête groupée par valeur brute de compliance_assessment
    query = db.session.query(
        FarmReport.eudr_compliance_assessment.label('compliance_status'),
        func.count(FarmReport.id).label('farm_count'),
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
            'compliance_status':    row.compliance_status or 'Unknown',
            'farm_count':           row.farm_count or 0,
            'total_area':           round(row.total_area or 0, 2),
            'total_tree_cover_loss': round(row.total_tree_cover_loss or 0, 2),
        })

    return jsonify({'status': 'success', 'data': data})

# ─────────────────────────────────────────────────────────────────────────────
# GET /api/farm/export/polygons
# Exporte les polygones de toutes les fermes visibles en un seul GeoJSON
# ─────────────────────────────────────────────────────────────────────────────
@bp.route('/export/polygons', methods=['GET'])
@jwt_required()
def export_farm_polygons():
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)

    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    if user.is_admin:
        farms = Farm.query.all()
    else:
        farms = Farm.query.filter_by(created_by=user_id).all()

    features = []
    skipped  = []

    for farm in farms:
        points = (
            Point.query
            .filter_by(owner_type='farmer', owner_id=farm.farm_id)
            .order_by(Point.id.asc())
            .all()
        )

        if len(points) < 3:
            skipped.append({"farm_id": farm.farm_id, "name": farm.name, "reason": "not_enough_points"})
            continue

        ring = [[float(p.longitude), float(p.latitude)] for p in points]
        # Fermer l'anneau si besoin (même logique que MapView.jsx)
        if ring[0] != ring[-1]:
            ring.append(ring[0])

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [ring],
            },
            "properties": {
                "farm_id":     farm.farm_id,
                "name":        farm.name,
                "subcounty":   farm.subcounty,
                "district_id": farm.district_id,
                "cin":         farm.cin,
                "gender":      farm.gender,
            },
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    return jsonify({
        "status":  "success",
        "geojson": geojson,
        "total_exported": len(features),
        "skipped": skipped,
    })
    
    # ─────────────────────────────────────────────────────────────────────────────
# GET /api/farm/<farm_id>/export/polygon
# Exporte le polygone d'une seule ferme en GeoJSON (geometry: MultiPolygon)
# ─────────────────────────────────────────────────────────────────────────────
@bp.route('/<farm_id>/export/polygon', methods=['GET'])
@jwt_required()
def export_single_farm_polygon(farm_id):
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)

    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    farm = Farm.query.filter_by(farm_id=farm_id).first_or_404()

    if not user.is_admin and farm.created_by != user_id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

    points = (
        Point.query
        .filter_by(owner_type='farmer', owner_id=farm.farm_id)
        .order_by(Point.id.asc())
        .all()
    )

    if len(points) < 3:
        return jsonify({
            'status':  'error',
            'message': 'Not enough points to build a polygon for this farm',
        }), 400

    ring = [[float(p.longitude), float(p.latitude)] for p in points]
    if ring[0] != ring[-1]:
        ring.append(ring[0])

    feature = {
        "type": "Feature",
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [[ring]],   # un seul polygone dans le tableau, extensible plus tard
        },
        "properties": {
            "farm_id":     farm.farm_id,
            "name":        farm.name,
            "subcounty":   farm.subcounty,
            "district_id": farm.district_id,
            "cin":         farm.cin,
            "gender":      farm.gender,
            "vertex_count": len(ring) - 1,
        },
    }

    geojson = {
        "type": "FeatureCollection",
        "features": [feature],
    }

    return jsonify({
        "status":  "success",
        "geojson": geojson,
    })
    
@bp.route('/bulk-create-geojson', methods=['POST'])
@jwt_required()
def bulk_create_farms_geojson():
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)

    if not user or not user.id_start:
        return jsonify({"msg": "User id_start is not defined"}), 400
    if 'file' not in request.files:
        return jsonify({"msg": "No file provided"}), 400

    file = request.files['file']
    try:
        geojson = json.loads(file.stream.read().decode('utf-8'))
    except Exception as e:
        return jsonify({"msg": f"Invalid GeoJSON file: {e}"}), 400

    features = geojson.get('features', [])
    if not features:
        return jsonify({"msg": "No features found in GeoJSON"}), 400

    results = {'success': 0, 'errors': 0, 'skipped': 0, 'details': []}

    for row_num, feature in enumerate(features, start=1):
        props = feature.get('properties', {}) or {}
        name = (props.get('name') or '').strip()
        try:
            if not name:
                raise ValueError('Name is required')

            district_id = props.get('district_id')
            farmergroup_id = props.get('farmergroup_id')
            cin = props.get('cin')

            ring = point_utils.ring_from_geometry(feature.get('geometry') or {})
            if len(ring) < 3:
                raise ValueError('Polygon needs at least 3 vertices')
            lon, lat = point_utils.polygon_centroid(ring)
            geolocation = f"{lat:.6f}, {lon:.6f}"

            existing_farm = Farm.query.filter_by(name=name, district_id=district_id, cin=cin).first()
            if existing_farm:
                results['skipped'] += 1
                results['details'].append({'row': row_num, 'name': name, 'farm_id': existing_farm.farm_id,
                                             'status': 'skipped', 'reason': 'Farm already exists for this district/CIN'})
                continue

            new_farm = farm_utils.create_farm(
                user=user, name=name, subcounty=props.get('subcounty'),
                farmergroup_id=farmergroup_id, district_id=district_id, geolocation=geolocation,
                phonenumber1=props.get('phonenumber1') or props.get('phonenumber'),
                phonenumber2=props.get('phonenumber2', ''), gender=props.get('gender'), cin=cin,
            )

            for lng, lat_pt in ring:
                point_utils.create_point(longitude=lng, latitude=lat_pt, owner_type='farmer',
                                          district_id=district_id, farmer_id=new_farm.farm_id, user=user)

            results['success'] += 1
            results['details'].append({'row': row_num, 'name': name, 'farm_id': new_farm.farm_id,
                                         'points_created': len(ring), 'status': 'created'})
        except Exception as e:
            db.session.rollback()
            results['errors'] += 1
            results['details'].append({'row': row_num, 'name': name or 'N/A', 'error': str(e)})

    return jsonify(results), 200