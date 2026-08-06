# app/routes/ecommerce.py
# =============================================================================
#  Boutique — remplace intégralement ton fichier actuel.
#
#  Ce qui change par rapport à ta version :
#   1. Stock décimal + trois modes de vente ('unit', 'weight', 'lot')
#   2. Images : synchronisation via l'ORM, URLs relatives, route de service
#   3. Routes admin réellement protégées (admin_required, plus jwt_required nu)
#   4. Suppression logique des produits (une FK non nullable faisait planter
#      la suppression physique dès qu'un mouvement de stock existait)
#   5. Panier multi-devises refusé au lieu d'être silencieusement faux
# =============================================================================

import os
import uuid
import traceback
from decimal import Decimal, InvalidOperation
from datetime import datetime

from flask import Blueprint, jsonify, request, redirect, current_app, send_from_directory, abort
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required
from werkzeug.utils import secure_filename

from app import db
from app.models import (
    ProductCategory, EcoProduct, EcoProductImage, EcoOrder, EcoOrderItem,
    StockMovement, SALE_MODES,
)
from app.utils.dpo_payment import DPOPayment
from app.utils.decorators import admin_required, current_user_id
from app.utils.storage import get_storage, build_key, LocalStorage

bp = Blueprint('ecommerce', __name__, url_prefix='/api/ecommerce')

FRONTEND_URL = "https://www.nkusu.com"
BACKEND_URL = "https://www.nkusu.com/api"

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_IMAGE_SIZE_MB = 5
ZERO = Decimal('0')

ORDER_STATUS_TRANSITIONS = {
    'paid':      {'shipped', 'cancelled', 'refunded'},
    'shipped':   {'delivered', 'cancelled', 'refunded'},
    'delivered': {'refunded'},
    'cancelled': set(),
    'refunded':  set(),
}
STOCK_RESTORING_STATUSES = {'cancelled', 'refunded'}


# ==================== HELPERS ====================

def _allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def _dec(value, field='value'):
    """Conversion sûre vers Decimal. Lève ValueError avec un message lisible."""
    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field} must be a valid number")
    if d.is_nan() or d.is_infinite():
        raise ValueError(f"{field} must be a valid number")
    return d


def _get_user_id():
    identity = get_jwt_identity()
    return identity['id'] if isinstance(identity, dict) else identity


# ==================== STOCK ====================

def _log_stock_movement(product_id, quantity_change, stock_before, stock_after,
                        reason, order_id=None, note=None, created_by=None):
    """Écrit une ligne d'audit sans toucher au stock (l'appelant l'a déjà modifié)."""
    db.session.add(StockMovement(
        product_id=product_id, order_id=order_id,
        quantity_change=quantity_change,
        stock_before=stock_before, stock_after=stock_after,
        reason=reason, note=note, created_by=created_by,
    ))


def _adjust_stock(product, quantity_change, reason, order_id=None, note=None, created_by=None):
    """Modifie stock_qty ET trace le mouvement. quantity_change est un Decimal,
    négatif pour une sortie, positif pour une entrée."""
    quantity_change = _dec(quantity_change, 'quantity_change')
    stock_before = product.stock_qty or ZERO
    # max() entre deux Decimal : ne jamais écrire max(0, ...) ici, la comparaison
    # int/Decimal fonctionne mais le résultat peut redevenir un int et casser
    # l'arithmétique décimale plus loin.
    product.stock_qty = max(ZERO, stock_before + quantity_change)
    _log_stock_movement(
        product.id, quantity_change, stock_before, product.stock_qty,
        reason, order_id=order_id, note=note, created_by=created_by,
    )
    return product


@bp.route('/products/<int:id>/stock-movements', methods=['GET'])
@admin_required
def list_stock_movements(id):
    EcoProduct.query.get_or_404(id)
    movements = (StockMovement.query
                 .filter_by(product_id=id)
                 .order_by(StockMovement.date_created.desc())
                 .limit(200).all())
    return jsonify([m.to_dict() for m in movements])


# ==================== CATEGORIES ====================

@bp.route('/categories', methods=['GET'])
def list_categories():
    categories = ProductCategory.query.order_by(ProductCategory.name).all()
    return jsonify([c.to_dict() for c in categories])


@bp.route('/categories/create', methods=['POST'])
@admin_required
def create_category():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"msg": "Category name is required"}), 400
    if ProductCategory.query.filter_by(name=name).first():
        return jsonify({"msg": "A category with this name already exists"}), 409

    slug = name.lower().replace(' ', '-')
    base_slug, i = slug, 1
    while ProductCategory.query.filter_by(slug=slug).first():
        i += 1
        slug = f"{base_slug}-{i}"

    category = ProductCategory(name=name, slug=slug,
                               description=data.get('description'),
                               created_by=current_user_id())
    db.session.add(category)
    db.session.commit()
    return jsonify({"msg": "Category created", "category": category.to_dict()}), 201


@bp.route('/categories/<int:id>/edit', methods=['PUT'])
@admin_required
def edit_category(id):
    category = ProductCategory.query.get_or_404(id)
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"msg": "Category name is required"}), 400
    category.name = name
    category.description = data.get('description')
    db.session.commit()
    return jsonify({"msg": "Category updated", "category": category.to_dict()})


@bp.route('/categories/<int:id>/delete', methods=['DELETE'])
@admin_required
def delete_category(id):
    category = ProductCategory.query.get_or_404(id)
    if EcoProduct.query.filter_by(category_id=id).first():
        return jsonify({"msg": "Products are still linked to this category"}), 400
    db.session.delete(category)
    db.session.commit()
    return jsonify({"msg": "Category deleted"})


# ==================== IMAGES ====================

@bp.route('/products/upload-image', methods=['POST'])
@admin_required
def upload_product_image():
    if 'file' not in request.files:
        return jsonify({"msg": "No file received"}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"msg": "No file selected"}), 400
    if not _allowed_image(file.filename):
        return jsonify({"msg": "Unsupported format. Use png, jpg, jpeg or webp"}), 400

    file.seek(0, os.SEEK_END)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    if size_mb > MAX_IMAGE_SIZE_MB:
        return jsonify({"msg": f"File is too large. Maximum {MAX_IMAGE_SIZE_MB} MB"}), 400

    # On ne stocke JAMAIS l'URL en base : seulement la clé. L'URL est
    # reconstruite à l'affichage par le backend de stockage courant. Basculer
    # sur S3 ne demandera alors aucune réécriture de la table.
    storage = get_storage()
    key = build_key(file.filename, prefix='products')
    storage.save(file, key)

    return jsonify({"msg": "Image uploaded",
                    "key": key,
                    "url": storage.url(key)}), 201


@bp.route('/media/<path:key>', methods=['GET'])
def serve_media(key):
    """Sert un fichier du stockage local.

    En mode S3 cette route n'est jamais appelée : les URLs pointent
    directement sur le CDN. Elle reste utile en développement et sur une
    installation mono-serveur.
    """
    storage = get_storage()
    if not isinstance(storage, LocalStorage):
        abort(404)

    safe = '/'.join(secure_filename(part) for part in key.split('/') if part)
    if not safe:
        return jsonify({"msg": "Invalid file name"}), 400

    directory, _, filename = safe.rpartition('/')
    return send_from_directory(
        os.path.join(storage.root, directory) if directory else storage.root,
        filename, max_age=60 * 60 * 24 * 30,
    )


def _sync_images(product, image_urls):
    """Remplace la galerie du produit.

    On passe par la COLLECTION ORM, pas par un DELETE en masse : un
    `query.filter_by(...).delete()` court-circuite la session, laisse
    `product.images` périmé en mémoire et fait réapparaître les anciennes URLs
    dans la réponse. C'était l'un des deux bugs d'images.
    """
    if image_urls is None:
        return
    product.images.clear()
    db.session.flush()          # applique la suppression avant de réinsérer
    for idx, entry in enumerate(image_urls):
        if not entry:
            continue
        # Le front peut envoyer soit la clé renvoyée par upload-image (nouveau),
        # soit une URL brute (anciennes fiches). On accepte les deux.
        if isinstance(entry, dict):
            key, url = entry.get('key'), entry.get('url')
        elif entry.startswith('products/'):
            key, url = entry, None
        else:
            key, url = None, entry
        product.images.append(EcoProductImage(
            storage_key=key, url=url, is_primary=(idx == 0), position=idx,
        ))


# ==================== PRODUITS ====================

@bp.route('/products', methods=['GET'])
def list_products_public():
    """Catalogue public. Les produits réservés aux enchères en sont exclus."""
    products = (EcoProduct.query
                .filter_by(is_active=True, is_auction_only=False)
                .order_by(EcoProduct.is_featured.desc(), EcoProduct.date_created.desc())
                .all())
    return jsonify([p.to_dict() for p in products])


@bp.route('/products/admin', methods=['GET'])
@admin_required
def list_products_admin():
    products = EcoProduct.query.order_by(EcoProduct.date_created.desc()).all()
    return jsonify([p.to_dict() for p in products])


@bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = EcoProduct.query.get_or_404(id)
    # with_traceability : joint la parcelle et son rapport forestier. C'est la
    # matière du panneau de preuve sur la fiche produit.
    return jsonify(product.to_dict(with_traceability=True))


def _slugify(name):
    slug = name.lower().strip().replace(' ', '-')
    base_slug, i = slug, 1
    while EcoProduct.query.filter_by(slug=slug).first():
        i += 1
        slug = f"{base_slug}-{i}"
    return slug


def _read_sale_config(data, current=None):
    """Lit et valide mode de vente, stock et contraintes de quantité.

    Retourne (config_dict, erreur_ou_None).
    """
    sale_mode = (data.get('sale_mode') or (current.sale_mode if current else 'unit')).strip()
    if sale_mode not in SALE_MODES:
        return None, f"Invalid sale mode. Accepted values: {', '.join(SALE_MODES)}"

    try:
        stock_qty = _dec(data.get('stock_qty', current.stock_qty if current else 0), 'Stock')
        min_order_qty = _dec(data.get('min_order_qty') or 1, 'Minimum quantity')
        order_step = _dec(data.get('order_step') or 1, 'Order step')
        threshold = _dec(data.get('low_stock_threshold') or 5, "Low stock threshold")
    except ValueError as e:
        return None, str(e)

    if stock_qty < ZERO:
        return None, "Stock cannot be negative"
    if min_order_qty <= ZERO or order_step <= ZERO:
        return None, "Minimum quantity and step must be above zero"

    # Mode 'lot' : le lot est indivisible. On force min = pas = stock pour que
    # la seule quantité achetable soit le lot entier. Une seule règle de
    # validation sert alors les trois modes.
    if sale_mode == 'lot':
        min_order_qty = stock_qty
        order_step = stock_qty

    if sale_mode in ('weight', 'lot') and not (data.get('unit') or (current.unit if current else None)):
        data['unit'] = 'kg'

    return {
        'sale_mode': sale_mode,
        'stock_qty': stock_qty,
        'min_order_qty': min_order_qty,
        'order_step': order_step,
        'low_stock_threshold': threshold,
    }, None


def _apply_common_fields(product, data):
    """Champs partagés entre création et édition — storytelling inclus."""
    product.description = data.get('description')
    product.currency = data.get('currency') or product.currency or 'USD'
    product.unit = data.get('unit') or product.unit or 'kg'
    product.sku = data.get('sku') or None
    product.origin_country = data.get('origin_country')
    product.farm_id = data.get('farm_id') or None
    product.is_deforestation_free = bool(data.get('is_deforestation_free'))
    product.certification_labels = data.get('certification_labels') or []
    product.is_featured = bool(data.get('is_featured'))
    product.is_auction_only = bool(data.get('is_auction_only'))

    product.origin_story = data.get('origin_story')
    product.story_blocks = data.get('story_blocks') or []
    product.farmer_name = data.get('farmer_name')
    product.varietal = data.get('varietal')
    product.process_method = data.get('process_method')
    product.tasting_notes = data.get('tasting_notes') or []

    for field in ('harvest_year', 'altitude_m'):
        raw = data.get(field)
        if raw in (None, ''):
            setattr(product, field, None)
        else:
            try:
                setattr(product, field, int(raw))
            except (TypeError, ValueError):
                raise ValueError(f"{field} must be a whole number")

    score = data.get('cupping_score')
    product.cupping_score = float(score) if score not in (None, '') else None


@bp.route('/products/create', methods=['POST'])
@admin_required
def create_product():
    user_id = current_user_id()
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"msg": "Product name is required"}), 400
    if data.get('price') in (None, ''):
        return jsonify({"msg": "Price is required"}), 400

    category = ProductCategory.query.get(data.get('category_id'))
    if not category:
        return jsonify({"msg": "Invalid category"}), 400

    config, err = _read_sale_config(data)
    if err:
        return jsonify({"msg": err}), 400

    try:
        price = _dec(data.get('price'), 'Price')
        compare_at = _dec(data['compare_at_price'], 'Price barré') \
            if data.get('compare_at_price') else None
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400

    if price <= ZERO:
        return jsonify({"msg": "Price must be above zero"}), 400

    product = EcoProduct(
        name=name, slug=_slugify(name), category_id=category.id,
        price=price, compare_at_price=compare_at,
        is_active=data.get('is_active', True), created_by=user_id, **config,
    )
    try:
        _apply_common_fields(product, data)
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400

    db.session.add(product)
    db.session.flush()

    _sync_images(product, data.get('images'))

    if config['stock_qty'] > ZERO:
        _log_stock_movement(
            product.id, quantity_change=config['stock_qty'],
            stock_before=ZERO, stock_after=config['stock_qty'],
            reason='initial', note='Stock initial à la création', created_by=user_id,
        )

    db.session.commit()
    return jsonify({"msg": "Product created", "product": product.to_dict()}), 201


@bp.route('/products/<int:id>/edit', methods=['PUT'])
@admin_required
def edit_product(id):
    user_id = current_user_id()
    product = EcoProduct.query.get_or_404(id)
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"msg": "Product name is required"}), 400

    category = ProductCategory.query.get(data.get('category_id'))
    if not category:
        return jsonify({"msg": "Invalid category"}), 400

    config, err = _read_sale_config(data, current=product)
    if err:
        return jsonify({"msg": err}), 400

    try:
        price = _dec(data.get('price'), 'Price')
        compare_at = _dec(data['compare_at_price'], 'Price barré') \
            if data.get('compare_at_price') else None
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400

    product.name = name
    product.category_id = category.id
    product.price = price
    product.compare_at_price = compare_at
    product.sale_mode = config['sale_mode']
    product.min_order_qty = config['min_order_qty']
    product.order_step = config['order_step']
    product.low_stock_threshold = config['low_stock_threshold']
    product.is_active = data.get('is_active', product.is_active)
    product.date_updated = datetime.utcnow()

    try:
        _apply_common_fields(product, data)
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400

    # Stock : on ne trace que si la valeur change réellement.
    stock_diff = config['stock_qty'] - (product.stock_qty or ZERO)
    if stock_diff != ZERO:
        _adjust_stock(product, stock_diff, reason='manual_adjustment',
                      note=data.get('stock_note') or None, created_by=user_id)

    if 'images' in data:
        _sync_images(product, data.get('images'))

    db.session.commit()
    return jsonify({"msg": "Product updated", "product": product.to_dict()})


@bp.route('/products/<int:id>/delete', methods=['DELETE'])
@admin_required
def delete_product(id):
    """Suppression LOGIQUE.

    La suppression physique lève une IntegrityError dès qu'un StockMovement ou
    un EcoOrderItem référence le produit (FK non nullable, pas de cascade). Et
    même si elle passait, elle effacerait le nom des produits dans des commandes
    déjà payées. On désactive : le produit sort du catalogue, l'historique reste.
    """
    product = EcoProduct.query.get_or_404(id)
    product.is_active = False
    product.date_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Product removed from the catalogue"})


# ==================== CHECKOUT DPO ====================

def _build_order_items(cart_items):
    """Valide le panier et recalcule le total côté serveur.

    Retourne (items, total, currency, erreur). Le front n'est jamais cru sur
    le prix — seulement sur l'identifiant produit et la quantité.
    """
    order_items, total, currency = [], ZERO, None

    for entry in cart_items:
        product = EcoProduct.query.get(entry.get('product_id'))
        if not product or not product.is_active:
            return None, None, None, f"Product {entry.get('product_id')} is unavailable"

        try:
            qty = _dec(entry.get('quantity', 1), 'Quantity')
        except ValueError as e:
            return None, None, None, str(e)

        if not product.is_valid_quantity(qty):
            if product.sale_mode == 'lot':
                msg = (f"{product.name} is sold as a whole lot "
                       f"({product.stock_qty} {product.unit})")
            elif qty > (product.stock_qty or ZERO):
                msg = f"Not enough stock for {product.name}"
            else:
                msg = (f"Invalid quantity for {product.name}: "
                       f"minimum {product.min_order_qty} {product.unit}, "
                       f"in steps of {product.order_step}")
            return None, None, None, msg

        # Un panier multi-devises donnait un total silencieusement faux : la
        # devise retenue était celle du dernier produit de la boucle.
        if currency is None:
            currency = product.currency
        elif currency != product.currency:
            return None, None, None, (
                "Your cart mixes several currencies. Please place one order "
                "per currency."
            )

        total += product.price * qty
        order_items.append((product, qty))

    return order_items, total, (currency or 'USD'), None


@bp.route('/checkout/initiate', methods=['POST'])
def initiate_checkout():
    try:
        user_id = None
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            user_id = identity['id'] if isinstance(identity, dict) else identity
        except Exception:
            user_id = None   # mode invité

        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON request body"}), 400

        cart_items = data.get('items', [])
        if not cart_items:
            return jsonify({"error": "Your cart is empty"}), 400

        phone = data.get("phone_number", "")
        email = data.get("email", "")
        guest_name = data.get("guest_name", "")
        shipping_address = data.get("shipping_address", "")

        order_items, total, currency, err = _build_order_items(cart_items)
        if err:
            return jsonify({"error": err}), 400

        order = EcoOrder(
            user_id=user_id,
            guest_email=None if user_id else email,
            guest_name=None if user_id else guest_name,
            guest_phone=None if user_id else phone,
            shipping_address=shipping_address,
            total_amount=total, currency=currency,
            status='pending', payment_method='dpo',
        )
        db.session.add(order)
        db.session.flush()

        for product, qty in order_items:
            db.session.add(EcoOrderItem(
                order_id=order.id, product_id=product.id,
                quantity=qty, unit_price=product.price, unit=product.unit,
            ))
        db.session.commit()

        result = DPOPayment().create_payment_token(
            amount=float(total), currency=currency,
            reference=f"NKU-SHOP-{order.id}",
            redirect_url=f"{BACKEND_URL}/ecommerce/checkout/success",
            back_url=f"{BACKEND_URL}/ecommerce/checkout/cancelled",
            customer_phone=phone, customer_email=email,
        )

        if not result.get('success'):
            order.status = 'payment_failed'
            db.session.commit()
            return jsonify({"success": False, "error": result.get('error'),
                            "result_code": result.get('result_code')}), 400

        order.dpo_trans_token = result['trans_token']
        order.dpo_trans_ref = result['trans_ref']
        db.session.commit()

        return jsonify({
            "success": True, "order_id": order.id,
            "payment_url": result['payment_url'],
            "trans_token": result['trans_token'],
            "amount": float(total), "currency": currency,
        }), 200

    except Exception:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"error": "Unexpected server error"}), 500


def _confirm_order_paid(order_id):
    """Confirme le paiement, décrémente le stock et trace chaque sortie.

    Point d'entrée unique, atomique et idempotent : verify_checkout (polling du
    front) et checkout_success (callback DPO) passent tous les deux par ici.
    with_for_update verrouille la ligne, et le statut est revérifié APRÈS
    obtention du verrou — le stock ne peut donc jamais être décrémenté deux
    fois pour la même commande.
    """
    order = EcoOrder.query.filter_by(id=order_id).with_for_update().first()
    if not order or order.status == "paid":
        return order

    order.status = "paid"
    for item in order.items:
        product = EcoProduct.query.filter_by(id=item.product_id).with_for_update().first()
        if product:
            _adjust_stock(product, -item.quantity, reason='sale',
                          order_id=order.id, note=f"Order #{order.id}")
        # Un lot adjugé aux enchères est marqué vendu au moment du paiement.
        if item.auction_lot_id:
            from app.models import AuctionLot
            lot = AuctionLot.query.get(item.auction_lot_id)
            if lot:
                lot.status = 'sold'

    db.session.commit()
    return order


@bp.route('/checkout/verify/<trans_token>', methods=['GET'])
def verify_checkout(trans_token):
    """Renvoie 202 (en attente) sauf paiement définitivement confirmé (200).
    Une erreur temporaire ne doit jamais être présentée comme un échec."""
    try:
        order = EcoOrder.query.filter_by(dpo_trans_token=trans_token).first()
        if not order:
            return jsonify({"success": False, "status": "pending",
                            "message": "Order not recorded yet"}), 202

        if order.status == "paid":
            return jsonify({"success": True, "status": "paid",
                            "order": order.to_dict()}), 200

        verification = DPOPayment().verify_payment(trans_token)
        if verification.get("success") and verification.get("status") == "verified":
            order = _confirm_order_paid(order.id)
            return jsonify({"success": True, "status": "paid",
                            "order": order.to_dict()}), 200

        return jsonify({"success": False, "status": "pending"}), 202

    except Exception:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"success": False, "status": "pending",
                        "message": "Verification failed, will retry"}), 202


@bp.route('/checkout/success', methods=['GET'])
def checkout_success():
    trans_token = request.args.get('TransactionToken')
    if not trans_token:
        return redirect(f"{FRONTEND_URL}/shop/payment/error?error=Missing+token")
    try:
        order = EcoOrder.query.filter_by(dpo_trans_token=trans_token).first()
        if order:
            _confirm_order_paid(order.id)
        return redirect(f"{FRONTEND_URL}/shop/payment/success?TransactionToken={trans_token}")
    except Exception:
        db.session.rollback()
        traceback.print_exc()
        return redirect(f"{FRONTEND_URL}/shop/payment/error?error=Server+error")


@bp.route('/checkout/cancelled', methods=['GET'])
def checkout_cancelled():
    """L'acheteur peut encore payer après avoir annulé — on ne touche pas au statut."""
    trans_token = request.args.get('TransactionToken')
    return redirect(f"{FRONTEND_URL}/shop/payment/cancelled?TransactionToken={trans_token}")


# ==================== COMMANDES (ADMIN) ====================

@bp.route('/orders/admin', methods=['GET'])
@admin_required
def list_orders_admin():
    status = request.args.get('status')
    query = EcoOrder.query
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(EcoOrder.date_created.desc()).all()
    return jsonify([o.to_dict() for o in orders])


@bp.route('/orders/<int:id>', methods=['GET'])
@admin_required
def get_order_admin(id):
    return jsonify(EcoOrder.query.get_or_404(id).to_dict())


@bp.route('/orders/mine', methods=['GET'])
@jwt_required()
def list_my_orders():
    """Commandes de l'utilisateur connecté — boutique et enchères confondues."""
    orders = (EcoOrder.query.filter_by(user_id=current_user_id())
              .order_by(EcoOrder.date_created.desc()).all())
    return jsonify([o.to_dict() for o in orders])


@bp.route('/orders/<int:id>/status', methods=['PUT'])
@admin_required
def update_order_status(id):
    """Change le statut avec validation des transitions autorisées.

    Un passage en 'cancelled' ou 'refunded' restaure le stock et le trace
    (reason='return') : la commande l'avait décrémenté au paiement, l'annuler
    doit logiquement le rendre.
    """
    user_id = current_user_id()
    data = request.get_json() or {}
    new_status = (data.get('status') or '').strip()
    note = data.get('note') or None

    if new_status not in {'shipped', 'delivered', 'cancelled', 'refunded'}:
        return jsonify({"msg": "Invalid target status: shipped, delivered, "
                               "cancelled or refunded"}), 400

    order = EcoOrder.query.filter_by(id=id).with_for_update().first()
    if not order:
        return jsonify({"msg": "Order not found"}), 404

    allowed = ORDER_STATUS_TRANSITIONS.get(order.status, set())
    if new_status not in allowed:
        return jsonify({"msg": f"Cannot move this order from '{order.status}' "
                               f"to '{new_status}'",
                        "allowed_transitions": sorted(allowed)}), 400

    order.status = new_status
    order.date_updated = datetime.utcnow()

    if new_status in STOCK_RESTORING_STATUSES:
        for item in order.items:
            product = EcoProduct.query.filter_by(id=item.product_id).with_for_update().first()
            if product:
                _adjust_stock(product, item.quantity, reason='return',
                              order_id=order.id,
                              note=note or f"Order #{order.id} marked as {new_status}",
                              created_by=user_id)

    db.session.commit()
    return jsonify({"msg": f"Order marked as {new_status}", "order": order.to_dict()})