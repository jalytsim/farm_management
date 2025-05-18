from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required
import requests

from app.utils.feature_payment_utils import (
    create_payment_attempt,
    has_user_access,
    has_guest_access,
    consume_feature_usage
)
from app.models import db

api_payments_bp = Blueprint('api_payments', __name__, url_prefix='/api/payments')


# 1️⃣ INITIER PAIEMENT (utilisateur connecté ou invité)
@api_payments_bp.route('/initiate', methods=['POST'])
def initiate_payment():
    verify_jwt_in_request(optional=True)
    user_id = get_jwt_identity()

    data = request.get_json()
    phone = data.get("phone_number")
    txn_id = data.get("txn_id")
    feature_name = data.get("feature_name")

    if not phone or not txn_id or not feature_name:
        return jsonify({"error": "Missing required fields"}), 400

    # Crée la tentative de paiement
    payment, amount_or_error = create_payment_attempt(
        user_id=user_id if user_id else None,
        guest_phone_number=None if user_id else phone,
        feature_name=feature_name,
        txn_id=txn_id
    )

    if not payment:
        return jsonify({"error": amount_or_error}), 400

    # Appel de l'API externe de paiement
    url = f"https://188.166.125.28/nkusu-iot/api/nkusu-iot/payments?amount={amount_or_error}&msisdn={phone}&txnId={txn_id}"
    try:
        res = requests.post(url)
        return jsonify({
            "status": res.status_code,
            "msg": res.text,
            "amount": amount_or_error,
            "user_type": "logged_in" if user_id else "guest"
        }), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 2️⃣ VÉRIFIER STATUT PAIEMENT PAR txn_id
@api_payments_bp.route('/status/<txn_id>', methods=['GET'])
def check_payment_status(txn_id):
    try:
        url = f"https://188.166.125.28/nkusu-iot/api/nkusu-iot/payments/{txn_id}"
        res = requests.get(url)
        return jsonify({"status": res.text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 3️⃣ VÉRIFIER SI ACCÈS EST ACTIF (connecté ou invité)
@api_payments_bp.route('/access/<feature_name>', methods=['GET'])
def check_access(feature_name):
    verify_jwt_in_request(optional=True)
    user_id = get_jwt_identity()
    phone = request.args.get("phone_number")

    if user_id:
        has_access = has_user_access(user_id, feature_name)
    elif phone:
        has_access = has_guest_access(phone, feature_name)
    else:
        return jsonify({"access": False, "reason": "Missing credentials"}), 400

    return jsonify({"access": has_access}), 200


# 4️⃣ CONSOMMER UNE UTILISATION D'UNE FONCTIONNALITÉ
@api_payments_bp.route('/consume/<feature_name>', methods=['POST'])
@jwt_required()
def consume_feature(feature_name):
    user_id = get_jwt_identity()
    success = consume_feature_usage(user_id, feature_name)
    if success:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Access denied or usage exceeded"}), 403


# 5️⃣ (optionnel) : LISTER LES PAIEMENTS D’UN UTILISATEUR
@api_payments_bp.route('/my-access', methods=['GET'])
@jwt_required()
def list_my_payments():
    user_id = get_jwt_identity()
    from app.models import PaidFeatureAccess
    results = PaidFeatureAccess.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "feature": a.feature_name,
            "status": a.payment_status,
            "usage_left": a.usage_left,
            "expires": a.access_expires_at.isoformat() if a.access_expires_at else None
        }
        for a in results
    ])
