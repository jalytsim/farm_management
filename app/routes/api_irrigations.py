from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import Irrigation, db

bp = Blueprint('api_irrigation', __name__, url_prefix='/api/irrigation')

# Get all irrigation records
@bp.route('/', methods=['GET'])
def index():
    irrigation_list = Irrigation.query.all()
    irrigation_data = [
        {
            "id": irrigation.id,
            "crop_id": irrigation.crop_id,
            "farm_id": irrigation.farm_id,
            "irrigation_date": irrigation.irrigation_date,
            "water_applied": irrigation.water_applied,
            "method": irrigation.method,
            "date_created": irrigation.date_created,
            "date_updated": irrigation.date_updated
        } 
        for irrigation in irrigation_list
    ]
    return jsonify(irrigation=irrigation_data)

# Create a new irrigation record
@bp.route('/create', methods=['POST'])
def create_irrigation():
    data = request.json
    crop_id = data.get('crop_id')
    farm_id = data.get('farm_id')
    irrigation_date = data.get('irrigation_date')
    water_applied = data.get('water_applied')
    method = data.get('method')

    new_irrigation = Irrigation(
        crop_id=crop_id,
        farm_id=farm_id,
        irrigation_date=irrigation_date,
        water_applied=water_applied,
        method=method,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )

    db.session.add(new_irrigation)
    db.session.commit()
    return jsonify({"msg": "Irrigation record created successfully!"}), 201

# Edit an existing irrigation record
@bp.route('/<int:id>/edit', methods=['PUT'])
def edit_irrigation(id):
    irrigation = Irrigation.query.get_or_404(id)
    data = request.json

    irrigation.crop_id = data.get('crop_id')
    irrigation.farm_id = data.get('farm_id')
    irrigation.irrigation_date = data.get('irrigation_date')
    irrigation.water_applied = data.get('water_applied')
    irrigation.method = data.get('method')
    irrigation.date_updated = datetime.utcnow()

    db.session.commit()
    return jsonify({"msg": "Irrigation record updated successfully!"})

# Get a specific irrigation record by id
@bp.route('/<int:id>', methods=['GET'])
def get_irrigation(id):
    irrigation = Irrigation.query.get_or_404(id)
    irrigation_data = {
        'id': irrigation.id,
        'crop_id': irrigation.crop_id,
        'farm_id': irrigation.farm_id,
        'irrigation_date': irrigation.irrigation_date,
        'water_applied': irrigation.water_applied,
        'method': irrigation.method,
        'date_created': irrigation.date_created,
        'date_updated': irrigation.date_updated
    }
    return jsonify(irrigation_data)

# Delete an irrigation record
@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_irrigation(id):
    irrigation = Irrigation.query.get_or_404(id)
    db.session.delete(irrigation)
    db.session.commit()
    return jsonify({"msg": "Irrigation record deleted successfully!"})


@bp.route('/getbycrop/<int:crop_id>', methods=['GET'])
def get_by_crop_id(crop_id):
    irrigations = Irrigation.query.filter_by(crop_id=crop_id).all()
    irrigation_list = [
        {
            'id': irrigation.id,
            'crop_id': irrigation.crop_id,
            'farm_id': irrigation.farm_id,
            'irrigation_date': irrigation.irrigation_date,
            'water_applied': irrigation.water_applied,
            'method': irrigation.method,
            'date_created': irrigation.date_created,
            'date_updated': irrigation.date_updated

        } for irrigation in irrigations
    ]
    return jsonify({
        'irrigation': irrigation_list,
    })
