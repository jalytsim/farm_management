# app/routes/subscriptions.py
# =============================================================================
#  Abonnements de livraison — option A : le client paie CHAQUE livraison.
#
#  Cycle de vie :
#    1. /create        → crée l'abonnement ('pending') + la commande de la
#                        1re livraison, puis lance le paiement (DPO ou Mobile
#                        Money), exactement comme le checkout boutique.
#    2. Paiement confirmé → _confirm_order_paid (ecommerce.py) appelle
#                        on_order_paid() : l'abonnement passe 'active'.
#    3. Chaque jour     → run_subscription_cycle() crée la commande de la
#                        prochaine livraison LEAD_DAYS jours avant la date,
#                        et prévient le client (lien vers sa page).
#    4. Le client paie depuis sa page (/manage/<token>/orders/<id>/pay).
#       Une livraison non payée est annulée UNPAID_GRACE_DAYS jours après
#       sa date prévue.
#
#  La vérification du paiement ne change pas : le front utilise les routes
#  existantes /api/ecommerce/checkout/verify/<token> (DPO) et
#  /api/ecommerce/checkout/mobile/status/<txn_id> (Mobile Money).
# =============================================================================

import time
import logging
import traceback
from contextlib import nullcontext
from datetime import date, datetime, timedelta

import requests
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import (
    EcoProduct, EcoOrder, EcoOrderItem, Subscription, SubscriptionOrder,
)
from app.utils.dpo_payment import DPOPayment
from app.utils.decorators import admin_required, current_user_id
from app.utils.site_url import site_url
from app.routes.ecommerce import (
    _dec, _normalize_msisdn, MOBILE_MONEY_CURRENCIES, ZERO, PAID_STATUSES,
)
from app.routes.api_notifications import deliver_sms

logger = logging.getLogger(__name__)

bp = Blueprint('subscriptions', __name__, url_prefix='/api/subscriptions')

# Nombre de jours AVANT la date de livraison où la commande est créée,
# pour laisser au client le temps de payer.
LEAD_DAYS = 2
# Une livraison non payée est annulée ce nombre de jours APRÈS sa date.
UNPAID_GRACE_DAYS = 3

UNPAID_STATUSES = ('pending', 'payment_failed')


# ==================== HELPERS ====================

def _optional_user_id():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return identity['id'] if isinstance(identity, dict) else identity
    except Exception:
        return None   # mode invité


def _qty_txt(value):
    return f"{float(value):g}"


def manage_url(sub):
    """Page client « gérer mon abonnement » (payer, pause, annuler)."""
    return f"{site_url()}/shop/subscription/{sub.manage_token}"


def _create_delivery_order(sub, delivery_date):
    """Crée une EcoOrder normale pour une échéance, au prix COURANT du produit.

    Le stock n'est PAS décrémenté ici : comme pour la boutique, c'est
    _confirm_order_paid qui le fait, au moment du paiement.
    """
    product = sub.product
    price = _dec(product.price, 'Price')
    order = EcoOrder(
        user_id=sub.user_id,
        guest_email=sub.guest_email,
        guest_name=sub.guest_name,
        guest_phone=sub.guest_phone,
        shipping_address=sub.shipping_address,
        total_amount=price * sub.quantity_kg,
        currency=product.currency or 'USD',
        status='pending',
        payment_method='dpo',
    )
    db.session.add(order)
    db.session.flush()

    db.session.add(EcoOrderItem(
        order_id=order.id, product_id=product.id,
        quantity=sub.quantity_kg, unit_price=price, unit=product.unit,
    ))
    db.session.add(SubscriptionOrder(
        subscription_id=sub.id, order_id=order.id, delivery_date=delivery_date,
    ))
    return order


def _check_mobile_money(currency, phone):
    """Retourne un message d'erreur, ou None si Mobile Money est utilisable."""
    if currency not in MOBILE_MONEY_CURRENCIES:
        return (f"Mobile Money is only available for orders in "
                f"{', '.join(sorted(MOBILE_MONEY_CURRENCIES))}. Please pay by card (DPO).")
    if len(_normalize_msisdn(phone)) < 9:
        return "A valid phone number is required for Mobile Money"
    return None


def _start_payment(order, method, phone, email):
    """Lance le paiement d'une commande existante. Retourne (payload, code HTTP).

    Même logique que initiate_checkout / _start_mobile_money dans ecommerce.py,
    mais réutilisable pour une commande déjà créée (paiement d'une échéance).
    """
    if method == 'mobile_money':
        err = _check_mobile_money(order.currency, phone)
        if err:
            return {"success": False, "error": err}, 400

        txn_id = f"NKUSUB{order.id}T{int(time.time())}"
        order.payment_method = 'mobile_money'
        order.dpo_trans_ref = txn_id
        order.status = 'pending'
        db.session.commit()

        try:
            res = requests.post(
                current_app.config["MOBILE_MONEY_API_URL"],
                params={"amount": order.total_amount,
                        "msisdn": _normalize_msisdn(phone), "txnId": txn_id},
                verify=current_app.config["MOBILE_MONEY_VERIFY_SSL"],
                timeout=15,
            )
        except requests.RequestException:
            traceback.print_exc()
            order.status = 'payment_failed'
            db.session.commit()
            return {"success": False, "error": "Mobile Money provider unreachable"}, 502

        if res.status_code >= 400:
            order.status = 'payment_failed'
            db.session.commit()
            return {"success": False,
                    "error": res.text or "Mobile Money request rejected"}, 400

        return {
            "success": True, "order_id": order.id,
            "payment_method": "mobile_money", "txn_id": txn_id, "msg": res.text,
            "amount": float(order.total_amount), "currency": order.currency,
        }, 200

    # ── DPO (carte) ──────────────────────────────────────────────────────────
    result = DPOPayment().create_payment_token(
        amount=float(order.total_amount), currency=order.currency,
        reference=f"NKU-SUB-{order.id}",
        redirect_url=f"{site_url()}/api/ecommerce/checkout/success",
        back_url=f"{site_url()}/api/ecommerce/checkout/cancelled",
        customer_phone=phone, customer_email=email,
        description=f"Nkusu Services - Subscription delivery NKU-SUB-{order.id}",
    )
    if not result.get('success'):
        order.status = 'payment_failed'
        db.session.commit()
        return {"success": False, "error": result.get('error'),
                "result_code": result.get('result_code')}, 400

    order.payment_method = 'dpo'
    order.status = 'pending'
    order.dpo_trans_token = result['trans_token']
    order.dpo_trans_ref = result['trans_ref']
    db.session.commit()

    return {
        "success": True, "order_id": order.id,
        "payment_method": "dpo",
        "payment_url": result['payment_url'],
        "trans_token": result['trans_token'],
        "amount": float(order.total_amount), "currency": order.currency,
    }, 200


def _send_sms(sub, message):
    """Envoie un SMS au client via deliver_sms (api_notifications.py), qui le
    journalise dans SMSLog. Un échec d'envoi ne bloque jamais l'abonnement.
    À appeler APRÈS un commit : deliver_sms commite sa propre ligne de log."""
    phone = _normalize_msisdn(sub.guest_phone)
    if not phone:
        return
    try:
        deliver_sms(phone, message, sub.user_id)
    except Exception:
        logger.exception("[Subscription] SMS failed for #%s", sub.id)


def _every_txt(weeks):
    return "every week" if int(weeks) == 1 else f"every {int(weeks)} weeks"


def _notify_subscribed(sub):
    product_name = sub.product.name if sub.product else 'coffee'
    _send_sms(sub, (f"Nkusu: thank you for subscribing! {_qty_txt(sub.quantity_kg)} kg "
                    f"{product_name} {_every_txt(sub.frequency_weeks)}. Pay, pause or cancel "
                    f"your deliveries here: {manage_url(sub)}"))


def _notify_payment_due(sub, order):
    """Prévient le client qu'une livraison est à payer."""
    product_name = sub.product.name if sub.product else 'coffee'
    _send_sms(sub, (f"Nkusu: your delivery of {_qty_txt(sub.quantity_kg)} kg {product_name} "
                    f"is ready ({float(order.total_amount):,.2f} {order.currency}). "
                    f"Pay or manage here: {manage_url(sub)}"))


def on_order_paid(order):
    """Appelé par _confirm_order_paid (ecommerce.py) quand une commande est payée.

    Si c'est la 1re livraison d'un abonnement, l'abonnement devient actif.
    Pas de commit ici : _confirm_order_paid commite juste après.
    """
    link = SubscriptionOrder.query.filter_by(order_id=order.id).first()
    if link and link.subscription and link.subscription.status == 'pending':
        link.subscription.status = 'active'


# ==================== CLIENT : S'ABONNER ====================

@bp.route('/create', methods=['POST'])
def create_subscription():
    """Crée l'abonnement + la 1re livraison, puis lance son paiement.

    Body JSON : product_id, quantity_kg, frequency_weeks, guest_name,
                phone_number, shipping_address, email (optionnel),
                payment_method ('dpo' | 'mobile_money').
    """
    try:
        user_id = _optional_user_id()
        data = request.get_json() or {}

        product = EcoProduct.query.get(data.get('product_id'))
        if not Subscription.is_subscribable(product):
            return jsonify({"error": "This product is not available for subscription"}), 400

        try:
            qty = _dec(data.get('quantity_kg'), 'Quantity')
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        if not Subscription.is_valid_quantity(product, qty):
            return jsonify({"error": (
                f"Minimum {_qty_txt(product.min_order_qty or 1)} kg per delivery, "
                f"in steps of {_qty_txt(product.order_step or 1)} kg")}), 400

        if not Subscription.is_valid_frequency(data.get('frequency_weeks')):
            return jsonify({"error": "Delivery frequency must be every 1, 2 or 3 weeks"}), 400
        weeks = int(data.get('frequency_weeks'))

        # La 1re livraison part tout de suite : il faut le stock maintenant.
        if qty > (product.stock_qty or ZERO):
            return jsonify({"error": f"Not enough stock for {product.name}"}), 400

        guest_name = (data.get('guest_name') or '').strip()
        phone = (data.get('phone_number') or '').strip()
        email = (data.get('email') or '').strip()
        address = (data.get('shipping_address') or '').strip()
        if not guest_name or not phone or not address:
            return jsonify({"error": "Name, phone number and shipping address are required"}), 400

        method = (data.get('payment_method') or 'dpo').lower()
        if method not in ('dpo', 'mobile_money'):
            return jsonify({"error": f"Unknown payment method: {method}"}), 400
        # Vérifié AVANT de créer quoi que ce soit : pas d'abonnement orphelin.
        if method == 'mobile_money':
            err = _check_mobile_money(product.currency, phone)
            if err:
                return jsonify({"error": err}), 400

        today = date.today()
        sub = Subscription(
            user_id=user_id,
            guest_email=email or None,
            guest_name=guest_name,
            guest_phone=phone,
            product_id=product.id,
            quantity_kg=qty,
            frequency_weeks=weeks,
            shipping_address=address,
            status='pending',                       # actif une fois la 1re livraison payée
            next_delivery_date=today + timedelta(weeks=weeks),
        )
        db.session.add(sub)
        db.session.flush()

        order = _create_delivery_order(sub, today)
        db.session.commit()

        payload, code = _start_payment(order, method, phone, email)
        # Renvoyés même si le paiement n'a pas pu démarrer : le front réessaie
        # alors sur la MÊME commande au lieu de créer un 2e abonnement.
        payload.update({
            "subscription_id": sub.id,
            "order_id": order.id,
            "manage_token": sub.manage_token,
            "manage_url": manage_url(sub),
        })
        # Le client garde ainsi son lien de gestion, même s'il ferme la page.
        _notify_subscribed(sub)
        return jsonify(payload), code

    except Exception:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"error": "Unexpected server error"}), 500


# ==================== CLIENT : GÉRER (lien avec token) ====================

def _sub_by_token(token):
    return Subscription.query.filter_by(manage_token=token).first_or_404()


@bp.route('/manage/<token>', methods=['GET'])
def get_subscription(token):
    return jsonify(_sub_by_token(token).to_dict())


@bp.route('/manage/<token>/pause', methods=['POST'])
def pause_subscription(token):
    sub = _sub_by_token(token)
    if sub.status != 'active':
        return jsonify({"error": f"Only an active subscription can be paused (current: {sub.status})"}), 400
    sub.status = 'paused'
    db.session.commit()
    return jsonify({"msg": "Subscription paused", "subscription": sub.to_dict()})


@bp.route('/manage/<token>/resume', methods=['POST'])
def resume_subscription(token):
    sub = _sub_by_token(token)
    if sub.status != 'paused':
        return jsonify({"error": f"Only a paused subscription can be resumed (current: {sub.status})"}), 400
    sub.status = 'active'
    # Une date passée pendant la pause : la prochaine livraison repart d'aujourd'hui.
    if sub.next_delivery_date < date.today():
        sub.next_delivery_date = date.today()
    db.session.commit()
    return jsonify({"msg": "Subscription resumed", "subscription": sub.to_dict()})


@bp.route('/manage/<token>/cancel', methods=['POST'])
def cancel_subscription(token):
    sub = _sub_by_token(token)
    if sub.status == 'cancelled':
        return jsonify({"msg": "Subscription already cancelled", "subscription": sub.to_dict()})

    sub.status = 'cancelled'
    sub.cancelled_at = datetime.utcnow()
    # Les livraisons pas encore payées sont annulées aussi (rien n'a été encaissé).
    for link in sub.links:
        if link.order and link.order.status in UNPAID_STATUSES:
            link.order.status = 'cancelled'
            link.order.date_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Subscription cancelled", "subscription": sub.to_dict()})


@bp.route('/manage/<token>/orders/<int:order_id>/pay', methods=['POST'])
def pay_delivery(token, order_id):
    """Paie une livraison en attente depuis la page de l'abonnement.

    Body JSON : payment_method ('dpo' | 'mobile_money'),
                phone_number (optionnel, sinon celui de l'abonnement), email (optionnel).
    """
    try:
        sub = _sub_by_token(token)
        if sub.status == 'cancelled':
            return jsonify({"error": "This subscription is cancelled"}), 400

        link = SubscriptionOrder.query.filter_by(subscription_id=sub.id, order_id=order_id).first()
        if not link or not link.order:
            return jsonify({"error": "Delivery not found"}), 404

        order = EcoOrder.query.filter_by(id=order_id).with_for_update().first()
        if order.status not in UNPAID_STATUSES:
            return jsonify({"error": f"This delivery cannot be paid (status: {order.status})"}), 400

        data = request.get_json() or {}
        method = (data.get('payment_method') or 'dpo').lower()
        if method not in ('dpo', 'mobile_money'):
            return jsonify({"error": f"Unknown payment method: {method}"}), 400

        phone = (data.get('phone_number') or sub.guest_phone or '').strip()
        email = (data.get('email') or sub.guest_email or '').strip()

        payload, code = _start_payment(order, method, phone, email)
        return jsonify(payload), code

    except Exception:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"error": "Unexpected server error"}), 500


# ==================== CLIENT CONNECTÉ ====================

@bp.route('/mine', methods=['GET'])
@jwt_required()
def list_my_subscriptions():
    subs = (Subscription.query.filter_by(user_id=current_user_id())
            .order_by(Subscription.date_created.desc()).all())
    return jsonify([s.to_dict() for s in subs])


# ==================== ADMIN ====================

@bp.route('/admin', methods=['GET'])
@admin_required
def list_subscriptions_admin():
    query = Subscription.query
    status = request.args.get('status')
    if status and status != 'all':
        query = query.filter(Subscription.status == status)
    subs = query.order_by(Subscription.date_created.desc()).all()
    return jsonify([s.to_dict(for_admin=True) for s in subs])


@bp.route('/admin/<int:id>/status', methods=['PUT'])
@admin_required
def update_subscription_status_admin(id):
    sub = Subscription.query.get_or_404(id)
    new_status = ((request.get_json() or {}).get('status') or '').strip()
    if new_status not in ('active', 'paused', 'cancelled'):
        return jsonify({"msg": "Invalid status: active, paused or cancelled"}), 400

    sub.status = new_status
    if new_status == 'cancelled':
        sub.cancelled_at = datetime.utcnow()
    elif new_status == 'active' and sub.next_delivery_date < date.today():
        sub.next_delivery_date = date.today()
    db.session.commit()
    return jsonify({"msg": f"Subscription marked as {new_status}",
                    "subscription": sub.to_dict(for_admin=True)})


# ==================== TÂCHE QUOTIDIENNE ====================

def run_subscription_cycle(app=None):
    """Annule les livraisons impayées en retard, puis crée les prochaines.

    Lancée chaque jour par le planificateur (app/__init__.py), ou à la main :
        flask subscriptions run
    Peut tourner plusieurs fois par jour sans créer de doublon (contrainte
    unique sur subscription_id + delivery_date).
    """
    ctx = app.app_context() if app else nullcontext()
    with ctx:
        today = date.today()
        stats = {'created': 0, 'waiting_stock': 0, 'skipped': 0, 'cancelled_unpaid': 0}

        # 1. Livraisons non payées, trop en retard → annulées.
        #    Rien à rendre au stock : il n'est décrémenté qu'au paiement.
        overdue = (EcoOrder.query
                   .join(SubscriptionOrder, SubscriptionOrder.order_id == EcoOrder.id)
                   .filter(EcoOrder.status.in_(UNPAID_STATUSES),
                           SubscriptionOrder.delivery_date < today - timedelta(days=UNPAID_GRACE_DAYS))
                   .all())
        for order in overdue:
            order.status = 'cancelled'
            order.date_updated = datetime.utcnow()
            stats['cancelled_unpaid'] += 1
        db.session.commit()

        # 1 bis. Abonnements jamais activés (1re livraison jamais payée) → annulés.
        stale = Subscription.query.filter(
            Subscription.status == 'pending',
            Subscription.date_created < datetime.utcnow() - timedelta(days=UNPAID_GRACE_DAYS),
        ).all()
        for sub in stale:
            if any(l.order and l.order.status in PAID_STATUSES for l in sub.links):
                sub.status = 'active'          # payé mais pas activé : on rattrape
                continue
            sub.status = 'cancelled'
            sub.cancelled_at = datetime.utcnow()
            for link in sub.links:
                if link.order and link.order.status in UNPAID_STATUSES:
                    link.order.status = 'cancelled'
            stats['cancelled_unpaid'] += 1
        db.session.commit()

        # 2. Prochaines livraisons à créer.
        due_ids = [s.id for s in Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.next_delivery_date <= today + timedelta(days=LEAD_DAYS),
        ).all()]

        for sub_id in due_ids:
            sub = Subscription.query.get(sub_id)
            try:
                product = sub.product
                delivery_date = sub.next_delivery_date
                in_stock = (Subscription.is_subscribable(product)
                            and (product.stock_qty or ZERO) >= sub.quantity_kg)

                if not in_stock:
                    if delivery_date <= today:
                        # Date atteinte sans stock : cette livraison est sautée.
                        sub.advance()
                        stats['skipped'] += 1
                        logger.warning("[Subscription] #%s skipped on %s: product unavailable or out of stock",
                                       sub.id, delivery_date)
                    else:
                        stats['waiting_stock'] += 1   # on réessaie demain
                    db.session.commit()
                    continue

                order = _create_delivery_order(sub, delivery_date)
                sub.advance()
                db.session.commit()
                stats['created'] += 1
                _notify_payment_due(sub, order)

            except IntegrityError:
                # Commande déjà créée pour cette date : on avance juste la date.
                db.session.rollback()
                sub = Subscription.query.get(sub_id)
                sub.advance()
                db.session.commit()
            except Exception:
                db.session.rollback()
                logger.exception("[Subscription] cycle failed for #%s", sub_id)

        logger.info("[Subscription] daily cycle: %s", stats)
        return stats


@bp.route('/admin/run-cycle', methods=['POST'])
@admin_required
def run_cycle_admin():
    """Bouton de secours dans l'admin : lance le cycle quotidien tout de suite.
    Sans risque de doublon : le même jour, une 2e exécution ne recrée rien."""
    try:
        return jsonify({"msg": "Daily cycle done", "stats": run_subscription_cycle()})
    except Exception:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"msg": "Daily cycle failed"}), 500


@bp.cli.command('run')
def run_cycle_command():
    """flask subscriptions run — lance le cycle quotidien à la main."""
    print(run_subscription_cycle())