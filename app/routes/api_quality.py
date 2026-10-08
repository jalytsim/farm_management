from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import QualityParameter, GradeRule, Grade, Crop, CropVariety, User, db
from app.utils.grading_utils import (
    evaluate_grade, applicable_parameters, applicable_grades, OPERATORS, VALUE_TYPES,
)

bp = Blueprint('api_quality', __name__, url_prefix='/api/quality')


# ── Helpers ──────────────────────────────────────────────────────────────────
def _current_user():
    identity = get_jwt_identity()
    user_id = identity['id'] if isinstance(identity, dict) else identity
    return User.query.get(user_id)


def _admin_only():
    user = _current_user()
    if not user or not user.is_admin:
        return None, (jsonify({"message": "Only administrators can manage quality settings."}), 403)
    return user, None


def _decimal_or_none(value, field):
    if value in (None, ''):
        return None, None
    try:
        return Decimal(str(value)), None
    except (InvalidOperation, ValueError):
        return None, f"{field} must be a number."


def _resolve_variety(crop_id, raw):
    """Returns (variety_id, error). Empty means: applies to every variety."""
    if raw in (None, '', 'null'):
        return None, None
    variety = CropVariety.query.get(raw)
    if not variety:
        return None, "Variety not found."
    if variety.crop_id != int(crop_id):
        return None, "That variety belongs to another commodity."
    return variety.id, None


# =============================================================================
#  QUALITY PARAMETERS  (moisture content, purity, defects…)
# =============================================================================
@bp.route('/parameters', methods=['GET'])
@jwt_required()
def list_parameters():
    """?crop_id= · ?variety_id= · ?scope=applicable (shared + variety-specific)
    · ?active=1"""
    crop_id = request.args.get('crop_id', type=int)
    variety_id = request.args.get('variety_id', type=int)

    if crop_id and request.args.get('scope') == 'applicable':
        return jsonify(parameters=[p.to_dict() for p in applicable_parameters(crop_id, variety_id)])

    query = QualityParameter.query
    if crop_id:
        query = query.filter_by(crop_id=crop_id)
    if variety_id:
        query = query.filter_by(variety_id=variety_id)
    if request.args.get('active') == '1':
        query = query.filter_by(is_active=True)

    parameters = query.order_by(QualityParameter.crop_id,
                                QualityParameter.position,
                                QualityParameter.id).all()
    return jsonify(parameters=[p.to_dict() for p in parameters])


def _read_parameter_payload(parameter, data, creating):
    if creating:
        crop_id = data.get('crop_id')
        if not crop_id:
            return "crop_id is required."
        if not Crop.query.get(crop_id):
            return "Commodity not found."
        parameter.crop_id = int(crop_id)

    if 'variety_id' in data or creating:
        variety_id, error = _resolve_variety(parameter.crop_id, data.get('variety_id'))
        if error:
            return error
        parameter.variety_id = variety_id

    name = (data.get('name') or '').strip()
    if not name:
        return "Parameter name is required."
    if len(name) > 100:
        return "Parameter name must be 100 characters or less."

    value_type = data.get('value_type', 'number')
    if value_type not in VALUE_TYPES:
        return f"value_type must be one of: {', '.join(VALUE_TYPES)}."

    duplicate = QualityParameter.query.filter(
        QualityParameter.crop_id == parameter.crop_id,
        db.func.lower(QualityParameter.name) == name.lower(),
        QualityParameter.id != (parameter.id or 0),
    )
    duplicate = (duplicate.filter(QualityParameter.variety_id == parameter.variety_id)
                 if parameter.variety_id
                 else duplicate.filter(QualityParameter.variety_id.is_(None)))
    if duplicate.first():
        scope = "this variety" if parameter.variety_id else "this commodity"
        return f"The parameter '{name}' already exists for {scope}."

    options = data.get('options') or []
    if value_type == 'choice':
        options = [str(o).strip() for o in options if str(o).strip()]
        if len(options) < 2:
            return "A choice parameter needs at least two options."
    else:
        options = []

    min_value, error = _decimal_or_none(data.get('min_value'), 'Minimum')
    if error:
        return error
    max_value, error = _decimal_or_none(data.get('max_value'), 'Maximum')
    if error:
        return error
    if value_type != 'number':
        min_value = max_value = None
    elif min_value is not None and max_value is not None and min_value > max_value:
        return "Minimum cannot be greater than maximum."

    parameter.name        = name
    parameter.unit        = (data.get('unit') or '').strip() or None
    parameter.value_type  = value_type
    parameter.options     = options
    parameter.min_value   = min_value
    parameter.max_value   = max_value
    parameter.is_required = bool(data.get('is_required', True))
    parameter.is_active   = bool(data.get('is_active', True))
    parameter.position    = int(data.get('position') or 0)
    return None


@bp.route('/parameters/create', methods=['POST'])
@jwt_required()
def create_parameter():
    user, denied = _admin_only()
    if denied:
        return denied

    data = request.get_json(silent=True) or {}
    parameter = QualityParameter(created_by=user.id, modified_by=user.id)
    error = _read_parameter_payload(parameter, data, creating=True)
    if error:
        return jsonify({"message": error}), 400

    db.session.add(parameter)
    db.session.commit()
    return jsonify({"message": "Quality parameter created.", "parameter": parameter.to_dict()}), 201


@bp.route('/parameters/<int:id>/edit', methods=['PUT'])
@jwt_required()
def edit_parameter(id):
    user, denied = _admin_only()
    if denied:
        return denied

    parameter = QualityParameter.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    error = _read_parameter_payload(parameter, data, creating=False)
    if error:
        db.session.rollback()
        return jsonify({"message": error}), 400

    parameter.modified_by  = user.id
    parameter.date_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Quality parameter updated.", "parameter": parameter.to_dict()})


@bp.route('/parameters/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_parameter(id):
    user, denied = _admin_only()
    if denied:
        return denied

    parameter = QualityParameter.query.get_or_404(id)
    if parameter.rules:
        return jsonify({"message": "This parameter is used by grading rules. "
                                   "Delete those rules first, or deactivate the parameter."}), 409

    db.session.delete(parameter)
    db.session.commit()
    return jsonify({"message": "Quality parameter deleted."})


# =============================================================================
#  GRADING RULES
# =============================================================================
@bp.route('/rules', methods=['GET'])
@jwt_required()
def list_rules():
    """?crop_id= (required) · ?variety_id= → the grades that apply, with rules."""
    crop_id = request.args.get('crop_id', type=int)
    variety_id = request.args.get('variety_id', type=int)
    if not crop_id:
        return jsonify({"message": "crop_id is required."}), 400

    grades = applicable_grades(crop_id, variety_id)
    return jsonify(grades=[{**g.to_dict(), 'rules': [r.to_dict() for r in g.rules]} for g in grades])


def _read_rule_payload(rule, data):
    grade = Grade.query.get(data.get('grade_id'))
    if not grade:
        return "Grade not found."
    parameter = QualityParameter.query.get(data.get('parameter_id'))
    if not parameter:
        return "Quality parameter not found."
    if parameter.crop_id != grade.crop_id:
        return "The parameter and the grade belong to different commodities."
    # A variety-specific parameter cannot drive a commodity-wide grade: the rule
    # would be unverifiable for the other varieties.
    if parameter.variety_id and grade.variety_id and parameter.variety_id != grade.variety_id:
        return "The parameter and the grade belong to different varieties."
    if parameter.variety_id and not grade.variety_id:
        return ("This parameter is specific to one variety, so it cannot be used by a grade "
                "that applies to the whole commodity.")

    duplicate = GradeRule.query.filter(
        GradeRule.grade_id == grade.id,
        GradeRule.parameter_id == parameter.id,
        GradeRule.id != (rule.id or 0),
    ).first()
    if duplicate:
        return f"A rule on '{parameter.name}' already exists for this grade."

    operator = data.get('operator')
    if operator not in OPERATORS:
        return f"operator must be one of: {', '.join(OPERATORS)}."

    min_value, error = _decimal_or_none(data.get('min_value'), 'Minimum')
    if error:
        return error
    max_value, error = _decimal_or_none(data.get('max_value'), 'Maximum')
    if error:
        return error
    expected = (data.get('expected_value') or '').strip() or None

    if parameter.value_type == 'number':
        if operator in ('gte', 'eq') and min_value is None:
            return "Enter the value this rule compares against."
        if operator == 'lte' and max_value is None:
            return "Enter the value this rule compares against."
        if operator == 'between':
            if min_value is None or max_value is None:
                return "A 'between' rule needs both a minimum and a maximum."
            if min_value > max_value:
                return "Minimum cannot be greater than maximum."
        expected = None
    else:
        if operator != 'eq':
            return "Non-numeric parameters only support the 'equals' operator."
        if not expected:
            return "Enter the expected value."
        if parameter.value_type == 'choice' and expected not in (parameter.options or []):
            return f"'{expected}' is not one of the parameter options."
        min_value = max_value = None

    rule.grade_id       = grade.id
    rule.parameter_id   = parameter.id
    rule.operator       = operator
    rule.min_value      = min_value
    rule.max_value      = max_value
    rule.expected_value = expected
    return None


@bp.route('/rules/create', methods=['POST'])
@jwt_required()
def create_rule():
    user, denied = _admin_only()
    if denied:
        return denied

    data = request.get_json(silent=True) or {}
    rule = GradeRule(created_by=user.id)
    error = _read_rule_payload(rule, data)
    if error:
        return jsonify({"message": error}), 400

    db.session.add(rule)
    db.session.commit()
    return jsonify({"message": "Grading rule created.", "rule": rule.to_dict()}), 201


@bp.route('/rules/<int:id>/edit', methods=['PUT'])
@jwt_required()
def edit_rule(id):
    user, denied = _admin_only()
    if denied:
        return denied

    rule = GradeRule.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    error = _read_rule_payload(rule, data)
    if error:
        db.session.rollback()
        return jsonify({"message": error}), 400

    db.session.commit()
    return jsonify({"message": "Grading rule updated.", "rule": rule.to_dict()})


@bp.route('/rules/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_rule(id):
    user, denied = _admin_only()
    if denied:
        return denied

    rule = GradeRule.query.get_or_404(id)
    db.session.delete(rule)
    db.session.commit()
    return jsonify({"message": "Grading rule deleted."})


# =============================================================================
#  EVALUATION — rule tester, and warehouse reception from step 5 on
# =============================================================================
@bp.route('/evaluate', methods=['POST'])
@jwt_required()
def evaluate():
    """Body: { "crop_id": 1, "variety_id": 3, "measurements": { "<id>": value } }"""
    data = request.get_json(silent=True) or {}
    crop_id = data.get('crop_id')
    if not crop_id:
        return jsonify({"message": "crop_id is required."}), 400
    if not Crop.query.get(crop_id):
        return jsonify({"message": "Commodity not found."}), 404

    variety_id, error = _resolve_variety(crop_id, data.get('variety_id'))
    if error:
        return jsonify({"message": error}), 400

    try:
        result = evaluate_grade(int(crop_id), data.get('measurements') or {}, variety_id)
    except (TypeError, ValueError):
        return jsonify({"message": "measurements must be an object keyed by parameter id."}), 400

    return jsonify(result)