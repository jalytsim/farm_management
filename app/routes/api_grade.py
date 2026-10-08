from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import Grade, Crop, CropVariety, User, db
from app.utils.grading_utils import applicable_grades

bp = Blueprint('api_grade', __name__, url_prefix='/api/grade')


# ── Helpers ──────────────────────────────────────────────────────────────────
def _current_user():
    identity = get_jwt_identity()
    user_id = identity['id'] if isinstance(identity, dict) else identity
    return User.query.get(user_id)


def _admin_only():
    user = _current_user()
    if not user or not user.is_admin:
        return None, (jsonify({"message": "Only administrators can manage grades."}), 403)
    return user, None


def _read_payload(grade, data, creating):
    crop_id = data.get('crop_id')
    if creating and not crop_id:
        return "Commodity is required."
    if crop_id:
        if not Crop.query.get(crop_id):
            return "Commodity not found."
        grade.crop_id = int(crop_id)

    # variety_id is optional: empty means the grade applies to every variety
    # of the commodity.
    if 'variety_id' in data:
        raw = data.get('variety_id')
        if raw in (None, '', 'null'):
            grade.variety_id = None
        else:
            variety = CropVariety.query.get(raw)
            if not variety:
                return "Variety not found."
            if variety.crop_id != grade.crop_id:
                return "That variety belongs to another commodity."
            grade.variety_id = variety.id

    grade_value = (data.get('grade_value') or '').strip()
    if not grade_value:
        return "Grade value is required."

    duplicate = Grade.query.filter(
        Grade.crop_id == grade.crop_id,
        db.func.lower(Grade.grade_value) == grade_value.lower(),
        Grade.id != (grade.id or 0),
    )
    duplicate = (duplicate.filter(Grade.variety_id == grade.variety_id) if grade.variety_id
                 else duplicate.filter(Grade.variety_id.is_(None)))
    if duplicate.first():
        scope = "this variety" if grade.variety_id else "this commodity"
        return f"The grade '{grade_value}' already exists for {scope}."

    grade.grade_value = grade_value
    grade.description = (data.get('description') or '').strip() or None
    if 'sort_order' in data:
        try:
            grade.sort_order = int(data.get('sort_order') or 0)
        except (TypeError, ValueError):
            return "Sort order must be a whole number."
    return None


# ── Read ─────────────────────────────────────────────────────────────────────
@bp.route('/', methods=['GET'])
@jwt_required()
def index():
    """?crop_id= filters by commodity · ?variety_id= by variety
    · ?scope=applicable returns shared + variety-specific rows."""
    crop_id = request.args.get('crop_id', type=int)
    variety_id = request.args.get('variety_id', type=int)

    if crop_id and request.args.get('scope') == 'applicable':
        grades = applicable_grades(crop_id, variety_id)
        return jsonify(grades=[g.to_dict() for g in grades])

    query = Grade.query
    if crop_id:
        query = query.filter_by(crop_id=crop_id)
    if variety_id:
        query = query.filter_by(variety_id=variety_id)
    grades = query.order_by(Grade.crop_id, Grade.sort_order, Grade.id).all()
    return jsonify(grades=[g.to_dict() for g in grades])


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_grade(id):
    return jsonify(Grade.query.get_or_404(id).to_dict())


@bp.route('/getbycrop/<int:crop_id>', methods=['GET'])
@jwt_required()
def get_by_crop_id(crop_id):
    """Grades usable for a delivery of this commodity. Pass ?variety_id= to add
    the ones specific to that variety. Response shape unchanged: the QR and
    receipt forms read res.data.status and res.data.grades."""
    variety_id = request.args.get('variety_id', type=int)
    grades = applicable_grades(crop_id, variety_id)
    if not grades:
        return jsonify({'status': 'error', 'message': 'No grade found for this commodity'}), 404
    return jsonify({'status': 'success', 'grades': [g.to_dict() for g in grades]})


@bp.route('/getbyvariety/<int:variety_id>', methods=['GET'])
@jwt_required()
def get_by_variety(variety_id):
    variety = CropVariety.query.get_or_404(variety_id)
    grades = applicable_grades(variety.crop_id, variety.id)
    return jsonify({'status': 'success', 'grades': [g.to_dict() for g in grades]})


# ── Write (admin only) ───────────────────────────────────────────────────────
@bp.route('/create', methods=['POST'])
@jwt_required()
def create_grade():
    user, denied = _admin_only()
    if denied:
        return denied

    data = request.get_json(silent=True) or {}
    grade = Grade(created_by=user.id, modified_by=user.id)
    error = _read_payload(grade, data, creating=True)
    if error:
        return jsonify({"message": error}), 400

    db.session.add(grade)
    db.session.commit()
    return jsonify({"message": "Grade created successfully!", "grade": grade.to_dict()}), 201


@bp.route('/<int:id>/edit', methods=['PUT'])
@jwt_required()
def edit_grade(id):
    user, denied = _admin_only()
    if denied:
        return denied

    grade = Grade.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    error = _read_payload(grade, data, creating=False)
    if error:
        db.session.rollback()
        return jsonify({"message": error}), 400

    grade.modified_by = user.id
    grade.date_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Grade updated successfully!", "grade": grade.to_dict()})


@bp.route('/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_grade(id):
    user, denied = _admin_only()
    if denied:
        return denied

    grade = Grade.query.get_or_404(id)
    db.session.delete(grade)          # its grading rules go with it
    db.session.commit()
    return jsonify({"message": "Grade deleted successfully!"})