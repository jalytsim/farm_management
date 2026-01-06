from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required
import requests
import traceback
import urllib3
from datetime import datetime

from app.utils.feature_payment_utils import (
    create_payment_attempt,
    has_user_access,
    has_guest_access,
    consume_feature_usage
)
from app.models import PaidFeatureAccess, db
from app.utils.dpo_payment import DPOPayment

# 🔒 Désactive les avertissements SSL (à ne pas faire en prod sans raison valable)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api_payments_bp = Blueprint('api_payments', __name__, url_prefix='/api/payments')

# ==================== PAIEMENTS MOBILE MONEY (NKUSU) ====================

# 1️⃣ INITIER UN PAIEMENT MOBILE MONEY
@api_payments_bp.route('/initiate', methods=['POST'])
def initiate_payment():
    try:
        # 🔓 JWT facultatif (utilisateur connecté ou invité)
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity

        # ✅ Lecture et validation du corps JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        phone = data.get("phone_number")
        txn_id = data.get("txn_id")
        feature_name = data.get("feature_name")

        print("✅ Reçu:", {"phone": phone, "txn_id": txn_id, "feature_name": feature_name})

        if not phone or not txn_id or not feature_name:
            return jsonify({"error": "Missing required fields"}), 400

        # 🧾 Création du paiement
        try:
            payment, amount_or_error = create_payment_attempt(
                user_id=user_id if user_id else None,
                guest_phone_number=None if user_id else phone,
                feature_name=feature_name,
                txn_id=txn_id,
                payment_method='mobile_money'
            )
        except Exception as e:
            print("[ERROR] create_payment_attempt:", str(e))
            traceback.print_exc()
            return jsonify({"error": "Internal server error (create_payment_attempt)"}), 500

        if not payment:
            print("[DEBUG] Échec création paiement:", amount_or_error)
            return jsonify({"error": amount_or_error}), 400

        # 🌐 Appel à l'API de paiement externe
        url = f"https://188.166.125.28/nkusu-iot/api/nkusu-iot/payments?amount={amount_or_error}&msisdn={phone}&txnId={txn_id}"
        print("🌐 Appel API paiement:", url)

        try:
            res = requests.post(url, verify=False)
            print("📨 Réponse API externe:", res.status_code, res.text)

            return jsonify({
                "status": res.status_code,
                "msg": res.text,
                "amount": amount_or_error,
                "user_type": "logged_in" if user_id else "guest"
            }), res.status_code

        except Exception as e:
            print("[ERROR] API externe paiement:", str(e))
            traceback.print_exc()
            return jsonify({"error": f"Payment API call failed: {str(e)}"}), 500

    except Exception as e:
        print("[ERROR] initiate_payment global:", str(e))
        traceback.print_exc()
        return jsonify({"error": "Unexpected server error"}), 500


# 2️⃣ VÉRIFIER LE STATUT D'UN PAIEMENT MOBILE MONEY
@api_payments_bp.route('/status/<txn_id>', methods=['GET'])
def check_payment_status(txn_id):
    try:
        url = f"https://188.166.125.28/nkusu-iot/api/nkusu-iot/payments/{txn_id}"
        res = requests.get(url, verify=False)

        status_text = res.text.strip().lower()
        print(f"[DEBUG] Status reçu pour {txn_id} : {status_text}")

        if status_text == "expired":
            print(f"[INFO] Statut 'expired' ignoré pour {txn_id} (non pris en charge par le fournisseur).")
            return jsonify({"status": "ignored"}), 200

        # 🔄 Mise à jour en BDD
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

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== PAIEMENTS DPO PAY ====================

# 3️⃣ INITIER UN PAIEMENT DPO
@api_payments_bp.route('/dpo/initiate', methods=['POST'])
def initiate_dpo_payment():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        feature_name = data.get("feature_name")
        phone = data.get("phone_number", "")
        email = data.get("email", "")
        currency = data.get("currency", "UGX")
        
        if not feature_name:
            return jsonify({"error": "Missing feature_name"}), 400

        # Générer un txn_id unique
        txn_id = f"DPO-{user_id or 'GUEST'}-{int(datetime.now().timestamp())}"

        # Créer la tentative de paiement
        payment, amount = create_payment_attempt(
            user_id=user_id if user_id else None,
            guest_phone_number=None if user_id else phone,
            feature_name=feature_name,
            txn_id=txn_id,
            payment_method='dpo',
            currency=currency
        )

        if not payment:
            return jsonify({"error": amount}), 400

        # Initialiser DPO
        dpo = DPOPayment()
        
        # 🔥 CORRECTION: URLs SANS placeholders - DPO ajoute TransactionToken automatiquement
        base_url = request.host_url.rstrip('/')
        redirect_url = f"{base_url}/payment/success"
        back_url = f"{base_url}/payment/cancelled"

        print(f"[DPO] Redirect URL: {redirect_url}")
        print(f"[DPO] Back URL: {back_url}")

        # Créer le token de paiement
        result = dpo.create_payment_token(
            amount=amount,
            currency=currency,
            reference=txn_id,
            redirect_url=redirect_url,
            back_url=back_url,
            customer_phone=phone,
            customer_email=email
        )

        if result['success']:
            # Stocker le trans_token dans la BDD pour vérification ultérieure
            payment.dpo_trans_token = result['trans_token']
            payment.dpo_trans_ref = result['trans_ref']
            db.session.commit()

            return jsonify({
                "success": True,
                "payment_url": result['payment_url'],
                "trans_token": result['trans_token'],
                "trans_ref": result['trans_ref'],
                "amount": amount,
                "currency": currency,
                "txn_id": txn_id
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 400

    except Exception as e:
        print("[ERROR] initiate_dpo_payment:", str(e))
        traceback.print_exc()
        return jsonify({"error": "Unexpected server error"}), 500


# 4️⃣ VÉRIFIER LE STATUT D'UN PAIEMENT DPO
@api_payments_bp.route('/dpo/verify/<trans_token>', methods=['GET'])
def verify_dpo_payment(trans_token):
    """Route API pour vérifier manuellement un paiement DPO"""
    try:
        dpo = DPOPayment()
        verification = dpo.verify_payment(trans_token)
        
        # Mettre à jour la BDD si trouvé
        payment = PaidFeatureAccess.query.filter_by(dpo_trans_token=trans_token).first()
        if payment and verification['success'] and verification['status'] == 'verified':
            payment.payment_status = "success"
            db.session.commit()
        
        return jsonify(verification), 200

    except Exception as e:
        print(f"[ERROR] verify_dpo_payment: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ==================== ROUTES COMMUNES ====================

# 5️⃣ VÉRIFIER L'ACCÈS À UNE FONCTIONNALITÉ
@api_payments_bp.route('/access/<feature_name>', methods=['GET'])
def check_access(feature_name):
    verify_jwt_in_request(optional=True)
    identity = get_jwt_identity()
    user_id = identity['id'] if isinstance(identity, dict) else identity
    phone = request.args.get("phone_number")

    if user_id:
        has_access = has_user_access(user_id, feature_name)
    elif phone:
        has_access = has_guest_access(phone, feature_name)
    else:
        return jsonify({"access": False, "reason": "Missing credentials"}), 400

    return jsonify({"access": has_access}), 200


# 6️⃣ CONSOMMER UNE UTILISATION D'UNE FONCTIONNALITÉ
@api_payments_bp.route('/consume/<feature_name>', methods=['POST'])
@jwt_required()
def consume_feature(feature_name):
    identity = get_jwt_identity()
    user_id = identity['id'] if isinstance(identity, dict) else identity

    success = consume_feature_usage(user_id, feature_name)
    if success:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Access denied or usage exceeded"}), 403


# 7️⃣ LISTER LES FONCTIONNALITÉS PAYÉES PAR L'UTILISATEUR
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
            "amount": a.amount,
            "usage_left": a.usage_left,
            "expires": a.access_expires_at.isoformat() if a.access_expires_at else None
        }
        for a in results
    ])