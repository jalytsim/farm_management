from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_cors import cross_origin
from app.utils import farmdata_utils
from app.models import Farm, Crop, FarmData, User
from app import db

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
            'hs_code': data.hs_code
        } for data in farmdata_list
    ]
    return jsonify(farmdata_list=farmdata_json)

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_farmdata():
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)

    data = request.json
    # Ensure hs_code is included if provided
    data['hs_code'] = data.get('hs_code')

    farmdata_utils.create_farmdata(data, user)
    return jsonify({"msg": "FarmData created successfully."}), 201

@bp.route('/<int:id>/edit', methods=['PUT'])
def edit_farmdata(id):
    farmdata = farmdata_utils.get_farmdata_by_id(id)
    data = request.json
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
        'hs_code': farmdata.hs_code,
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

# Nouveau endpoint pour récupérer la dernière date de plantation
@bp.route('/latest-planting-date/<string:farm_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_latest_planting_date(farm_id):
    """Retourne la date de plantation la plus récente pour une ferme donnée."""
    latest = (FarmData.query
              .filter_by(farm_id=farm_id)
              .order_by(FarmData.timestamp.desc())
              .first())

    if not latest: 
        return jsonify({'msg': 'Aucun enregistrement trouvé'}), 404
    # 🔥 Récupération de la culture plantée
    crop = Crop.query.get(latest.crop_id)
    crop_name = crop.name if crop else None

    return jsonify({
        'farm_id': farm_id,
        'planting_date': latest.planting_date.isoformat(),
        'crop_name': crop_name     # ✅ ajouté ici
    
        
    }), 200

@bp.route('/save-planting-date', methods=['GET'])
@jwt_required()
def save_planting_date_via_get():
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])

    farm_id       = request.args.get('farm_id')
    crop_id       = request.args.get('crop_id')
    planting_date = request.args.get('planting_date')

    if not farm_id or not crop_id or not planting_date:
        return jsonify({'msg': 'Il manque farm_id, crop_id ou planting_date'}), 400

    # 1) Recherche du dernier FarmData existant
    existing = (FarmData.query
                .filter_by(farm_id=farm_id, crop_id=crop_id)
                .order_by(FarmData.timestamp.desc())
                .first())

    if existing:
        # 2) Mise à jour
        existing.planting_date = planting_date
        db.session.commit()
        msg = 'Date de plantation mise à jour'
    else:
        # 3) Création si aucun enregistrement
        data = {'farm_id': farm_id, 'crop_id': crop_id, 'planting_date': planting_date}
        farmdata_utils.create_farmdata(data, user)
        msg = 'Date de plantation créée'

    return jsonify({'msg': msg}), 200
