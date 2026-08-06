# app/routes/auction.py  — v2
# =============================================================================
#  Enchères — remplace intégralement la version précédente.
#
#  Ce que la v1 ne garantissait pas : que le gagnant paie. N'importe quel
#  compte pouvait pousser un lot à 500 $/kg puis disparaître.
#
#  Trois verrous ajoutés :
#    1. INSCRIPTION — on n'enchérit pas sans être inscrit à la vente
#    2. PLAFOND     — l'exposition totale d'un enchérisseur est bornée
#    3. DÉFAUT      — caution saisie, lot réattribué au second, compte sanctionné
#
#  Les messages renvoyés à l'utilisateur sont en anglais, comme le reste du site.
# =============================================================================

import traceback
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, redirect
from flask_jwt_extended import jwt_required

from app import db
from app.models import (
    Auction, AuctionLot, Bid, AutoBid, AuctionRegistration, BidderSanction,
    EcoProduct, EcoOrder, EcoOrderItem, ACCESS_MODES,
)
from app.utils.dpo_payment import DPOPayment
from app.utils.decorators import admin_required, current_user_id

bp = Blueprint('auction', __name__, url_prefix='/api/auction')

FRONTEND_URL = "https://www.nkusu.com"
BACKEND_URL = "https://www.nkusu.com/api"
ZERO = Decimal('0')


def _dec(value, field='Amount'):
    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field} must be a valid number")
    if d.is_nan() or d.is_infinite():
        raise ValueError(f"{field} must be a valid number")
    return d


def _slugify(name):
    slug = name.lower().strip().replace(' ', '-')
    base, i = slug, 1
    while Auction.query.filter_by(slug=slug).first():
        i += 1
        slug = f"{base}-{i}"
    return slug


# =============================================================================
#  MOTEUR D'ENCHÈRES
# =============================================================================

def _record_bid(lot, user_id, amount, is_auto):
    """Écrit une enchère et met à jour l'état du lot. Table append-only :
    c'est l'historique qui fait foi en cas de contestation."""
    db.session.add(Bid(lot_id=lot.id, user_id=user_id,
                       amount_per_kg=amount, is_auto=is_auto))
    lot.current_price_per_kg = amount
    lot.winner_user_id = user_id
    lot.bid_count = (lot.bid_count or 0) + 1
    lot.date_updated = datetime.utcnow()


def _settle(lot):
    """Fait jouer les enchères automatiques et fixe le prix courant.

    Formule fermée plutôt que ping-pong : on classe tous les maximums, le plus
    haut gagne et ne paie que le deuxième maximum plus un incrément. Une seule
    ligne d'historique, pas trente allers-retours artificiels.
    """
    inc = lot.min_increment or Decimal('0.50')

    entries = {}
    for ab in AutoBid.query.filter_by(lot_id=lot.id, is_active=True).all():
        entries[ab.user_id] = (ab.max_amount_per_kg, ab.date_created, True)

    if lot.winner_user_id and lot.winner_user_id not in entries:
        entries[lot.winner_user_id] = (
            lot.current_price_per_kg or lot.starting_price_per_kg,
            lot.date_updated or datetime.utcnow(), False,
        )

    if not entries:
        return

    ranked = sorted(entries.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
    winner_id, (winner_max, _, winner_is_auto) = ranked[0]

    if len(ranked) > 1:
        price = min(winner_max, ranked[1][1][0] + inc)
    else:
        price = lot.current_price_per_kg or lot.starting_price_per_kg

    price = max(price, lot.starting_price_per_kg)

    if winner_id != lot.winner_user_id or price != lot.current_price_per_kg:
        _record_bid(lot, winner_id, price, is_auto=winner_is_auto)


def _lock_open_lot(lot_id):
    lot = AuctionLot.query.filter_by(id=lot_id).with_for_update().first()
    if not lot:
        return None, "Lot not found", 404
    if lot.auction.status != 'live':
        return None, "This auction is not open", 409
    if not lot.is_open:
        return None, "Bidding has closed on this lot", 409
    return lot, None, None


# =============================================================================
#  DROIT D'ENCHÉRIR — le cœur de la garantie de paiement
# =============================================================================

def _check_bidding_rights(auction, user_id, lot, exposure_amount):
    """Vérifie qu'un utilisateur a le droit d'engager `exposure_amount`.

    `exposure_amount` est le TOTAL en jeu (prix au kg × poids du lot), pas le
    prix au kilo. Pour une enchère automatique on prend le plafond de
    l'utilisateur et non le montant courant : sinon un plafond de 200 $/kg
    passerait un contrôle calculé sur 50 $/kg.

    Retourne (registration_ou_None, message_erreur, code_http).
    """
    # Un défaut de paiement passé bloque toutes les ventes suivantes.
    if BidderSanction.is_blocked(user_id):
        return None, ("Your bidding privileges are suspended following a "
                      "previous payment default. Contact us to resolve this."), 403

    if auction.access_mode == 'open':
        return None, None, None

    reg = AuctionRegistration.query.filter_by(
        auction_id=auction.id, user_id=user_id).first()

    if not reg:
        return None, "You must register for this auction before bidding", 403
    if reg.status == 'deposit_pending':
        return None, "Your deposit has not been received yet", 402
    if reg.status == 'pending':
        return None, "Your registration is awaiting approval", 403
    if reg.status == 'rejected':
        return None, "Your registration for this auction was not approved", 403
    if reg.status == 'defaulted':
        return None, "Your registration was cancelled after a payment default", 403
    if not reg.can_bid:
        return None, "You are not approved to bid on this auction", 403

    # ── Plafond d'exposition ─────────────────────────────────────────────────
    # On additionne ce que l'utilisateur mène déjà sur les AUTRES lots. Le lot
    # courant n'y figure pas : enchérir alors qu'on est déjà en tête est refusé
    # en amont.
    if reg.bid_limit is not None:
        committed = reg.committed_exposure()
        if committed + exposure_amount > reg.bid_limit:
            available = reg.bid_limit - committed
            return None, (
                f"This bid would exceed your bidding limit. You have "
                f"{available:.2f} {auction.currency} left out of {reg.bid_limit:.2f}. "
                f"Increase your deposit to raise the limit."
            ), 403

    return reg, None, None


# =============================================================================
#  PUBLIC — CONSULTATION
# =============================================================================

@bp.route('/auctions', methods=['GET'])
def list_auctions():
    auctions = (Auction.query.filter_by(is_published=True)
                .order_by(Auction.starts_at.desc()).all())
    return jsonify([a.to_dict() for a in auctions])


@bp.route('/auctions/<slug>', methods=['GET'])
def get_auction(slug):
    auction = Auction.query.filter_by(slug=slug, is_published=True).first_or_404()
    data = auction.to_dict(with_lots=True)
    data['access_mode'] = auction.access_mode
    data['deposit_amount'] = float(auction.deposit_amount) if auction.deposit_amount else None
    data['deposit_multiplier'] = auction.deposit_multiplier
    data['payment_deadline_hours'] = auction.payment_deadline_hours
    return jsonify(data)


@bp.route('/auctions/<int:id>/lots', methods=['GET'])
def list_lots(id):
    """Endpoint léger pour le rafraîchissement du front. Renvoie aussi les
    stats d'en-tête pour éviter un second appel."""
    auction = Auction.query.get_or_404(id)
    return jsonify({
        'stats': auction.stats(),
        'status': auction.status,
        'ends_at': auction.ends_at.isoformat() if auction.ends_at else None,
        'server_time': datetime.utcnow().isoformat(),
        'lots': [l.to_dict() for l in auction.lots],
    })
@bp.route('/auctions/admin', methods=['GET'])
@admin_required
def list_auctions_admin():
    """Toutes les ventes, brouillons compris — la liste publique filtre
    sur is_published et masquerait donc tout ce qui reste à préparer."""
    auctions = Auction.query.order_by(Auction.starts_at.desc()).all()
    return jsonify([a.to_dict() for a in auctions])

@bp.route('/lots/<int:id>', methods=['GET'])
def get_lot(id):
    lot = AuctionLot.query.get_or_404(id)
    data = lot.to_dict()
    data['product'] = lot.product.to_dict(with_traceability=True) if lot.product else None
    data['bids'] = [b.to_dict(mask_identity=True) for b in lot.bids[:30]]
    data['server_time'] = datetime.utcnow().isoformat()
    return jsonify(data)


@bp.route('/lots/<int:id>/my-status', methods=['GET'])
@jwt_required()
def my_lot_status(id):
    uid = current_user_id()
    lot = AuctionLot.query.get_or_404(id)
    autobid = AutoBid.query.filter_by(lot_id=id, user_id=uid, is_active=True).first()
    reg = AuctionRegistration.query.filter_by(
        auction_id=lot.auction_id, user_id=uid).first()
    return jsonify({
        'is_leading': lot.winner_user_id == uid,
        'has_bid': Bid.query.filter_by(lot_id=id, user_id=uid).first() is not None,
        'autobid': autobid.to_dict() if autobid else None,
        'next_min_bid': float(lot.next_min_bid),
        'registration': reg.to_dict() if reg else None,
        'can_bid': (lot.auction.access_mode == 'open') or bool(reg and reg.can_bid),
    })


# =============================================================================
#  INSCRIPTION & CAUTION
# =============================================================================

@bp.route('/auctions/<int:id>/register', methods=['POST'])
@jwt_required()
def register_bidder(id):
    """Inscription à une vente. Selon le mode d'accès : immédiate, conditionnée
    au paiement d'une caution, ou soumise à validation manuelle."""
    uid = current_user_id()
    auction = Auction.query.get_or_404(id)
    data = request.get_json() or {}

    if BidderSanction.is_blocked(uid):
        return jsonify({"msg": "Your account is not eligible to register for auctions"}), 403
    if auction.status == 'closed':
        return jsonify({"msg": "This auction has closed"}), 409

    existing = AuctionRegistration.query.filter_by(auction_id=id, user_id=uid).first()
    if existing and existing.status in ('approved', 'deposit_pending'):
        return jsonify({"msg": "You are already registered",
                        "registration": existing.to_dict()}), 200

    reg = existing or AuctionRegistration(auction_id=id, user_id=uid)
    reg.company_name = data.get('company_name')
    reg.contact_phone = data.get('contact_phone')
    reg.contact_email = data.get('contact_email')
    reg.shipping_country = data.get('shipping_country')

    if auction.access_mode == 'open':
        reg.status = 'approved'
        reg.approved_at = datetime.utcnow()
        reg.bid_limit = None
    elif auction.access_mode == 'deposit':
        reg.status = 'deposit_pending'
        reg.deposit_amount = auction.deposit_amount
        reg.deposit_currency = auction.currency
        reg.deposit_status = 'none'
        reg.bid_limit = None      # accordé seulement une fois la caution encaissée
    else:
        reg.status = 'pending'

    if not existing:
        db.session.add(reg)
    db.session.commit()

    return jsonify({
        "msg": {
            'approved': "You are registered and can start bidding",
            'deposit_pending': "Registration created. Pay the deposit to unlock bidding.",
            'pending': "Registration submitted. We will review it shortly.",
        }.get(reg.status, "Registration created"),
        "registration": reg.to_dict(),
        "next_step": ('pay_deposit' if reg.status == 'deposit_pending'
                      else 'wait_approval' if reg.status == 'pending' else 'bid'),
    }), 201


@bp.route('/auctions/<int:id>/registration', methods=['GET'])
@jwt_required()
def my_registration(id):
    reg = AuctionRegistration.query.filter_by(
        auction_id=id, user_id=current_user_id()).first()
    if not reg:
        return jsonify({"registered": False}), 200
    return jsonify({"registered": True, "registration": reg.to_dict()}), 200


@bp.route('/registrations/<int:id>/pay-deposit', methods=['POST'])
@jwt_required()
def pay_deposit(id):
    """Génère le lien DPO pour la caution.

    La caution n'est pas une commande : ni produit, ni stock, ni livraison.
    Elle porte donc ses propres références DPO sur la ligne d'inscription
    plutôt que de détourner EcoOrder.
    """
    reg = AuctionRegistration.query.get_or_404(id)
    if reg.user_id != current_user_id():
        return jsonify({"msg": "This registration is not yours"}), 403
    if reg.deposit_status == 'held':
        return jsonify({"msg": "Your deposit has already been received"}), 409
    if not reg.deposit_amount or reg.deposit_amount <= ZERO:
        return jsonify({"msg": "No deposit is required for this auction"}), 400

    data = request.get_json() or {}
    result = DPOPayment().create_payment_token(
        amount=float(reg.deposit_amount),
        currency=reg.deposit_currency or reg.auction.currency,
        reference=f"NKU-DEPOSIT-{reg.id}",
        redirect_url=f"{BACKEND_URL}/auction/deposit/success",
        back_url=f"{BACKEND_URL}/auction/deposit/cancelled",
        customer_phone=data.get('phone_number') or reg.contact_phone or '',
        customer_email=data.get('email') or reg.contact_email or '',
    )
    if not result.get('success'):
        return jsonify({"success": False, "error": result.get('error')}), 400

    reg.dpo_trans_token = result['trans_token']
    reg.dpo_trans_ref = result['trans_ref']
    db.session.commit()

    return jsonify({"success": True, "payment_url": result['payment_url'],
                    "trans_token": result['trans_token'],
                    "amount": float(reg.deposit_amount),
                    "currency": reg.deposit_currency}), 200


def _confirm_deposit(reg_id):
    """Encaisse la caution et ouvre le droit d'enchérir.

    Même schéma que _confirm_order_paid côté boutique : verrou de ligne,
    revérification après obtention du verrou. Idempotent même si le callback
    DPO et le polling du front arrivent en même temps.
    """
    reg = AuctionRegistration.query.filter_by(id=reg_id).with_for_update().first()
    if not reg or reg.deposit_status == 'held':
        return reg

    reg.deposit_status = 'held'
    reg.deposit_paid_at = datetime.utcnow()
    reg.status = 'approved'
    reg.approved_at = datetime.utcnow()
    # Le plafond découle de la caution : 500 × 10 = 5 000 d'exposition
    # autorisée. Le multiplicateur se règle vente par vente.
    reg.bid_limit = reg.deposit_amount * (reg.auction.deposit_multiplier or 10)

    db.session.commit()
    return reg


@bp.route('/deposit/verify/<trans_token>', methods=['GET'])
def verify_deposit(trans_token):
    """Polling du front après retour de DPO. 202 tant que non confirmé."""
    try:
        reg = AuctionRegistration.query.filter_by(dpo_trans_token=trans_token).first()
        if not reg:
            return jsonify({"success": False, "status": "pending"}), 202
        if reg.deposit_status == 'held':
            return jsonify({"success": True, "status": "paid",
                            "registration": reg.to_dict()}), 200

        verification = DPOPayment().verify_payment(trans_token)
        if verification.get("success") and verification.get("status") == "verified":
            reg = _confirm_deposit(reg.id)
            return jsonify({"success": True, "status": "paid",
                            "registration": reg.to_dict()}), 200

        return jsonify({"success": False, "status": "pending"}), 202
    except Exception:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"success": False, "status": "pending"}), 202


@bp.route('/deposit/success', methods=['GET'])
def deposit_success():
    trans_token = request.args.get('TransactionToken')
    if not trans_token:
        return redirect(f"{FRONTEND_URL}/auction/deposit/error?error=Missing+token")
    try:
        reg = AuctionRegistration.query.filter_by(dpo_trans_token=trans_token).first()
        if reg:
            _confirm_deposit(reg.id)
        return redirect(f"{FRONTEND_URL}/auction/deposit/success?TransactionToken={trans_token}")
    except Exception:
        db.session.rollback()
        traceback.print_exc()
        return redirect(f"{FRONTEND_URL}/auction/deposit/error?error=Server+error")


@bp.route('/deposit/cancelled', methods=['GET'])
def deposit_cancelled():
    trans_token = request.args.get('TransactionToken')
    return redirect(f"{FRONTEND_URL}/auction/deposit/cancelled?TransactionToken={trans_token}")


# =============================================================================
#  PUBLIC — ENCHÉRIR
# =============================================================================

@bp.route('/lots/<int:id>/bid', methods=['POST'])
@jwt_required()
def place_bid(id):
    """Enchère manuelle : un montant exact au kilo."""
    uid = current_user_id()
    data = request.get_json() or {}

    try:
        amount = _dec(data.get('amount_per_kg'), "Bid amount")
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400

    try:
        lot, err, code = _lock_open_lot(id)
        if err:
            db.session.rollback()
            return jsonify({"msg": err}), code

        if lot.winner_user_id == uid:
            db.session.rollback()
            return jsonify({"msg": "You are already the highest bidder on this lot"}), 409

        if amount < lot.next_min_bid:
            db.session.rollback()
            return jsonify({"msg": f"Minimum bid is {lot.next_min_bid} "
                                   f"{lot.auction.currency}/kg",
                            "next_min_bid": float(lot.next_min_bid)}), 400

        _, err, code = _check_bidding_rights(lot.auction, uid, lot, amount * lot.weight_kg)
        if err:
            db.session.rollback()
            return jsonify({"msg": err}), code

        _record_bid(lot, uid, amount, is_auto=False)
        extended = lot.extend_for_anti_snipe()
        _settle(lot)

        db.session.commit()
        return jsonify({"msg": "Bid placed", "extended": extended,
                        "lot": lot.to_dict(),
                        "is_leading": lot.winner_user_id == uid}), 201

    except Exception:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"msg": "Your bid could not be placed. Please try again."}), 500


@bp.route('/lots/<int:id>/autobid', methods=['POST'])
@jwt_required()
def set_autobid(id):
    """Enchère automatique : l'utilisateur pose son plafond, le système
    n'engage que le minimum nécessaire pour le garder en tête."""
    uid = current_user_id()
    data = request.get_json() or {}

    try:
        max_amount = _dec(data.get('max_amount_per_kg'), "Maximum bid")
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400

    try:
        lot, err, code = _lock_open_lot(id)
        if err:
            db.session.rollback()
            return jsonify({"msg": err}), code

        if max_amount < lot.next_min_bid:
            db.session.rollback()
            return jsonify({"msg": f"Your maximum must be at least "
                                   f"{lot.next_min_bid} {lot.auction.currency}/kg",
                            "next_min_bid": float(lot.next_min_bid)}), 400

        # Contrôle du plafond sur le MAXIMUM : c'est bien ce montant que
        # l'utilisateur s'engage à payer si personne ne le dépasse.
        _, err, code = _check_bidding_rights(lot.auction, uid, lot,
                                             max_amount * lot.weight_kg)
        if err:
            db.session.rollback()
            return jsonify({"msg": err}), code

        autobid = AutoBid.query.filter_by(lot_id=id, user_id=uid).first()
        if autobid:
            if autobid.is_active and max_amount < autobid.max_amount_per_kg:
                db.session.rollback()
                return jsonify({"msg": "A maximum bid can only be raised"}), 400
            autobid.max_amount_per_kg = max_amount
            autobid.is_active = True
        else:
            db.session.add(AutoBid(lot_id=id, user_id=uid,
                                   max_amount_per_kg=max_amount, is_active=True))
        db.session.flush()

        extended = lot.extend_for_anti_snipe()
        _settle(lot)

        db.session.commit()
        return jsonify({"msg": "Automatic bidding is active", "extended": extended,
                        "lot": lot.to_dict(),
                        "is_leading": lot.winner_user_id == uid}), 201

    except Exception:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"msg": "Automatic bidding could not be set. Please try again."}), 500


# =============================================================================
#  ADMIN — VENTES
# =============================================================================

@bp.route('/auctions/create', methods=['POST'])
@admin_required
def create_auction():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"msg": "Auction name is required"}), 400

    try:
        starts_at = datetime.fromisoformat(data['starts_at'])
        ends_at = datetime.fromisoformat(data['ends_at'])
    except (KeyError, ValueError):
        return jsonify({"msg": "Start and end dates are required, in ISO format"}), 400
    if ends_at <= starts_at:
        return jsonify({"msg": "The end date must come after the start date"}), 400

    access_mode = data.get('access_mode') or 'open'
    if access_mode not in ACCESS_MODES:
        return jsonify({"msg": f"Access mode must be one of: {', '.join(ACCESS_MODES)}"}), 400

    deposit_amount = None
    if access_mode == 'deposit':
        try:
            deposit_amount = _dec(data.get('deposit_amount'), "Deposit amount")
        except ValueError as e:
            return jsonify({"msg": str(e)}), 400
        if deposit_amount <= ZERO:
            return jsonify({"msg": "A deposit auction needs a deposit above zero"}), 400

    auction = Auction(
        name=name, slug=_slugify(name),
        subtitle=data.get('subtitle'), description=data.get('description'),
        cover_image=data.get('cover_image'),
        starts_at=starts_at, ends_at=ends_at,
        anti_snipe_minutes=int(data.get('anti_snipe_minutes') or 3),
        currency=data.get('currency') or 'USD',
        access_mode=access_mode, deposit_amount=deposit_amount,
        deposit_multiplier=int(data.get('deposit_multiplier') or 10),
        payment_deadline_hours=int(data.get('payment_deadline_hours') or 72),
        created_by=current_user_id(),
    )
    db.session.add(auction)
    db.session.commit()
    return jsonify({"msg": "Auction created", "auction": auction.to_dict()}), 201


@bp.route('/auctions/<int:id>/lots', methods=['POST'])
@admin_required
def add_lot(id):
    auction = Auction.query.get_or_404(id)
    data = request.get_json() or {}

    product = EcoProduct.query.get(data.get('product_id'))
    if not product:
        return jsonify({"msg": "Product not found"}), 400
    if product.sale_mode != 'lot':
        return jsonify({"msg": "Only products sold as a whole lot can be auctioned"}), 400

    try:
        weight = _dec(data.get('weight_kg') or product.stock_qty, "Weight")
        starting = _dec(data.get('starting_price_per_kg'), "Starting price")
        increment = _dec(data.get('min_increment') or '0.50', "Bid increment")
        reserve = _dec(data['reserve_price_per_kg'], "Reserve price") \
            if data.get('reserve_price_per_kg') else None
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400

    if weight <= ZERO or starting <= ZERO or increment <= ZERO:
        return jsonify({"msg": "Weight, starting price and increment must be above zero"}), 400

    last = (AuctionLot.query.filter_by(auction_id=id)
            .order_by(AuctionLot.lot_number.desc()).first())
    lot_number = data.get('lot_number') or ((last.lot_number + 1) if last else 1)

    lot = AuctionLot(
        auction_id=id, product_id=product.id, lot_number=int(lot_number),
        weight_kg=weight, starting_price_per_kg=starting,
        min_increment=increment, reserve_price_per_kg=reserve,
        ends_at=auction.ends_at, status='scheduled',
    )
    product.is_auction_only = True   # retiré de la boutique pendant la vente

    db.session.add(lot)
    db.session.commit()
    return jsonify({"msg": "Lot added", "lot": lot.to_dict(for_admin=True)}), 201


@bp.route('/auctions/<int:id>/open', methods=['POST'])
@admin_required
def open_auction(id):
    auction = Auction.query.get_or_404(id)
    if auction.status == 'closed':
        return jsonify({"msg": "This auction has already closed"}), 400
    if not auction.lots:
        return jsonify({"msg": "Add at least one lot before opening the auction"}), 400

    auction.status = 'live'
    auction.is_published = True
    for lot in auction.lots:
        if lot.status == 'scheduled':
            lot.status = 'live'
            lot.ends_at = lot.ends_at or auction.ends_at
    db.session.commit()
    return jsonify({"msg": "Auction is open", "auction": auction.to_dict(with_lots=True)})


def _create_award_order(lot, price, currency):
    """Crée la commande d'un lot adjugé et bascule le lot en attente de paiement."""
    order = EcoOrder(
        user_id=lot.winner_user_id,
        total_amount=price * lot.weight_kg,
        currency=currency, status='pending', payment_method='dpo',
    )
    db.session.add(order)
    db.session.flush()
    db.session.add(EcoOrderItem(
        order_id=order.id, product_id=lot.product_id,
        quantity=lot.weight_kg, unit_price=price, unit='kg',
        auction_lot_id=lot.id,
    ))
    lot.order_id = order.id
    lot.status = 'awaiting_payment'
    return order


@bp.route('/auctions/<int:id>/close', methods=['POST'])
@admin_required
def close_auction(id):
    """Clôture et adjuge.

    Chaque lot adjugé génère un EcoOrder en 'pending' AVEC UNE ÉCHÉANCE. Passé
    ce délai, /lots/<id>/default saisit la caution et réattribue le lot.
    """
    auction = Auction.query.get_or_404(id)
    deadline = timedelta(hours=auction.payment_deadline_hours or 72)
    awarded, unsold = [], []

    for lot in auction.lots:
        if lot.status not in ('live', 'scheduled'):
            continue
        if lot.is_open:
            return jsonify({"msg": f"Lot #{lot.lot_number} is still open "
                                   f"(extended to {lot.effective_ends_at.isoformat()})"}), 409

        price = lot.current_price_per_kg
        reserve_met = (lot.reserve_price_per_kg is None
                       or (price is not None and price >= lot.reserve_price_per_kg))

        if not lot.winner_user_id or not reserve_met:
            lot.status = 'unsold'
            unsold.append(lot.lot_number)
            continue

        order = _create_award_order(lot, price, auction.currency)
        lot.payment_due_at = datetime.utcnow() + deadline
        awarded.append({'lot_number': lot.lot_number, 'order_id': order.id,
                        'winner_user_id': lot.winner_user_id,
                        'payment_due_at': lot.payment_due_at.isoformat()})

    auction.status = 'closed'
    db.session.commit()
    return jsonify({"msg": "Auction closed", "awarded": awarded, "unsold": unsold})


@bp.route('/lots/<int:id>/default', methods=['POST'])
@admin_required
def declare_default(id):
    """Le gagnant n'a pas payé dans les délais.

    Trois conséquences, et c'est l'ensemble qui rend l'enchère crédible :
      - la caution est saisie
      - le compte est sanctionné, donc bloqué sur les ventes futures
      - le lot repart au second enchérisseur, ou devient invendu

    Sans réattribution, un défaut coûte le lot entier au vendeur. Avec, il ne
    coûte que l'écart entre les deux dernières enchères.
    """
    lot = AuctionLot.query.filter_by(id=id).with_for_update().first()
    if not lot:
        return jsonify({"msg": "Lot not found"}), 404
    if lot.status != 'awaiting_payment':
        return jsonify({"msg": f"This lot is '{lot.status}' and cannot be "
                               f"declared in default"}), 409
    if lot.payment_due_at and datetime.utcnow() < lot.payment_due_at:
        return jsonify({"msg": f"Payment is not overdue yet "
                               f"(due {lot.payment_due_at.isoformat()})"}), 409

    data = request.get_json() or {}
    defaulter_id = lot.winner_user_id
    forfeited = ZERO

    # ── 1. Caution saisie ────────────────────────────────────────────────────
    reg = AuctionRegistration.query.filter_by(
        auction_id=lot.auction_id, user_id=defaulter_id).first()
    if reg and reg.deposit_status == 'held':
        reg.deposit_status = 'forfeited'
        forfeited = reg.deposit_amount or ZERO
    if reg:
        reg.status = 'defaulted'

    # ── 2. Sanction ──────────────────────────────────────────────────────────
    db.session.add(BidderSanction(
        user_id=defaulter_id, auction_id=lot.auction_id, lot_id=lot.id,
        reason='payment_default', amount_lost=forfeited,
        note=data.get('note') or f"No payment received for lot #{lot.lot_number}",
        blocked_until=None,               # définitif, à lever manuellement
        created_by=current_user_id(),
    ))

    # ── 3. Annulation de la commande impayée ─────────────────────────────────
    if lot.order_id:
        order = EcoOrder.query.get(lot.order_id)
        if order and order.status == 'pending':
            order.status = 'cancelled'
            order.date_updated = datetime.utcnow()

    # ── 4. Réattribution au second ───────────────────────────────────────────
    # On remonte l'historique jusqu'à la meilleure enchère d'un AUTRE
    # participant, encore éligible.
    underbid = (Bid.query.filter(Bid.lot_id == lot.id, Bid.user_id != defaulter_id)
                .order_by(Bid.amount_per_kg.desc(), Bid.date_created.asc())
                .first())
    reserve_ok = (lot.reserve_price_per_kg is None or
                  (underbid and underbid.amount_per_kg >= lot.reserve_price_per_kg))

    if underbid and reserve_ok and not BidderSanction.is_blocked(underbid.user_id):
        lot.current_price_per_kg = underbid.amount_per_kg
        lot.winner_user_id = underbid.user_id
        lot.default_count = (lot.default_count or 0) + 1
        order = _create_award_order(lot, underbid.amount_per_kg, lot.auction.currency)
        lot.payment_due_at = datetime.utcnow() + timedelta(
            hours=lot.auction.payment_deadline_hours or 72)
        outcome = {'reassigned_to_user_id': underbid.user_id,
                   'new_price_per_kg': float(underbid.amount_per_kg),
                   'new_order_id': order.id,
                   'payment_due_at': lot.payment_due_at.isoformat()}
    else:
        lot.status = 'unsold'
        lot.order_id = None
        lot.payment_due_at = None
        outcome = {'reassigned_to_user_id': None, 'reason': 'no eligible underbidder'}

    db.session.commit()
    return jsonify({"msg": "Default recorded", "defaulted_user_id": defaulter_id,
                    "deposit_forfeited": float(forfeited), "outcome": outcome})


@bp.route('/lots/overdue', methods=['GET'])
@admin_required
def list_overdue_lots():
    """Lots dont le délai de paiement est dépassé — à interroger par le cron
    avant de déclarer les défauts."""
    now = datetime.utcnow()
    lots = AuctionLot.query.filter(
        AuctionLot.status == 'awaiting_payment',
        AuctionLot.payment_due_at.isnot(None),
        AuctionLot.payment_due_at < now,
    ).all()
    return jsonify([{**l.to_dict(for_admin=True),
                     'payment_due_at': l.payment_due_at.isoformat()} for l in lots])


# =============================================================================
#  ADMIN — INSCRIPTIONS
# =============================================================================

@bp.route('/auctions/<int:id>/registrations', methods=['GET'])
@admin_required
def list_registrations(id):
    regs = AuctionRegistration.query.filter_by(auction_id=id).all()
    return jsonify([r.to_dict(for_admin=True) for r in regs])


@bp.route('/registrations/<int:id>/approve', methods=['POST'])
@admin_required
def approve_registration(id):
    """Validation manuelle (mode 'approval'), ou relèvement du plafond."""
    reg = AuctionRegistration.query.get_or_404(id)
    data = request.get_json() or {}

    if data.get('bid_limit') is not None:
        try:
            reg.bid_limit = _dec(data['bid_limit'], "Bidding limit")
        except ValueError as e:
            return jsonify({"msg": str(e)}), 400

    reg.status = 'approved'
    reg.approved_at = datetime.utcnow()
    reg.approved_by = current_user_id()
    reg.admin_note = data.get('note') or reg.admin_note
    db.session.commit()
    return jsonify({"msg": "Registration approved",
                    "registration": reg.to_dict(for_admin=True)})


@bp.route('/registrations/<int:id>/reject', methods=['POST'])
@admin_required
def reject_registration(id):
    reg = AuctionRegistration.query.get_or_404(id)
    reg.status = 'rejected'
    reg.admin_note = (request.get_json() or {}).get('note') or reg.admin_note
    db.session.commit()
    return jsonify({"msg": "Registration rejected",
                    "registration": reg.to_dict(for_admin=True)})


@bp.route('/registrations/<int:id>/refund-deposit', methods=['POST'])
@admin_required
def refund_deposit(id):
    """Marque la caution comme remboursée.

    Le virement se fait hors application : DPO ne rembourse pas par API sur
    tous les moyens de paiement. Cette route enregistre la décision et libère
    le plafond — c'est la trace comptable, pas le mouvement d'argent.
    """
    reg = AuctionRegistration.query.get_or_404(id)
    if reg.deposit_status != 'held':
        return jsonify({"msg": f"Deposit is '{reg.deposit_status}'"}), 409

    exposure = reg.committed_exposure()
    if exposure > ZERO:
        return jsonify({"msg": f"This bidder still has {exposure} "
                               f"{reg.deposit_currency} committed on open lots"}), 409

    reg.deposit_status = 'refunded'
    reg.bid_limit = ZERO
    reg.admin_note = (request.get_json() or {}).get('note') or reg.admin_note
    db.session.commit()
    return jsonify({"msg": "Deposit marked as refunded",
                    "registration": reg.to_dict(for_admin=True)})


@bp.route('/auctions/<int:id>/admin', methods=['GET'])
@admin_required
def get_auction_admin(id):
    auction = Auction.query.get_or_404(id)
    data = auction.to_dict()
    data['lots'] = [l.to_dict(for_admin=True) for l in auction.lots]
    data['registrations'] = [r.to_dict(for_admin=True) for r in auction.registrations]
    return jsonify(data)


# =============================================================================
#  PAIEMENT D'UN LOT ADJUGÉ
# =============================================================================

@bp.route('/orders/<int:order_id>/pay', methods=['POST'])
@jwt_required()
def pay_awarded_order(order_id):
    """Lien de paiement DPO pour un lot remporté. La confirmation passe par
    /api/ecommerce/checkout/success, qui décrémente le stock et bascule le lot
    en 'sold'."""
    uid = current_user_id()
    data = request.get_json() or {}

    order = EcoOrder.query.get_or_404(order_id)
    if order.user_id != uid:
        return jsonify({"msg": "This order is not yours"}), 403
    if order.status != 'pending':
        return jsonify({"msg": f"This order is already '{order.status}'"}), 409

    if data.get('shipping_address'):
        order.shipping_address = data['shipping_address']

    result = DPOPayment().create_payment_token(
        amount=float(order.total_amount), currency=order.currency,
        reference=f"NKU-AUCTION-{order.id}",
        redirect_url=f"{BACKEND_URL}/ecommerce/checkout/success",
        back_url=f"{BACKEND_URL}/ecommerce/checkout/cancelled",
        customer_phone=data.get('phone_number', ''),
        customer_email=data.get('email', ''),
    )
    if not result.get('success'):
        return jsonify({"success": False, "error": result.get('error')}), 400

    order.dpo_trans_token = result['trans_token']
    order.dpo_trans_ref = result['trans_ref']
    db.session.commit()

    return jsonify({"success": True, "payment_url": result['payment_url'],
                    "trans_token": result['trans_token'],
                    "amount": float(order.total_amount),
                    "currency": order.currency}), 200