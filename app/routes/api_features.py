import logging
from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import db, PaidFeatureAccess, FeaturePrice, FeaturePriceCurrency

logger = logging.getLogger(__name__)
api_feature_bp = Blueprint('api_feature', __name__, url_prefix='/api/feature')


def _sync_prices(feature, prices_dict):
    """Remplace les prix de la feature. Retourne les devises valides après sync
    (ne pas relire feature.prices : peut être obsolète sans refresh session)."""
    if prices_dict is None:
        return {p.currency for p in feature.prices}

    incoming = {c.upper(): amt for c, amt in prices_dict.items() if amt not in (None, '')}

    for existing in list(feature.prices):
        if existing.currency not in incoming:
            db.session.delete(existing)

    current_by_currency = {p.currency: p for p in feature.prices}
    for currency, amount in incoming.items():
        if currency in current_by_currency:
            current_by_currency[currency].price = amount
        else:
            db.session.add(FeaturePriceCurrency(
                feature_price_id=feature.id, currency=currency, price=amount
            ))

    return set(incoming.keys())


# ---------------------- FeaturePrice Endpoints ----------------------

@api_feature_bp.route('/price/', methods=['GET'])
def get_all_feature_prices():
    features = FeaturePrice.query.all()
    return jsonify([f.to_dict() for f in features])


@api_feature_bp.route('/price/<int:id>', methods=['GET'])
def get_feature_price(id):
    feature = FeaturePrice.query.get_or_404(id)
    return jsonify(feature.to_dict())


@api_feature_bp.route('/price/create', methods=['POST'])
def create_feature_price():
    data = request.get_json(silent=True) or {}

    feature_name = data.get('feature_name')
    prices = data.get('prices')

    if not feature_name:
        return jsonify({"error": "feature_name is required"}), 400
    if not prices or not isinstance(prices, dict) or len(prices) == 0:
        return jsonify({"error": "At least one currency price is required"}), 400
    if FeaturePrice.query.filter_by(feature_name=feature_name).first():
        return jsonify({"error": "A feature with this name already exists"}), 409

    normalized_prices = {c.upper(): v for c, v in prices.items()}
    default_currency = (data.get('default_currency') or next(iter(normalized_prices))).upper()
    if default_currency not in normalized_prices:
        return jsonify({"error": "default_currency must be one of the provided prices"}), 400

    new_feature = FeaturePrice(
        feature_name=feature_name,
        duration_days=data.get('duration_days') or None,
        usage_limit=data.get('usage_limit') or None,
        description=data.get('description'),
        default_currency=default_currency,
    )
    db.session.add(new_feature)
    db.session.flush()

    _sync_prices(new_feature, normalized_prices)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Failed to create feature price for %s", feature_name)
        return jsonify({"error": "Failed to create feature price"}), 500

    return jsonify(new_feature.to_dict()), 201


@api_feature_bp.route('/price/<int:id>/edit', methods=['PUT'])
def edit_feature_price(id):
    feature = FeaturePrice.query.get_or_404(id)
    data = request.get_json(silent=True) or {}

    new_name = data.get('feature_name')
    if new_name and new_name != feature.feature_name:
        if FeaturePrice.query.filter(
            FeaturePrice.feature_name == new_name,
            FeaturePrice.id != id
        ).first():
            return jsonify({"error": "A feature with this name already exists"}), 409
        feature.feature_name = new_name

    feature.duration_days = data.get('duration_days', feature.duration_days)
    feature.usage_limit = data.get('usage_limit', feature.usage_limit)
    feature.description = data.get('description', feature.description)

    prices = data.get('prices')
    if prices is not None:
        if not isinstance(prices, dict) or len(prices) == 0:
            return jsonify({"error": "At least one currency price is required"}), 400
        valid_currencies = _sync_prices(feature, {c.upper(): v for c, v in prices.items()})
    else:
        valid_currencies = {p.currency for p in feature.prices}

    default_currency = data.get('default_currency')
    if default_currency:
        default_currency = default_currency.upper()
        if default_currency not in valid_currencies:
            return jsonify({"error": "default_currency must be one of the configured prices"}), 400
        feature.default_currency = default_currency
    elif feature.default_currency not in valid_currencies and valid_currencies:
        feature.default_currency = next(iter(valid_currencies))

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Failed to update feature price %s", id)
        return jsonify({"error": "Failed to update feature price"}), 500

    return jsonify(feature.to_dict())


@api_feature_bp.route('/price/<int:id>/delete', methods=['DELETE'])
def delete_feature_price(id):
    feature = FeaturePrice.query.get_or_404(id)
    db.session.delete(feature)
    db.session.commit()
    return jsonify({"msg": "Feature price deleted successfully."})


# ---------------------- PaidFeatureAccess Endpoints ----------------------

@api_feature_bp.route('/access/', methods=['GET'])
def get_all_access():
    accesses = PaidFeatureAccess.query.order_by(PaidFeatureAccess.created_at.desc()).all()
    return jsonify([
        {
            "id": a.id,
            "user_id": a.user_id,
            "guest_phone_number": a.guest_phone_number,
            "feature_name": a.feature_name,
            "txn_id": a.txn_id,
            "payment_status": a.payment_status,
            "payment_method": a.payment_method,
            "currency": a.currency,
            "amount": float(a.amount) if a.amount is not None else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "access_expires_at": a.access_expires_at.isoformat() if a.access_expires_at else None,
            "usage_left": a.usage_left,
        } for a in accesses
    ])


@api_feature_bp.route('/access/<int:id>', methods=['GET'])
def get_access(id):
    a = PaidFeatureAccess.query.get_or_404(id)
    return jsonify({
        "id": a.id,
        "user_id": a.user_id,
        "guest_phone_number": a.guest_phone_number,
        "feature_name": a.feature_name,
        "txn_id": a.txn_id,
        "payment_status": a.payment_status,
        "payment_method": a.payment_method,
        "currency": a.currency,
        "amount": float(a.amount) if a.amount is not None else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "access_expires_at": a.access_expires_at.isoformat() if a.access_expires_at else None,
        "usage_left": a.usage_left,
    })


@api_feature_bp.route('/access/create', methods=['POST'])
def create_access():
    data = request.get_json(silent=True) or {}
    if not data.get('feature_name') or not data.get('txn_id'):
        return jsonify({"error": "feature_name and txn_id are required"}), 400
    if not data.get('user_id') and not data.get('guest_phone_number'):
        return jsonify({"error": "Provide either user_id or guest_phone_number"}), 400

    new_access = PaidFeatureAccess(
        user_id=data.get('user_id') or None,
        guest_phone_number=data.get('guest_phone_number') or None,
        feature_name=data['feature_name'],
        txn_id=data['txn_id'],
        payment_status=data.get('payment_status', 'pending'),
        created_at=datetime.utcnow(),
        access_expires_at=data.get('access_expires_at') or None,
        usage_left=data.get('usage_left') or None,
        payment_method=data.get('payment_method', 'mobile_money'),
        currency=data.get('currency', 'UGX'),
        amount=data.get('amount'),
    )

    db.session.add(new_access)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Failed to create access record for txn %s", data.get('txn_id'))
        return jsonify({"error": "This transaction ID may already exist, or the record is invalid."}), 400

    return jsonify({"msg": "Access created successfully.", "id": new_access.id}), 201


@api_feature_bp.route('/access/<int:id>/edit', methods=['PUT'])
def edit_access(id):
    access = PaidFeatureAccess.query.get_or_404(id)
    data = request.get_json(silent=True) or {}

    access.user_id = data.get('user_id', access.user_id)
    access.guest_phone_number = data.get('guest_phone_number', access.guest_phone_number)
    access.feature_name = data.get('feature_name', access.feature_name)
    access.txn_id = data.get('txn_id', access.txn_id)
    access.payment_status = data.get('payment_status', access.payment_status)
    access.access_expires_at = data.get('access_expires_at', access.access_expires_at)
    access.usage_left = data.get('usage_left', access.usage_left)
    access.currency = data.get('currency', access.currency)
    if 'amount' in data:
        access.amount = data.get('amount')

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Failed to update access record %s", id)
        return jsonify({"error": "Failed to update access record"}), 500

    return jsonify({"msg": "Access updated successfully."})


@api_feature_bp.route('/access/<int:id>/delete', methods=['DELETE'])
def delete_access(id):
    access = PaidFeatureAccess.query.get_or_404(id)
    db.session.delete(access)
    db.session.commit()
    return jsonify({"msg": "Access deleted successfully."})