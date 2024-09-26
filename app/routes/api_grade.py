from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import Grade, db

bp = Blueprint('api_grade', __name__, url_prefix='/api/grade')

# Get all grade records
@bp.route('/', methods=['GET'])
def index():
    grades = Grade.query.all()
    grades_list = [
        {
            "id": grade.id,
            "crop_id": grade.crop_id,
            "grade_value": grade.grade_value,
            "description": grade.description,
            "date_created": grade.date_created,
            "date_updated": grade.date_updated
        }
        for grade in grades
    ]
    return jsonify(grades=grades_list)

# Create a new grade record
@bp.route('/create', methods=['POST'])
def create_grade():
    data = request.json
    crop_id = data.get('crop_id')
    grade_value = data.get('grade_value')
    description = data.get('description', None)

    new_grade = Grade(
        crop_id=crop_id,
        grade_value=grade_value,
        description=description,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )

    db.session.add(new_grade)
    db.session.commit()
    return jsonify({"msg": "Grade created successfully!"}), 201

# Edit an existing grade record
@bp.route('/<int:id>/edit', methods=['PUT'])
def edit_grade(id):
    grade = Grade.query.get_or_404(id)
    data = request.json

    grade.crop_id = data.get('crop_id')
    grade.grade_value = data.get('grade_value')
    grade.description = data.get('description', None)
    grade.date_updated = datetime.utcnow()

    db.session.commit()
    return jsonify({"msg": "Grade updated successfully!"})

# Get a specific grade record by id
@bp.route('/<int:id>', methods=['GET'])
def get_grade(id):
    grade = Grade.query.get_or_404(id)
    grade_data = {
        'id': grade.id,
        'crop_id': grade.crop_id,
        'grade_value': grade.grade_value,
        'description': grade.description,
        'date_created': grade.date_created,
        'date_updated': grade.date_updated
    }
    return jsonify(grade_data)

# Delete a grade record
@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_grade(id):
    grade = Grade.query.get_or_404(id)
    db.session.delete(grade)
    db.session.commit()
    return jsonify({"msg": "Grade deleted successfully!"})

@bp.route('/getbycrop/<int:crop_id>' methods=['GET'])
def get_by_crop_id(crop_id):
    grades = Grade.query.filter_by(crop_id=crop_id).all()
    grades_list = [
        {
            'id': grade.id,
            'crop_id': grade.crop_id,
            'grade_value': grade.grade_value,
            'description': grade.description,
            'date_created': grade.date_created,
            'date_updated': grade.date_updated

        } for grade in grades
    ]
    return jsonify({
        'grades': grades_list,
    })


