import time
from datetime import datetime
from decimal import Decimal, InvalidOperation

import requests
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import (
    WarehouseReceipt, WarehouseReceiptFarm, WarehouseReceiptMeasurement,
    Store, Crop, CropVariety, Grade, Farm, User, QualityParameter,
    FeaturePrice, PaidFeatureAccess,
    RECEIPT_STATUSES, DEPOSITOR_TYPES, OPEN_RECEIPT_STATUSES,
)
from app.utils.grading_utils import evaluate_grade, applicable_parameters
from app.utils.serials_utils import serial_from_id
from app.utils.feature_payment_utils import create_payment_attempt
from app.utils.dpo_payment import DPOPayment
from app.utils.site_url import on_site
from app.routes.api_qr import save_qr_in_db
from app.utils.warehouse_utils import log_movement

bp = Blueprint('api_receipt', __name__, url_prefix='/api/receipts')

RECEIPT_PREFIX = 'WR-'
ZERO = Decimal('0')

# Who may receive a delivery and issue a receipt.
RECEIVING_ROLES = {'admin', 'warehouse_operator', 'qa_tester'}

# ★ Vérification payante : le prix et la durée d'accès se règlent dans l'écran
#   Features (FeaturePrice 'receipt_verification'), comme pour les rapports.
VERIFICATION_FEATURE = 'receipt_verification'
# Chaque paiement est rattaché à UN reçu : son txn_id commence par ce préfixe.
VERIFICATION_TXN_PREFIX = 'WRV-'


# ── Helpers ──────────────────────────────────────────────────────────────────
def _current_user():
    identity = get_jwt_identity()
    user_id = identity['id'] if isinstance(identity, dict) else identity
    return User.query.get(user_id)


def _can_receive(user):
    return bool(user and (user.is_admin or user.user_type in RECEIVING_ROLES))


def _dec(value, field, minimum=None):
    """Returns (Decimal|None, error)."""
    if value in (None, ''):
        return None, None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None, f"{field} must be a number."
    if minimum is not None and number < minimum:
        return None, f"{field} must be at least {minimum}."
    return number, None


def warehouse_stock_kg(store_id):
    """Weight still held in the warehouse: everything issued and not yet released."""
    rows = (db.session.query(
        db.func.coalesce(db.func.sum(WarehouseReceipt.net_weight_kg
                                     - WarehouseReceipt.released_weight_kg), 0))
        .filter(WarehouseReceipt.store_id == store_id,
                WarehouseReceipt.status.in_(OPEN_RECEIPT_STATUSES))
        .scalar())
    return Decimal(str(rows or 0))


# ── Reception: the whole act of issuing a receipt ────────────────────────────
@bp.route('/create', methods=['POST'])
@jwt_required()
def create_receipt():
    """Body:
    {
      "store_id": 3,
      "depositor_type": "cooperative",
      "depositor_name": "Bugisu Cooperative Union",
      "depositor_code": "COOP-0012",            # optional, their own id
      "depositor_user_id": 18,                   # optional, if they have an account
      "crop_id": 1, "variety_id": 2,
      "gross_weight_kg": 1020, "net_weight_kg": 1000,
      "price_per_kg": 9500, "currency": "UGX",
      "measurements": { "<parameter_id>": 11.2 },
      "grade_id": 4,                             # optional: overrides the computed grade
      "farms": [ {"farm_id": "WAK0002", "weight_kg": 600}, ... ],
      "note": "..."
    }
    """
    user = _current_user()
    if not _can_receive(user):
        return jsonify({"message": "Only warehouse staff can issue receipts."}), 403

    data = request.get_json(silent=True) or {}

    # ── Warehouse ────────────────────────────────────────────────────────────
    store = Store.query.get(data.get('store_id'))
    if not store or store.store_type != 'warehouse':
        return jsonify({"message": "Warehouse not found."}), 404
    if store.status is False:
        return jsonify({"message": "This warehouse is inactive."}), 400
    if not store.is_certified:
        return jsonify({"message": "Only a certified warehouse can issue receipts."}), 400

    # ── Commodity and variety ────────────────────────────────────────────────
    crop = Crop.query.get(data.get('crop_id'))
    if not crop:
        return jsonify({"message": "Commodity not found."}), 404
    if store.accepted_crops and crop not in store.accepted_crops:
        return jsonify({"message": f"{store.name} does not accept {crop.name}."}), 400

    variety = None
    if data.get('variety_id'):
        variety = CropVariety.query.get(data['variety_id'])
        if not variety or variety.crop_id != crop.id:
            return jsonify({"message": "Variety not found for this commodity."}), 400

    # ── Weights ──────────────────────────────────────────────────────────────
    gross, error = _dec(data.get('gross_weight_kg'), 'Gross weight', Decimal('0.001'))
    if error:
        return jsonify({"message": error}), 400
    net, error = _dec(data.get('net_weight_kg'), 'Net weight', Decimal('0.001'))
    if error:
        return jsonify({"message": error}), 400
    if net is None:
        return jsonify({"message": "Net weight is required."}), 400
    if gross is None:
        gross = net
    if net > gross:
        return jsonify({"message": "Net weight cannot exceed gross weight."}), 400

    # Capacity: a receipt is a promise that the goods are there. Issuing beyond
    # what the warehouse can hold would make that promise false.
    if store.capacity_tonnes:
        capacity_kg = Decimal(str(store.capacity_tonnes)) * Decimal('1000')
        in_store = warehouse_stock_kg(store.id)
        if in_store + net > capacity_kg:
            free = capacity_kg - in_store
            return jsonify({"message": f"Not enough space: {free} kg free out of "
                                       f"{capacity_kg} kg capacity."}), 400

    # ── Quality: measure first, grade second ─────────────────────────────────
    measurements = data.get('measurements') or {}
    result = evaluate_grade(crop.id, measurements, variety.id if variety else None)
    if not result['accepted']:
        return jsonify({"message": "The delivery does not meet the accepted quality range.",
                        "errors": result['errors']}), 400

    grade_id = None
    if data.get('grade_id'):
        grade = Grade.query.get(data['grade_id'])
        if not grade or grade.crop_id != crop.id:
            return jsonify({"message": "Grade not found for this commodity."}), 400
        grade_id = grade.id
    elif result['grade']:
        grade_id = result['grade']['id']

    # ── Depositor ────────────────────────────────────────────────────────────
    depositor_type = data.get('depositor_type')
    if depositor_type not in DEPOSITOR_TYPES:
        return jsonify({"message": f"depositor_type must be one of: "
                                   f"{', '.join(DEPOSITOR_TYPES)}."}), 400
    depositor_name = (data.get('depositor_name') or '').strip()
    if not depositor_name:
        return jsonify({"message": "Depositor name is required."}), 400

    price_per_kg, error = _dec(data.get('price_per_kg'), 'Price per kg', ZERO)
    if error:
        return jsonify({"message": error}), 400

    receipt = WarehouseReceipt(
        store_id=store.id,
        depositor_type=depositor_type,
        depositor_name=depositor_name,
        depositor_code=(data.get('depositor_code') or '').strip() or None,
        depositor_user_id=data.get('depositor_user_id') or None,
        crop_id=crop.id,
        variety_id=variety.id if variety else None,
        grade_id=grade_id,
        gross_weight_kg=gross,
        net_weight_kg=net,
        released_weight_kg=ZERO,
        price_per_kg=price_per_kg,
        currency=(data.get('currency') or 'UGX').upper(),
        status='issued',
        quality_note=(data.get('note') or '').strip() or None,
        received_at=datetime.utcnow(),
        created_by=user.id,
    )
    db.session.add(receipt)
    db.session.flush()                       # gives the id, and therefore the serial
    receipt.serial = serial_from_id(RECEIPT_PREFIX, receipt.id)

    # ── Contributing farms: the EUDR backbone, kept from the Produce Stamp ──
    farms_payload = data.get('farms') or []
    total_farm_weight = ZERO
    for entry in farms_payload:
        weight, error = _dec(entry.get('weight_kg'), 'Farm weight', ZERO)
        if error:
            db.session.rollback()
            return jsonify({"message": error}), 400
        farm = Farm.query.filter_by(farm_id=entry.get('farm_id')).first() if entry.get('farm_id') else None
        db.session.add(WarehouseReceiptFarm(
            receipt_id=receipt.id,
            farm_id=farm.farm_id if farm else None,
            farm_name=entry.get('farm_name') or (farm.name if farm else None),
            weight_kg=weight or ZERO,
        ))
        total_farm_weight += (weight or ZERO)

    if farms_payload and abs(total_farm_weight - net) > Decimal('0.5'):
        db.session.rollback()
        return jsonify({"message": f"Farm weights add up to {total_farm_weight} kg "
                                   f"but the net weight is {net} kg."}), 400

    # ── Measurements, stored one row per parameter ───────────────────────────
    parameters = {p.id: p for p in applicable_parameters(crop.id, variety.id if variety else None)}
    for raw_id, raw_value in measurements.items():
        parameter = parameters.get(int(raw_id))
        if not parameter or raw_value in (None, ''):
            continue
        number, _ = _dec(raw_value, parameter.name)
        db.session.add(WarehouseReceiptMeasurement(
            receipt_id=receipt.id,
            parameter_id=parameter.id,
            value_number=number if parameter.value_type == 'number' else None,
            value_text=str(raw_value) if parameter.value_type != 'number' else None,
        ))

    # ── QR code: the serial and the public verification link ────────────────
    qr_payload = {
        'serial': receipt.serial,
        'warehouse': store.code or store.name,
        'commodity': crop.name,
        'variety': variety.name if variety else None,
        'grade': result['grade']['grade_value'] if result['grade'] else None,
        'net_weight_kg': str(net),
        'received_at': receipt.received_at.isoformat(),
        'verify': f"/verify/{receipt.serial}",
    }
    qr = save_qr_in_db(qr_payload, user.id,
                       description=f"Warehouse receipt {receipt.serial}",
                       qr_type='warehouse_receipt')
    receipt.qr_hash = qr.hash_md5

    log_movement(store.id, receipt, 'in', net, 'reception',
                 note=f"Received from {depositor_name}", created_by=user.id)
    db.session.commit()
    return jsonify({"message": f"Receipt {receipt.serial} issued.",
                    "receipt": receipt.to_dict(with_detail=True),
                    "grading": result}), 201


# ── Read ─────────────────────────────────────────────────────────────────────
@bp.route('/', methods=['GET'])
@jwt_required()
def list_receipts():
    """?store_id= ?status= ?crop_id= ?q= ?from= ?to= ?page= ?per_page="""
    user = _current_user()
    if not user:
        return jsonify({"message": "User not found."}), 404

    page = max(request.args.get('page', 1, type=int), 1)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    query = WarehouseReceipt.query

    store_id = request.args.get('store_id', type=int)
    if store_id:
        query = query.filter_by(store_id=store_id)
    status = request.args.get('status')
    if status and status != 'all':
        query = query.filter_by(status=status)
    crop_id = request.args.get('crop_id', type=int)
    if crop_id:
        query = query.filter_by(crop_id=crop_id)

    search = (request.args.get('q') or '').strip()
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(
            WarehouseReceipt.serial.ilike(like),
            WarehouseReceipt.depositor_name.ilike(like),
            WarehouseReceipt.depositor_code.ilike(like),
        ))

    for key, column, op in (('from', WarehouseReceipt.received_at, 'ge'),
                            ('to', WarehouseReceipt.received_at, 'le')):
        raw = request.args.get(key)
        if not raw:
            continue
        try:
            moment = datetime.strptime(raw, '%Y-%m-%d')
        except ValueError:
            continue
        query = query.filter(column >= moment if op == 'ge'
                             else column < moment.replace(hour=23, minute=59, second=59))

    # A depositor with an account only sees their own receipts.
    if not user.is_admin and user.user_type not in RECEIVING_ROLES:
        query = query.filter(WarehouseReceipt.depositor_user_id == user.id)

    total = query.count()
    receipts = (query.order_by(WarehouseReceipt.received_at.desc())
                .limit(per_page).offset((page - 1) * per_page).all())

    return jsonify({
        'items': [r.to_dict() for r in receipts],
        'total': total,
        'page': page,
        'pages': max((total + per_page - 1) // per_page, 1),
        'statuses': list(RECEIPT_STATUSES),
    })


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_receipt(id):
    user = _current_user()
    receipt = WarehouseReceipt.query.get_or_404(id)
    if (not user.is_admin and user.user_type not in RECEIVING_ROLES
            and receipt.depositor_user_id != user.id):
        return jsonify({"message": "Unauthorized"}), 403
    return jsonify(receipt.to_dict(with_detail=True))


# ── Public verification ──────────────────────────────────────────────────────
#  ★ MODIFIÉ — deux niveaux :
#    · GRATUIT  : le reçu existe, il est authentique, son statut, la
#                 marchandise et l'entrepôt. Assez pour repérer un faux.
#    · PAYANT   : grade, mesures, poids, déposant, fermes d'origine. Débloqué
#                 par un paiement rattaché à CE reçu (txn_id 'WRV-<serial>-…').
#  Prix et durée d'accès : FeaturePrice 'receipt_verification' (écran Features).
# ─────────────────────────────────────────────────────────────────────────────
def _receipt_by_serial(serial):
    return WarehouseReceipt.query.filter_by(serial=(serial or '').strip().upper()).first()


def _verification_price():
    """{devise: prix} configuré pour la vérification détaillée, ou None."""
    feature = FeaturePrice.query.filter_by(feature_name=VERIFICATION_FEATURE).first()
    if not feature or not feature.prices:
        return None, None
    return ({p.currency: float(p.price) for p in feature.prices},
            {'currency': feature.default_currency, 'duration_days': feature.duration_days})


def _public_summary(receipt):
    store = receipt.store
    return {
        "valid": True,
        "serial": receipt.serial,
        "status": receipt.status,
        "warehouse": store.name if store else None,
        "warehouse_code": store.code if store else None,
        "country": store.country if store else None,
        "commodity": receipt.crop.name if receipt.crop else None,
        "variety": receipt.variety.name if receipt.variety else None,
        "received_at": receipt.received_at.isoformat() if receipt.received_at else None,
    }


def _full_detail(receipt):
    data = _public_summary(receipt)
    data.update({
        "grade": receipt.grade.grade_value if receipt.grade else None,
        "net_weight_kg": float(receipt.net_weight_kg or 0),
        "released_weight_kg": float(receipt.released_weight_kg or 0),
        "remaining_weight_kg": float(receipt.remaining_weight_kg or 0),
        "depositor": receipt.depositor_name,
        "depositor_type": receipt.depositor_type,
        "quality": [m.to_dict() for m in receipt.measurements],
        "farms": [{"farm_id": f.farm_id, "farm_name": f.farm_name,
                   "weight_kg": float(f.weight_kg or 0)} for f in receipt.farms],
    })
    return data


@bp.route('/verify/<serial>', methods=['GET'])
def verify_receipt(serial):
    """GRATUIT — anyone scanning the QR can check that the receipt is genuine."""
    receipt = _receipt_by_serial(serial)
    if not receipt:
        return jsonify({"valid": False, "message": "No receipt with this serial number."}), 404

    prices, info = _verification_price()
    data = _public_summary(receipt)
    data["detail_prices"] = prices                      # None = vérification détaillée non configurée
    data["detail_currency"] = info['currency'] if info else None
    data["detail_duration_days"] = info['duration_days'] if info else None
    return jsonify(data)


@bp.route('/verify/<serial>/pay', methods=['POST'])
def pay_receipt_verification(serial):
    """Lance le paiement du détail d'UN reçu. Pas de compte nécessaire.

    Body : { "payment_method": "dpo" | "mobile_money",
             "phone_number": "...", "email": "...", "currency": "UGX" }

    La vérification du paiement passe par les routes existantes :
      Mobile Money → /api/payments/status/<txn_id>
      DPO          → /api/payments/dpo/verify/<trans_token>
    La réponse contient `access_key`, à renvoyer à /verify/<serial>/detail.
    """
    receipt = _receipt_by_serial(serial)
    if not receipt:
        return jsonify({"error": "No receipt with this serial number."}), 404

    data = request.get_json(silent=True) or {}
    method = (data.get('payment_method') or 'dpo').lower()
    if method not in ('dpo', 'mobile_money'):
        return jsonify({"error": f"Unknown payment method: {method}"}), 400

    phone = (data.get('phone_number') or '').strip()
    email = (data.get('email') or '').strip()
    msisdn = ''.join(ch for ch in phone if ch.isdigit())
    if method == 'mobile_money' and len(msisdn) < 9:
        return jsonify({"error": "A valid phone number is required for Mobile Money"}), 400

    txn_id = f"{VERIFICATION_TXN_PREFIX}{receipt.serial}-{int(time.time() * 1000)}"
    payment, amount_or_error = create_payment_attempt(
        guest_phone_number=phone or None,
        feature_name=VERIFICATION_FEATURE,
        txn_id=txn_id,
        payment_method=method,
        currency=data.get('currency'),
    )
    if not payment:
        return jsonify({"error": amount_or_error}), 400
    amount = amount_or_error

    # ── Mobile Money ─────────────────────────────────────────────────────────
    if method == 'mobile_money':
        try:
            res = requests.post(
                current_app.config["MOBILE_MONEY_API_URL"],
                params={"amount": amount, "msisdn": msisdn, "txnId": txn_id},
                verify=current_app.config["MOBILE_MONEY_VERIFY_SSL"],
                timeout=15,
            )
        except requests.RequestException:
            payment.payment_status = 'failed'
            db.session.commit()
            return jsonify({"success": False, "error": "Mobile Money provider unreachable"}), 502
        if res.status_code >= 400:
            payment.payment_status = 'failed'
            db.session.commit()
            return jsonify({"success": False, "error": res.text or "Mobile Money request rejected"}), 400

        return jsonify({"success": True, "payment_method": "mobile_money",
                        "txn_id": txn_id, "access_key": txn_id, "msg": res.text,
                        "amount": float(amount), "currency": payment.currency}), 200

    # ── DPO (carte) ──────────────────────────────────────────────────────────
    result = DPOPayment().create_payment_token(
        amount=float(amount), currency=payment.currency, reference=txn_id,
        redirect_url=on_site(current_app.config["DPO_REDIRECT_URL"]),
        back_url=on_site(current_app.config["DPO_BACK_URL"]),
        customer_phone=phone, customer_email=email,
        description=f"Nkusu Services - {payment.narrative}",
    )
    if not result.get('success'):
        payment.payment_status = 'failed'
        db.session.commit()
        return jsonify({"success": False, "error": result.get('error'),
                        "result_code": result.get('result_code')}), 400

    payment.dpo_trans_token = result['trans_token']
    payment.dpo_trans_ref = result['trans_ref']
    db.session.commit()
    return jsonify({"success": True, "payment_method": "dpo",
                    "payment_url": result['payment_url'],
                    "trans_token": result['trans_token'],
                    "access_key": result['trans_token'],
                    "amount": float(amount), "currency": payment.currency}), 200


@bp.route('/verify/<serial>/detail', methods=['GET'])
def verify_receipt_detail(serial):
    """PAYANT — le détail complet, si ?key= correspond à un paiement réussi,
    non expiré, et fait pour CE reçu."""
    receipt = _receipt_by_serial(serial)
    if not receipt:
        return jsonify({"error": "No receipt with this serial number."}), 404

    key = (request.args.get('key') or '').strip()
    if not key:
        return jsonify({"error": "Payment required to see the full details."}), 402

    access = PaidFeatureAccess.query.filter(
        PaidFeatureAccess.feature_name == VERIFICATION_FEATURE,
        db.or_(PaidFeatureAccess.txn_id == key, PaidFeatureAccess.dpo_trans_token == key),
    ).first()

    # Un paiement fait pour un autre reçu ne débloque pas celui-ci.
    if not access or not (access.txn_id or '').startswith(
            f"{VERIFICATION_TXN_PREFIX}{receipt.serial}-"):
        return jsonify({"error": "This access key is not valid for this receipt."}), 403

    if access.payment_status != 'success':
        return jsonify({"status": "pending", "error": "Payment not confirmed yet."}), 402

    if access.access_expires_at and access.access_expires_at < datetime.utcnow():
        return jsonify({"status": "expired", "error": "Your access to this receipt has expired."}), 410

    data = _full_detail(receipt)
    data["access_expires_at"] = (access.access_expires_at.isoformat()
                                 if access.access_expires_at else None)
    return jsonify(data)


# ── Release: goods leave the warehouse ───────────────────────────────────────
@bp.route('/<int:id>/release', methods=['POST'])
@jwt_required()
def release_receipt(id):
    """Body: { "weight_kg": 400, "note": "collected by buyer B-00012" }
    Omit weight_kg to release everything that is left."""
    user = _current_user()
    if not _can_receive(user):
        return jsonify({"message": "Only warehouse staff can release goods."}), 403

    receipt = WarehouseReceipt.query.get_or_404(id)
    if receipt.status == 'pledged':
        return jsonify({"message": "This receipt is pledged as collateral. "
                                   "It must be released by the lender first."}), 409
    if receipt.status not in OPEN_RECEIPT_STATUSES:
        return jsonify({"message": f"A receipt marked '{receipt.status}' cannot be released."}), 400

    remaining = receipt.remaining_weight_kg
    weight, error = _dec(request.get_json(silent=True, force=True).get('weight_kg')
                         if request.data else None, 'Weight', Decimal('0.001'))
    if error:
        return jsonify({"message": error}), 400
    if weight is None:
        weight = remaining
    if weight > remaining:
        return jsonify({"message": f"Only {remaining} kg are left on this receipt."}), 400

    receipt.released_weight_kg = (receipt.released_weight_kg or ZERO) + weight
    receipt.status = 'released' if receipt.remaining_weight_kg <= ZERO else 'partially_released'
    receipt.date_updated = datetime.utcnow()
    log_movement(receipt.store_id, receipt, 'out', weight, 'release',
                 note=(request.get_json(silent=True) or {}).get('note'), created_by=user.id)
    db.session.commit()

    return jsonify({"message": f"{weight} kg released.", "receipt": receipt.to_dict()})


@bp.route('/<int:id>/cancel', methods=['POST'])
@jwt_required()
def cancel_receipt(id):
    user = _current_user()
    if not user or not user.is_admin:
        return jsonify({"message": "Only administrators can cancel a receipt."}), 403

    receipt = WarehouseReceipt.query.get_or_404(id)
    if receipt.status in ('released', 'sold', 'cancelled'):
        return jsonify({"message": f"A receipt marked '{receipt.status}' cannot be cancelled."}), 400
    if receipt.status == 'pledged':
        return jsonify({"message": "This receipt is pledged as collateral."}), 409

    receipt.status = 'cancelled'
    note = (request.get_json(silent=True) or {}).get('note')
    receipt.quality_note = f"{receipt.quality_note or ''}\nCancelled: {note or 'no reason given'}".strip()
    receipt.date_updated = datetime.utcnow()
    log_movement(receipt.store_id, receipt, 'out', receipt.remaining_weight_kg, 'cancellation',
                 note=note, created_by=user.id)
    db.session.commit()
    return jsonify({"message": "Receipt cancelled.", "receipt": receipt.to_dict()})


# ── What a warehouse currently holds ─────────────────────────────────────────
@bp.route('/stock/<int:store_id>', methods=['GET'])
@jwt_required()
def warehouse_stock(store_id):
    """Outstanding weight per commodity, variety and grade."""
    store = Store.query.get_or_404(store_id)

    rows = (db.session.query(
        WarehouseReceipt.crop_id, WarehouseReceipt.variety_id, WarehouseReceipt.grade_id,
        db.func.sum(WarehouseReceipt.net_weight_kg - WarehouseReceipt.released_weight_kg),
        db.func.count(WarehouseReceipt.id))
        .filter(WarehouseReceipt.store_id == store_id,
                WarehouseReceipt.status.in_(OPEN_RECEIPT_STATUSES))
        .group_by(WarehouseReceipt.crop_id, WarehouseReceipt.variety_id,
                  WarehouseReceipt.grade_id).all())

    lines = []
    for crop_id, variety_id, grade_id, weight, count in rows:
        crop = Crop.query.get(crop_id)
        variety = CropVariety.query.get(variety_id) if variety_id else None
        grade = Grade.query.get(grade_id) if grade_id else None
        lines.append({
            'commodity': crop.name if crop else None,
            'variety': variety.name if variety else None,
            'grade': grade.grade_value if grade else None,
            'weight_kg': float(weight or 0),
            'receipts': count,
        })

    held = warehouse_stock_kg(store_id)
    capacity_kg = (Decimal(str(store.capacity_tonnes)) * 1000) if store.capacity_tonnes else None

    return jsonify({
        'warehouse': {'id': store.id, 'code': store.code, 'name': store.name,
                      'country': store.country},
        'held_kg': float(held),
        'capacity_kg': float(capacity_kg) if capacity_kg else None,
        'usage_percent': float(held / capacity_kg * 100) if capacity_kg else None,
        'lines': sorted(lines, key=lambda l: -l['weight_kg']),
    })