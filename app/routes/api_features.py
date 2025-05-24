from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import db, PaidFeatureAccess, FeaturePrice

api_feature_bp = Blueprint('api_feature', __name__, url_prefix='/api/feature')

# ---------------------- FeaturePrice Endpoints ----------------------

@api_feature_bp.route('/price/', methods=['GET'])
def get_all_feature_prices():
    features = FeaturePrice.query.all()
    return jsonify([
    {
        "id": f.id,
        "feature_name": f.feature_name,
        "price": f.price,
        "duration_days": f.duration_days,
        "usage_limit": f.usage_limit
    } for f in features
    ])


@api_feature_bp.route('/price/create', methods=['POST'])
def create_feature_price():
    data = request.json
    new_feature = FeaturePrice(
        feature_name=data['feature_name'],
        price=data['price'],
        duration_days=data.get('duration_days'),
        usage_limit=data.get('usage_limit')
    )
    db.session.add(new_feature)
    db.session.commit()
    return jsonify({"msg": "Feature price created successfully."}), 201

@api_feature_bp.route('/price/<int:id>/edit', methods=['PUT'])
def edit_feature_price(id):
    feature = FeaturePrice.query.get_or_404(id)
    data = request.json
    feature.feature_name = data.get('feature_name', feature.feature_name)
    feature.price = data.get('price', feature.price)
    feature.duration_days = data.get('duration_days', feature.duration_days)
    feature.usage_limit = data.get('usage_limit', feature.usage_limit)
    db.session.commit()
    return jsonify({"msg": "Feature price updated successfully."})

@api_feature_bp.route('/price/<int:id>', methods=['GET'])
def get_feature_price(id):
    feature = FeaturePrice.query.get_or_404(id)
    return jsonify({
        "id": feature.id,
        "feature_name": feature.feature_name,
        "price": feature.price,
        "duration_days": feature.duration_days,
        "usage_limit": feature.usage_limit
    })

@api_feature_bp.route('/price/<int:id>/delete', methods=['DELETE'])
def delete_feature_price(id):
    feature = FeaturePrice.query.get_or_404(id)
    db.session.delete(feature)
    db.session.commit()
    return jsonify({"msg": "Feature price deleted successfully."})

# ---------------------- PaidFeatureAccess Endpoints ----------------------

@api_feature_bp.route('/access/', methods=['GET'])
def get_all_access():
    accesses = PaidFeatureAccess.query.all()
    return jsonify([
        {
            "id": a.id,
            "user_id": a.user_id,
            "guest_phone_number": a.guest_phone_number,
            "feature_name": a.feature_name,
            "txn_id": a.txn_id,
            "payment_status": a.payment_status,
            "created_at": a.created_at.isoformat(),
            "access_expires_at": a.access_expires_at.isoformat() if a.access_expires_at else None,
            "usage_left": a.usage_left
        } for a in accesses
    ])

@api_feature_bp.route('/access/create', methods=['POST'])
def create_access():
    data = request.json
    new_access = PaidFeatureAccess(
        user_id=data.get('user_id'),
        guest_phone_number=data.get('guest_phone_number'),
        feature_name=data['feature_name'],
        txn_id=data['txn_id'],
        payment_status=data.get('payment_status', 'pending'),
        created_at=datetime.utcnow(),
        access_expires_at=data.get('access_expires_at'),
        usage_left=data.get('usage_left')
    )
    db.session.add(new_access)
    db.session.commit()
    return jsonify({"msg": "Access created successfully."}), 201

@api_feature_bp.route('/access/<int:id>/edit', methods=['PUT'])
def edit_access(id):
    access = PaidFeatureAccess.query.get_or_404(id)
    data = request.json
    access.user_id = data.get('user_id', access.user_id)
    access.guest_phone_number = data.get('guest_phone_number', access.guest_phone_number)
    access.feature_name = data.get('feature_name', access.feature_name)
    access.txn_id = data.get('txn_id', access.txn_id)
    access.payment_status = data.get('payment_status', access.payment_status)
    access.access_expires_at = data.get('access_expires_at', access.access_expires_at)
    access.usage_left = data.get('usage_left', access.usage_left)
    db.session.commit()
    return jsonify({"msg": "Access updated successfully."})

@api_feature_bp.route('/access/<int:id>', methods=['GET'])
def get_access(id):
    access = PaidFeatureAccess.query.get_or_404(id)
    return jsonify({
        "id": access.id,
        "user_id": access.user_id,
        "guest_phone_number": access.guest_phone_number,
        "feature_name": access.feature_name,
        "txn_id": access.txn_id,
        "payment_status": access.payment_status,
        "created_at": access.created_at.isoformat(),
        "access_expires_at": access.access_expires_at.isoformat() if access.access_expires_at else None,
        "usage_left": access.usage_left
    })

@api_feature_bp.route('/access/<int:id>/delete', methods=['DELETE'])
def delete_access(id):
    access = PaidFeatureAccess.query.get_or_404(id)
    db.session.delete(access)
    db.session.commit()
    return jsonify({"msg": "Access deleted successfully."})
