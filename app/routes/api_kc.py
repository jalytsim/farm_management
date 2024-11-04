from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import CropCoefficient, db

bp = Blueprint('api_crop_coefficient', __name__, url_prefix='/api/cropcoefficient')

# Get all crop coefficient records
@bp.route('/', methods=['GET'])
def index():
    coefficients = CropCoefficient.query.all()
    coefficients_list = [
        {
            "id": coefficient.id,
            "crop_id": coefficient.crop_id,
            "stage": coefficient.stage,
            "kc_value": coefficient.kc_value,
            "date_created": coefficient.date_created,
            "date_updated": coefficient.date_updated
        }
        for coefficient in coefficients
    ]
    return jsonify(coefficients=coefficients_list)

# Create a new crop coefficient record
@bp.route('/create', methods=['POST'])
def create_coefficient():
    data = request.json
    crop_id = data.get('crop_id')
    stage = data.get('stage')
    kc_value = data.get('kc_value')

    new_coefficient = CropCoefficient(
        crop_id=crop_id,
        stage=stage,
        kc_value=kc_value,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )

    db.session.add(new_coefficient)
    db.session.commit()
    return jsonify({"msg": "Crop coefficient created successfully!"}), 201

# Edit an existing crop coefficient record
@bp.route('/<int:id>/edit', methods=['PUT'])
def edit_coefficient(id):
    coefficient = CropCoefficient.query.get_or_404(id)
    data = request.json

    coefficient.crop_id = data.get('crop_id')
    coefficient.stage = data.get('stage')
    coefficient.kc_value = data.get('kc_value')
    coefficient.date_updated = datetime.utcnow()

    db.session.commit()
    return jsonify({"msg": "Crop coefficient updated successfully!"})

# Get a specific crop coefficient record by id
@bp.route('/<int:id>', methods=['GET'])
def get_coefficient(id):
    coefficient = CropCoefficient.query.get_or_404(id)
    coefficient_data = {
        'id': coefficient.id,
        'crop_id': coefficient.crop_id,
        'stage': coefficient.stage,
        'kc_value': coefficient.kc_value,
        'date_created': coefficient.date_created,
        'date_updated': coefficient.date_updated
    }
    return jsonify(coefficient_data)

# Delete a crop coefficient record
@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_coefficient(id):
    coefficient = CropCoefficient.query.get_or_404(id)
    db.session.delete(coefficient)
    db.session.commit()
    return jsonify({"msg": "Crop coefficient deleted successfully!"})


@bp.route('/getbycrop/<int:crop_id>', methods=['GET'])
def get_by_crop_id(crop_id):
    coefficients = CropCoefficient.query.filter_by(crop_id=crop_id).all()
    if coefficients:

        coefficients_list = [
            {
                'id': coefficient.id,
                'crop_id': coefficient.crop_id,
                'stage': coefficient.stage,
                'kc_value': coefficient.kc_value,
                'date_created': coefficient.date_created,
                'date_updated': coefficient.date_updated

            } for coefficient in coefficients
        ]
        return jsonify({
            'status': 'success',
            'kc_value': coefficients_list,
        })
    else:
        # Return an error message if no data is found
        return jsonify({
            'status': 'error',
            'message': 'No data found for the provided farm ID'
        }), 404

