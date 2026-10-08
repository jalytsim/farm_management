"""Turns quality measurements taken at the warehouse into a grade.

Scope rule, used everywhere below:
    variety_id = NULL  → the row applies to the whole commodity
    variety_id = <id>  → the row applies to that variety only

So grading a delivery of Coffee / Arabica uses the parameters and grades shared
by all coffee, plus those specific to Arabica. A variety-specific grade is
checked before a shared one when both have the same sort_order.
"""

from decimal import Decimal, InvalidOperation

from app.models import QualityParameter, Grade

OPERATORS = ('lte', 'gte', 'between', 'eq')
VALUE_TYPES = ('number', 'choice', 'boolean')

OPERATOR_LABELS = {
    'lte':     'at most',
    'gte':     'at least',
    'between': 'between',
    'eq':      'equals',
}


def _to_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def applicable_parameters(crop_id, variety_id=None):
    """Active parameters for this commodity, plus those of the variety."""
    query = QualityParameter.query.filter_by(crop_id=crop_id, is_active=True)
    if variety_id:
        query = query.filter(
            (QualityParameter.variety_id.is_(None)) | (QualityParameter.variety_id == variety_id))
    else:
        query = query.filter(QualityParameter.variety_id.is_(None))
    return query.order_by(QualityParameter.position, QualityParameter.id).all()


def applicable_grades(crop_id, variety_id=None):
    """Grades for this commodity, plus those of the variety.

    Variety-specific grades come first at equal sort_order: when a variety
    defines its own scale, it wins over the commodity-wide one.
    """
    query = Grade.query.filter_by(crop_id=crop_id)
    if variety_id:
        query = query.filter((Grade.variety_id.is_(None)) | (Grade.variety_id == variety_id))
    else:
        query = query.filter(Grade.variety_id.is_(None))
    grades = query.order_by(Grade.sort_order, Grade.id).all()
    return sorted(grades, key=lambda g: (g.sort_order or 0, 0 if g.variety_id else 1, g.id))


def _normalize(parameter, raw_value):
    """Returns (value, error). Numbers come back as Decimal, the rest as str."""
    if raw_value in (None, ''):
        return None, None
    if parameter.value_type == 'number':
        number = _to_decimal(raw_value)
        if number is None:
            return None, f"{parameter.name}: '{raw_value}' is not a number."
        return number, None
    if parameter.value_type == 'boolean':
        return ('yes' if str(raw_value).lower() in ('1', 'true', 'yes') else 'no'), None
    value = str(raw_value)
    if parameter.options and value not in parameter.options:
        return None, f"{parameter.name}: '{value}' is not an allowed option."
    return value, None


def _rule_passes(rule, value):
    if value is None:
        return False
    if rule.parameter.value_type == 'number':
        if rule.operator == 'lte':
            return rule.max_value is not None and value <= rule.max_value
        if rule.operator == 'gte':
            return rule.min_value is not None and value >= rule.min_value
        if rule.operator == 'between':
            return (rule.min_value is not None and rule.max_value is not None
                    and rule.min_value <= value <= rule.max_value)
        if rule.operator == 'eq':
            return rule.min_value is not None and value == rule.min_value
        return False
    return rule.expected_value is not None and str(value) == str(rule.expected_value)


def evaluate_grade(crop_id, measurements, variety_id=None):
    """measurements: {parameter_id: raw value}.

    Returns:
      accepted   False when a required value is missing or outside the accepted
                 range of its parameter — the delivery is rejected.
      grade      the best matching grade, or None when no rule set matches.
      errors     blocking problems.
      notes      non-blocking information.
    """
    measurements = {int(k): v for k, v in (measurements or {}).items()}
    parameters = applicable_parameters(crop_id, variety_id)

    errors, notes, values = [], [], {}

    for parameter in parameters:
        value, error = _normalize(parameter, measurements.get(parameter.id))
        if error:
            errors.append(error)
            continue
        if value is None:
            if parameter.is_required:
                errors.append(f"{parameter.name} is required.")
            continue
        if parameter.value_type == 'number':
            unit = f" {parameter.unit}" if parameter.unit else ''
            if parameter.min_value is not None and value < parameter.min_value:
                errors.append(f"{parameter.name}: {value}{unit} is below the accepted minimum "
                              f"({parameter.min_value}{unit}).")
            if parameter.max_value is not None and value > parameter.max_value:
                errors.append(f"{parameter.name}: {value}{unit} is above the accepted maximum "
                              f"({parameter.max_value}{unit}).")
        values[parameter.id] = value

    if errors:
        return {'accepted': False, 'grade': None, 'errors': errors, 'notes': notes}

    for grade in applicable_grades(crop_id, variety_id):
        rules = list(grade.rules)
        if not rules:
            continue
        if all(_rule_passes(rule, values.get(rule.parameter_id)) for rule in rules):
            return {'accepted': True, 'grade': grade.to_dict(), 'errors': [], 'notes': notes}

    notes.append("The measurements are acceptable but match no grade rule. "
                 "Set the grade manually or complete the grading rules.")
    return {'accepted': True, 'grade': None, 'errors': [], 'notes': notes}