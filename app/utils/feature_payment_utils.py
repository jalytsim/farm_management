import logging
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from flask import current_app
from app.models import PaidFeatureAccess, FeaturePrice, db

logger = logging.getLogger(__name__)


def create_payment_attempt(user_id=None, guest_phone_number=None, feature_name=None,
                            txn_id=None, payment_method='mobile_money', currency=None):
    supported = current_app.config.get("SUPPORTED_CURRENCIES", ["UGX"])
    default_currency = current_app.config.get("DEFAULT_CURRENCY", "UGX")

    currency = (currency or default_currency).upper()
    if currency not in supported:
        return None, f"Unsupported currency: {currency}"

    feature = FeaturePrice.query.filter_by(feature_name=feature_name).first()
    if not feature:
        return None, "Unknown feature"

    # feature.price n'existe plus depuis la migration multi-devises.
    # price_for() cherche dans FeaturePriceCurrency pour cette devise,
    # et retombe sur default_currency si elle n'y est pas configurée.
    amount = feature.price_for(currency)
    if amount is None:
        return None, f"No price configured for '{feature_name}' in {currency}"

    access_expires_at = (
        datetime.utcnow() + timedelta(days=feature.duration_days)
        if feature.duration_days else None
    )

    new_payment = PaidFeatureAccess(
        user_id=user_id,
        guest_phone_number=guest_phone_number,
        feature_name=feature_name,
        txn_id=txn_id,
        payment_status="pending",
        access_expires_at=access_expires_at,
        usage_left=feature.usage_limit,
        payment_method=payment_method,
        currency=currency,
        amount=amount,
    )

    db.session.add(new_payment)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        logger.warning("Duplicate txn_id attempted: %s", txn_id)
        return None, "This transaction ID has already been used."

    return new_payment, amount


def _has_active_access(condition):
    now = datetime.utcnow()
    return db.session.query(PaidFeatureAccess.id).filter(
        condition,
        PaidFeatureAccess.payment_status == "success",
        or_(PaidFeatureAccess.access_expires_at.is_(None),
            PaidFeatureAccess.access_expires_at > now),
        or_(PaidFeatureAccess.usage_left.is_(None),
            PaidFeatureAccess.usage_left > 0),
    ).first() is not None


def has_user_access(user_id, feature_name):
    return _has_active_access(and_(
        PaidFeatureAccess.user_id == user_id,
        PaidFeatureAccess.feature_name == feature_name,
    ))


def has_guest_access(phone, feature_name):
    return _has_active_access(and_(
        PaidFeatureAccess.guest_phone_number == phone,
        PaidFeatureAccess.feature_name == feature_name,
    ))


def consume_feature_usage(user_id, feature_name):
    now = datetime.utcnow()
    access = PaidFeatureAccess.query.filter(
        PaidFeatureAccess.user_id == user_id,
        PaidFeatureAccess.feature_name == feature_name,
        PaidFeatureAccess.payment_status == "success",
        or_(PaidFeatureAccess.access_expires_at.is_(None),
            PaidFeatureAccess.access_expires_at > now),
        or_(PaidFeatureAccess.usage_left.is_(None),
            PaidFeatureAccess.usage_left > 0),
    ).order_by(PaidFeatureAccess.created_at.desc()).first()

    if not access:
        return False

    if access.usage_left is not None:
        access.usage_left -= 1

    db.session.commit()
    return True