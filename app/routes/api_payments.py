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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api_payments_bp = Blueprint('api_payments', __name__, url_prefix='/api/payments')

# ==================== PAIEMENTS MOBILE MONEY (NKUSU) ====================

@api_payments_bp.route('/initiate', methods=['POST'])
def initiate_payment():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        phone = data.get("phone_number")
        txn_id = data.get("txn_id")
        feature_name = data.get("feature_name")

        print("✅ Reçu:", {"phone": phone, "txn_id": txn_id, "feature_name": feature_name})

        if not phone or not txn_id or not feature_name:
            return jsonify({"error": "Missing required fields"}), 400

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

@api_payments_bp.route('/dpo/initiate', methods=['POST'])
def initiate_dpo_payment():
    try:
        print("\n" + "="*60)
        print("[DPO] 🚀 NOUVELLE REQUÊTE DE PAIEMENT DPO")
        print("="*60)
        
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity
        print(f"[DPO] User ID: {user_id}")

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        feature_name = data.get("feature_name")
        phone = data.get("phone_number", "")
        email = data.get("email", "")
        currency = data.get("currency", "UGX")
        
        print(f"[DPO] Feature: {feature_name}")
        print(f"[DPO] Phone: {phone}")
        print(f"[DPO] Email: {email}")
        print(f"[DPO] Currency: {currency}")
        
        if not feature_name:
            return jsonify({"error": "Missing feature_name"}), 400

        txn_id = f"DPO-{user_id or 'GUEST'}-{int(datetime.now().timestamp())}"
        print(f"[DPO] Generated TXN ID: {txn_id}")

        print(f"[DPO] Creating payment attempt...")
        payment, amount = create_payment_attempt(
            user_id=user_id if user_id else None,
            guest_phone_number=None if user_id else phone,
            feature_name=feature_name,
            txn_id=txn_id,
            payment_method='dpo',
            currency=currency
        )

        if not payment:
            print(f"[DPO] ❌ Failed to create payment: {amount}")
            return jsonify({"error": amount}), 400

        print(f"[DPO] ✅ Payment record created (ID: {payment.id})")
        print(f"[DPO] Amount: {amount} {currency}")

        dpo = DPOPayment()
        
        # URLs de redirection pour DPO (DPO ajoute automatiquement ?TransactionToken=XXX)
        # Utiliser l'URL de production avec HTTPS
        base_url = "https://www.nkusu.com/api"
        redirect_url = f"{base_url}/payments/payment/success"
        back_url = f"{base_url}/payments/payment/cancelled"

        print(f"[DPO] Redirect URL: {redirect_url}")
        print(f"[DPO] Back URL: {back_url}")

        print(f"[DPO] Calling DPO API to create token...")
        result = dpo.create_payment_token(
            amount=amount,
            currency=currency,
            reference=txn_id,
            redirect_url=redirect_url,
            back_url=back_url,
            customer_phone=phone,
            customer_email=email
        )

        print(f"[DPO] DPO API Response:")
        print(f"[DPO] - Success: {result.get('success')}")
        print(f"[DPO] - Error: {result.get('error')}")
        print(f"[DPO] - Payment URL: {result.get('payment_url')}")

        if result['success']:
            payment.dpo_trans_token = result['trans_token']
            payment.dpo_trans_ref = result['trans_ref']
            db.session.commit()

            print(f"[DPO] ✅✅✅ SUCCESS!")
            print(f"[DPO] Trans Token: {result['trans_token']}")
            print(f"[DPO] Payment URL: {result['payment_url']}")
            print("="*60 + "\n")

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
            print(f"[DPO] ❌❌❌ FAILURE!")
            print(f"[DPO] Error: {result['error']}")
            print(f"[DPO] Result Code: {result.get('result_code')}")
            print("="*60 + "\n")
            
            return jsonify({
                "success": False,
                "error": result['error'],
                "result_code": result.get('result_code'),
                "raw_response": result.get('raw')
            }), 400

    except Exception as e:
        print(f"[DPO] ❌ EXCEPTION: {str(e)}")
        traceback.print_exc()
        print("="*60 + "\n")
        return jsonify({"error": "Unexpected server error"}), 500


@api_payments_bp.route('/dpo/verify/<trans_token>', methods=['GET'])
def verify_dpo_payment(trans_token):
    try:
        print(f"\n[DPO VERIFY] Verifying token: {trans_token}")
        
        dpo = DPOPayment()
        verification = dpo.verify_payment(trans_token)
        
        print(f"[DPO VERIFY] Verification result: {verification}")
        
        payment = PaidFeatureAccess.query.filter_by(dpo_trans_token=trans_token).first()
        if payment:
            print(f"[DPO VERIFY] Found payment record (ID: {payment.id})")
            if verification['success'] and verification['status'] == 'verified':
                payment.payment_status = "success"
                db.session.commit()
                print(f"[DPO VERIFY] ✅ Payment marked as successful")
            else:
                print(f"[DPO VERIFY] ❌ Verification failed")
        else:
            print(f"[DPO VERIFY] ⚠️ No payment record found")
        
        return jsonify(verification), 200

    except Exception as e:
        print(f"[DPO VERIFY] ❌ Error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ==================== ROUTES COMMUNES ====================

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
            "amount": a.amount,
            "usage_left": a.usage_left,
            "expires": a.access_expires_at.isoformat() if a.access_expires_at else None
        }
        for a in results
    ])


# ==================== ROUTES DE REDIRECTION DPO ====================

@api_payments_bp.route('/payment/success', methods=['GET'])
def dpo_payment_success():
    """Redirection après paiement DPO réussi"""
    trans_token = request.args.get('TransactionToken')
    print(f"[DPO REDIRECT] Success with token: {trans_token}")
    
    # Rediriger vers le frontend React
    frontend_url = "https://www.nkusu.com"
    return redirect(f"{frontend_url}/payment/success?TransactionToken={trans_token}")


@api_payments_bp.route('/payment/cancelled', methods=['GET'])
def dpo_payment_cancelled():
    """Redirection après annulation de paiement DPO"""
    trans_token = request.args.get('TransactionToken')
    print(f"[DPO REDIRECT] Cancelled with token: {trans_token}")
    
    # Rediriger vers le frontend React
    frontend_url = "https://www.nkusu.com"
    return redirect(f"{frontend_url}/payment/cancelled?TransactionToken={trans_token}")