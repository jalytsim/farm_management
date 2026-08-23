import logging
import traceback
from datetime import datetime

import requests
from flask import Blueprint, request, jsonify, redirect, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required

from app.utils.feature_payment_utils import (
    create_payment_attempt,
    has_user_access,
    has_guest_access,
    consume_feature_usage
)
from app.models import PaidFeatureAccess, db
from app.utils.dpo_payment import DPOPayment

logger = logging.getLogger(__name__)

api_payments_bp = Blueprint('api_payments', __name__, url_prefix='/api/payments')


def _get_current_user_id():
    """Récupère l'ID utilisateur depuis le JWT si présent, sinon None (mode invité)."""
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return identity['id'] if isinstance(identity, dict) else identity
    except Exception as e:
        logger.debug("No valid JWT, continuing as guest: %s", e)
        return None


# ==================== PAIEMENTS MOBILE MONEY (NKUSU) ====================

@api_payments_bp.route('/initiate', methods=['POST'])
def initiate_payment():
    user_id = _get_current_user_id()
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    phone = data.get("phone_number")
    txn_id = data.get("txn_id")
    feature_name = data.get("feature_name")
    currency = data.get("currency")

    if not phone or not txn_id or not feature_name:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        payment, amount_or_error = create_payment_attempt(
            user_id=user_id,
            guest_phone_number=None if user_id else phone,
            feature_name=feature_name,
            txn_id=txn_id,
            payment_method='mobile_money',
            currency=currency,
        )
    except Exception:
        logger.exception("create_payment_attempt failed")
        return jsonify({"error": "Internal server error"}), 500

    if not payment:
        return jsonify({"error": amount_or_error}), 400

    url = current_app.config["MOBILE_MONEY_API_URL"]
    verify_ssl = current_app.config["MOBILE_MONEY_VERIFY_SSL"]

    try:
        res = requests.post(
            url,
            params={"amount": amount_or_error, "msisdn": phone, "txnId": txn_id},
            verify=verify_ssl,
            timeout=15,
        )
    except requests.RequestException:
        logger.exception("Mobile money API call failed for txn %s", txn_id)
        return jsonify({"error": "Payment provider unreachable"}), 502

    return jsonify({
        "status": res.status_code,
        "msg": res.text,
        "amount": float(amount_or_error),
        "currency": payment.currency,
        "user_type": "logged_in" if user_id else "guest",
    }), res.status_code


@api_payments_bp.route('/status/<txn_id>', methods=['GET'])
def check_payment_status(txn_id):
    url = f"{current_app.config['MOBILE_MONEY_STATUS_URL']}/{txn_id}"
    verify_ssl = current_app.config["MOBILE_MONEY_VERIFY_SSL"]

    try:
        res = requests.get(url, verify=verify_ssl, timeout=15)
    except requests.RequestException:
        logger.exception("Status check failed for txn %s", txn_id)
        return jsonify({"error": "Payment provider unreachable"}), 502

    status_text = res.text.strip().lower()

    if status_text == "expired":
        logger.info("Status 'expired' ignoré pour %s (non pris en charge par le fournisseur).", txn_id)
        return jsonify({"status": "ignored"}), 200

    payment = PaidFeatureAccess.query.filter_by(txn_id=txn_id).first()
    if payment:
        if "success" in status_text or "confirmed" in status_text:
            payment.payment_status = "success"
        elif "failed" in status_text or "rejected" in status_text:
            payment.payment_status = "failed"
        elif "pending" in status_text:
            payment.payment_status = "pending"
        else:
            payment.payment_status = "unknown"

        db.session.commit()

    return jsonify({"status": status_text}), 200


# ==================== PAIEMENTS DPO PAY ====================

@api_payments_bp.route('/dpo/initiate', methods=['POST'])
def initiate_dpo_payment():
    user_id = _get_current_user_id()
    logger.info("[DPO] Nouvelle requête de paiement, user_id=%s", user_id or "GUEST")

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    feature_name = data.get("feature_name")
    phone = data.get("phone_number", "")
    email = data.get("email", "")
    currency = data.get("currency") or current_app.config["DEFAULT_CURRENCY"]

    if not feature_name:
        return jsonify({"error": "Missing feature_name"}), 400

    txn_id = f"DPO-{user_id or 'GUEST'}-{int(datetime.now().timestamp())}"

    try:
        payment, amount = create_payment_attempt(
            user_id=user_id,
            guest_phone_number=None if user_id else phone,
            feature_name=feature_name,
            txn_id=txn_id,
            payment_method='dpo',
            currency=currency,
        )
    except Exception:
        logger.exception("create_payment_attempt failed for DPO")
        return jsonify({"error": "Internal server error"}), 500

    if not payment:
        return jsonify({"error": amount}), 400

    dpo = DPOPayment()

    result = dpo.create_payment_token(
        amount=amount,
        currency=currency,
        reference=txn_id,
        redirect_url=current_app.config["DPO_REDIRECT_URL"],
        back_url=current_app.config["DPO_BACK_URL"],
        customer_phone=phone,
        customer_email=email,
    )

    if result['success']:
        payment.dpo_trans_token = result['trans_token']
        payment.dpo_trans_ref = result['trans_ref']
        db.session.commit()

        logger.info("[DPO] Token créé pour txn %s", txn_id)

        return jsonify({
            "success": True,
            "payment_url": result['payment_url'],
            "trans_token": result['trans_token'],
            "trans_ref": result['trans_ref'],
            "amount": float(amount),
            "currency": currency,
            "txn_id": txn_id,
        }), 200

    logger.warning("[DPO] Échec création token: %s", result.get('error'))
    return jsonify({
        "success": False,
        "error": result['error'],
        "result_code": result.get('result_code'),
        "raw_response": result.get('raw'),
    }), 400


@api_payments_bp.route('/dpo/verify/<trans_token>', methods=['GET'])
def verify_dpo_payment(trans_token):
    """
    Vérifie le statut d'un paiement DPO.
    Retourne toujours 202 (pending) sauf si le paiement est définitivement payé (200).
    Ne retourne jamais d'échec pour éviter les faux négatifs dus aux 429 ou erreurs temporaires.
    """
    payment = PaidFeatureAccess.query.filter_by(dpo_trans_token=trans_token).first()

    if not payment:
        return jsonify({
            "success": False,
            "status": "pending",
            "message": "Payment record not found yet",
        }), 202

    if payment.payment_status == "success":
        return jsonify({"success": True, "status": "paid", "message": "Payment already confirmed"}), 200

    dpo = DPOPayment()
    try:
        verification = dpo.verify_payment(trans_token)
    except Exception:
        logger.exception("DPO verify_payment failed for %s", trans_token)
        return jsonify({"success": False, "status": "pending", "message": "Verification error, will retry"}), 202

    if verification.get("success") and verification.get("status") == "verified":
        payment.payment_status = "success"
        payment.verified_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"success": True, "status": "paid"}), 200

    if verification.get("status") in ["error", "rate_limited"]:
        return jsonify({"success": False, "status": "pending", "message": "Temporary error, retrying later"}), 202

    return jsonify({"success": False, "status": "pending"}), 202


# ==================== ROUTES COMMUNES ====================

@api_payments_bp.route('/access/<feature_name>', methods=['GET'])
def check_access(feature_name):
    user_id = _get_current_user_id()
    phone = request.args.get("phone_number")

    if user_id:
        access = has_user_access(user_id, feature_name)
    elif phone:
        access = has_guest_access(phone, feature_name)
    else:
        return jsonify({"access": False, "reason": "Missing credentials"}), 400

    return jsonify({"access": access}), 200


@api_payments_bp.route('/consume/<feature_name>', methods=['POST'])
@jwt_required()
def consume_feature(feature_name):
    identity = get_jwt_identity()
    user_id = identity['id'] if isinstance(identity, dict) else identity

    success = consume_feature_usage(user_id, feature_name)
    if success:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Access denied or usage exceeded"}), 403


@api_payments_bp.route('/my-access', methods=['GET'])
@jwt_required()
def list_my_payments():
    identity = get_jwt_identity()
    user_id = identity['id'] if isinstance(identity, dict) else identity

    results = PaidFeatureAccess.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "feature": a.feature_name,
            "status": a.payment_status,
            "payment_method": a.payment_method,
            "currency": a.currency,
            "amount": float(a.amount) if a.amount is not None else None,
            "usage_left": a.usage_left,
            "expires": a.access_expires_at.isoformat() if a.access_expires_at else None,
        }
        for a in results
    ])


# ==================== ROUTES DE REDIRECTION DPO ====================

@api_payments_bp.route('/payment/success', methods=['GET'])
def dpo_payment_success():
    trans_token = request.args.get('TransactionToken')
    frontend_url = current_app.config["FRONTEND_URL"]

    if not trans_token:
        return redirect(f"{frontend_url}/payment/error?error=Missing+token")

    try:
        payment = PaidFeatureAccess.query.filter_by(dpo_trans_token=trans_token).first()

        if payment and payment.payment_status != "success":
            payment.payment_status = "success"
            payment.verified_at = datetime.utcnow()
            db.session.commit()

        return redirect(f"{frontend_url}/payment/success?TransactionToken={trans_token}")

    except Exception:
        logger.exception("dpo_payment_success failed for token %s", trans_token)
        return redirect(f"{frontend_url}/payment/error?error=Server+error")


@api_payments_bp.route('/payment/cancelled', methods=['GET'])
def dpo_payment_cancelled():
    trans_token = request.args.get('TransactionToken')
    frontend_url = current_app.config["FRONTEND_URL"]

    # Ne pas toucher au statut : le paiement peut encore réussir après annulation
    return redirect(f"{frontend_url}/payment/cancelled?TransactionToken={trans_token}")