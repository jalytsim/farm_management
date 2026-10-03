import logging
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from flask import current_app
from app.models import PaidFeatureAccess, FeaturePrice, db

logger = logging.getLogger(__name__)

# Libellés des fonctionnalités payantes connues ; sinon FeaturePrice.description,
# sinon le feature_name rendu lisible.
FEATURE_LABELS = {
    'report':            'Farm Report',
    'reportfarmer':      'Farmer Report',
    'reportcarbon':      'Carbon Report',
    'reportcarbonguest': 'Carbon Report',
    'reportndviguest':   'Satellite NDVI Report',
    'reporteudrguest':   'EUDR Compliance Report',
    'eudrsubmission':    'EUDR DDS Submission',
    'qrexport':          'QR Code Export',
}

PAYMENT_METHOD_LABELS = {
    'mobile_money': 'Mobile Money',
    'dpo':          'Card / DPO Pay',
}


def feature_label(feature_name, feature=None):
    if feature_name in FEATURE_LABELS:
        return FEATURE_LABELS[feature_name]
    if feature is not None and feature.description and len(feature.description) <= 60:
        return feature.description.strip()
    label = (feature_name or 'Unknown feature').replace('_', ' ').replace('-', ' ')
    if label.endswith('guest'):
        label = label[:-len('guest')]
    return label.strip().title()


def build_payment_narrative(feature_name, payment_method, amount, currency, txn_id,
                            user_id=None, guest_phone_number=None, feature=None):
    """
    Ex: "Satellite NDVI Report - guest access (+256700000000) - Mobile Money - 15,000.00 UGX - Ref 123"
    Permet de savoir, dans la base comme chez le prestataire, quel type de
    paiement a été fait sans devoir décoder feature_name/txn_id.
    """
    who = f"user #{user_id}" if user_id else (
        f"guest access ({guest_phone_number})" if guest_phone_number else "guest access")
    parts = [
        feature_label(feature_name, feature),
        who,
        PAYMENT_METHOD_LABELS.get(payment_method, (payment_method or '').replace('_', ' ').title()),
        f"{float(amount):,.2f} {currency}" if amount is not None else currency,
        f"Ref {txn_id}" if txn_id else None,
    ]
    return " - ".join(p for p in parts if p)[:255]


def payment_narrative(access, features_by_name=None):
    """
    Narrative stockée, ou reconstruite pour les paiements antérieurs à la colonne.
    features_by_name : {feature_name: FeaturePrice} préchargé pour éviter une
    requête par ligne dans les listes.
    """
    if access.narrative:
        return access.narrative
    if features_by_name is not None:
        feature = features_by_name.get(access.feature_name)
    else:
        feature = FeaturePrice.query.filter_by(feature_name=access.feature_name).first()
    return build_payment_narrative(
        access.feature_name, access.payment_method, access.amount, access.currency,
        access.txn_id, user_id=access.user_id, guest_phone_number=access.guest_phone_number,
        feature=feature,
    )


def create_payment_attempt(user_id=None, guest_phone_number=None, feature_name=None,
                            txn_id=None, payment_method='mobile_money', currency=None,
                            agent_id=None):
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
        agent_id=str(agent_id)[:100] if agent_id else None,
        narrative=build_payment_narrative(
            feature_name, payment_method, amount, currency, txn_id,
            user_id=user_id, guest_phone_number=guest_phone_number, feature=feature,
        ),
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