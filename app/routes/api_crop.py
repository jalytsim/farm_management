from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import ProduceCategory, db, Crop

api_crop_bp = Blueprint('api_crop', __name__, url_prefix='/api/crop')

@api_crop_bp.route('/', methods=['GET'])
def index():
    crops = Crop.query.all()
    categories = ProduceCategory.query.all()
    crops_list = [
        {"id": crop.id, "name": crop.name, "weight": crop.weight, "category_id": crop.category_id} 
        for crop in crops
    ]
    categories_list = [{"id": category.id, "name": category.name} for category in categories]
    return jsonify(crops=crops_list, categories=categories_list)

@api_crop_bp.route('/create', methods=['POST'])
def create_crop():
    data = request.json
    name = data.get('name')
    weight = data.get('weight')
    category_id = data.get('category_id')
    new_crop = Crop(
        name=name,
        weight=weight,
        category_id=category_id,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )
    db.session.add(new_crop)
    db.session.commit()
    return jsonify({"msg": "Crop created successfully!"}), 201

@api_crop_bp.route('/<int:id>/edit', methods=['PUT'])
def edit_crop(id):
    crop = Crop.query.get_or_404(id)
    data = request.json
    crop.name = data.get('name')
    crop.weight = data.get('weight')
    crop.category_id = data.get('category_id')
    crop.date_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Crop updated successfully!"})

@api_crop_bp.route('/<int:id>', methods=['GET'])
def get_crop(id):
    crop = Crop.query.get_or_404(id)
    crop_data = {
        'id': crop.id,
        'name': crop.name,
        'weight': crop.weight,
        'category_id': crop.category_id
    }
    return jsonify(crop_data)

@api_crop_bp.route('/<int:id>/delete', methods=['DELETE'])getbycrop
def delete_crop(id):
    crop = Crop.query.get_or_404(id)
    db.session.delete(crop)
    db.session.commit()
    return jsonify({"msg": "Crop deleted successfully!"})

@api_crop_bp.route('/getbycat/<int:category_id>' methods=['GET'])
def get_crop_by_id(category_id):
    crops = Crop.query.filter_by(category_id=category_id).all()
    crops_list = [
        {
            'id': crop.id,
            'name': crop.name,
            'weight': crop.weight,
            'category_id': crop.category_id

        } for crop in crops
    ]
    return jsonify({
        'crops': crops_list,
    })




