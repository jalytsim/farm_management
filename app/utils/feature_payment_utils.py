from datetime import datetime, timedelta
from app.models import PaidFeatureAccess, FeaturePrice, db

def create_payment_attempt(user_id=None, guest_phone_number=None, feature_name=None, txn_id=None):
    """Crée une tentative de paiement avec configuration automatique"""
    feature = FeaturePrice.query.filter_by(feature_name=feature_name).first()
    if not feature:
        return None, "Unknown feature"

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
        usage_left=feature.usage_limit
    )

    db.session.add(new_payment)
    db.session.commit()
    return new_payment, feature.price



def has_user_access(user_id, feature_name):
    now = datetime.utcnow()
    access = PaidFeatureAccess.query.filter_by(
        user_id=user_id,
        feature_name=feature_name,
        payment_status="success"
    ).filter(
        (PaidFeatureAccess.access_expires_at == None) | (PaidFeatureAccess.access_expires_at > now),
        (PaidFeatureAccess.usage_left == None) | (PaidFeatureAccess.usage_left > 0)
    ).first()
    return access is not None


def consume_feature_usage(user_id, feature_name):
    access = PaidFeatureAccess.query.filter_by(
        user_id=user_id,
        feature_name=feature_name,
        payment_status="success"
    ).filter(
        (PaidFeatureAccess.usage_left == None) | (PaidFeatureAccess.usage_left > 0)
    ).order_by(PaidFeatureAccess.created_at.desc()).first()

    if not access:
        return False

    if access.usage_left:
        access.usage_left -= 1
        db.session.commit()

    return True


def has_guest_access(phone, feature_name):
    now = datetime.utcnow()
    access = PaidFeatureAccess.query.filter_by(
        guest_phone_number=phone,
        feature_name=feature_name,
        payment_status="success"
    ).filter(
        (PaidFeatureAccess.access_expires_at == None) | (PaidFeatureAccess.access_expires_at > now),
        (PaidFeatureAccess.usage_left == None) | (PaidFeatureAccess.usage_left > 0)
    ).first()
    return access is not None
