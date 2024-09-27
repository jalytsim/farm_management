from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import ProduceCategory, db

bp = Blueprint('api_producecategory', __name__, url_prefix='/api/producecategory')

# Get all produce category records
@bp.route('/', methods=['GET'])
def index():
    categories = ProduceCategory.query.all()
    categories_list = [
        {
            "id": category.id,
            "name": category.name,
            "date_created": category.date_created,
            "date_updated": category.date_updated,
            "created_by": category.created_by,
            "modified_by": category.modified_by
        }
        for category in categories
    ]
    return jsonify(categories=categories_list)

# Create a new produce category record
@bp.route('/create', methods=['POST'])
def create_category():
    data = request.json
    name = data.get('name')
    created_by = data.get('created_by')

    new_category = ProduceCategory(
        name=name,
        created_by=created_by,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )

    db.session.add(new_category)
    db.session.commit()
    return jsonify({"msg": "Produce category created successfully!"}), 201

# Edit an existing produce category record
@bp.route('/<int:id>/edit', methods=['PUT'])
def edit_category(id):
    category = ProduceCategory.query.get_or_404(id)
    data = request.json

    category.name = data.get('name')
    category.modified_by = data.get('modified_by')
    category.date_updated = datetime.utcnow()

    db.session.commit()
    return jsonify({"msg": "Produce category updated successfully!"})

# Get a specific produce category record by id
@bp.route('/<int:id>', methods=['GET'])
def get_category(id):
    category = ProduceCategory.query.get_or_404(id)
    category_data = {
        'id': category.id,
        'name': category.name,
        'date_created': category.date_created,
        'date_updated': category.date_updated,
        'created_by': category.created_by,
        'modified_by': category.modified_by
    }
    return jsonify(category_data)

# Delete a produce category record
@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_category(id):
    category = ProduceCategory.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"msg": "Produce category deleted successfully!"})

# Optional: Get categories for a specific crop (if needed)
@bp.route('/getbycrop/<int:crop_id>', methods=['GET'])
def get_by_crop_id(crop_id):
    categories = ProduceCategory.query.join(Crop).filter(Crop.id == crop_id).all()
    if categories :
        categories_list = [
            {
                'id': category.id,
                'name': category.name,
                'date_created': category.date_created,
                'date_updated': category.date_updated
            } for category in categories
        ]
        return jsonify({
            'status': 'success',
            'categories': categories_list,
        })
    else:
        # Return an error message if no data is found
        return jsonify({
            'status': 'error',
            'message': 'No data found for the provided farm ID'
        }), 404
