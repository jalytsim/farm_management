from flask import Blueprint, jsonify, request
from app.models import ProduceCategory, db
from app.utils import producecategory_utils

bp = Blueprint('api_producecategory', __name__, url_prefix='/api/producecategory')

@bp.route('/', methods=['GET'])
def index():
    pcs = ProduceCategory.query.all()
    pcs_json = [
        {
            'id': pc.id,
            'name': pc.name,
            'grade': pc.grade,
            'created_by': pc.created_by,
            'modified_by': pc.modified_by,
            'date_created': pc.date_created,
            'date_updated': pc.date_updated
        } for pc in pcs
    ]
    return jsonify(pcs_json)

@bp.route('/create', methods=['POST'])
def create_pc():
    data = request.json
    name = data.get('name')
    grade = data.get('grade')
    created_by = data.get('created_by')  # You might want to retrieve this from the JWT or session in a real scenario
    modified_by = data.get('modified_by')  # Same here

    producecategory_utils.create_pc(name, grade, created_by=created_by, modified_by=modified_by)
    return jsonify({"msg": "Produce category created successfully!"}), 201

@bp.route('/<int:pc_id>/edit', methods=['PUT'])
def edit_pc(pc_id):
    pc = ProduceCategory.query.get_or_404(pc_id)
    data = request.json

    name = data.get('name')
    grade = data.get('grade')
    modified_by = data.get('modified_by')  # Same here

    producecategory_utils.update_pc(pc, name, grade, modified_by=modified_by)
    return jsonify({"msg": "Produce category updated successfully!"})

@bp.route('/<int:pc_id>', methods=['GET'])
def get_pc(pc_id):
    pc = ProduceCategory.query.get_or_404(pc_id)
    pc_json = {
        'id': pc.id,
        'name': pc.name,
        'grade': pc.grade,
        'created_by': pc.created_by,
        'modified_by': pc.modified_by,
        'date_created': pc.date_created,
        'date_updated': pc.date_updated
    }
    return jsonify(pc_json)

@bp.route('/<int:pc_id>/delete', methods=['DELETE'])
def delete_pc(pc_id):
    pc = ProduceCategory.query.get_or_404(pc_id)
    producecategory_utils.delete_pc(pc)
    return jsonify({"msg": "Produce category deleted successfully!"})
