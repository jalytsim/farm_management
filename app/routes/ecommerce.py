import os
import uuid
import traceback
from datetime import datetime
from flask import Blueprint, jsonify, request, redirect, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required
from app import db
from app.models import ProductCategory, EcoProduct, EcoProductImage, EcoOrder, EcoOrderItem
from app.utils.dpo_payment import DPOPayment

bp = Blueprint('ecommerce', __name__, url_prefix='/api/ecommerce')

FRONTEND_URL = "https://www.nkusu.com"
BACKEND_URL = "https://www.nkusu.com/api"
ROOT_URL = "https://www.nkusu.com"  # sans /api — les fichiers statiques ne sont pas sous /api

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_IMAGE_SIZE_MB = 5


def _allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def _get_user_id():
    identity = get_jwt_identity()
    return identity['id'] if isinstance(identity, dict) else identity


# ==================== CATEGORIES ====================

@bp.route('/categories', methods=['GET'])
def list_categories():
    categories = ProductCategory.query.order_by(ProductCategory.name).all()
    return jsonify([c.to_dict() for c in categories])


@bp.route('/categories/create', methods=['POST'])
@jwt_required()
def create_category():
    user_id = _get_user_id()
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

    category = ProductCategory(
        name=name,
        slug=slug,
        description=data.get('description'),
        created_by=user_id,
    )
    db.session.add(category)
    db.session.commit()
    return jsonify({"msg": "Category created successfully!", "category": category.to_dict()}), 201


@bp.route('/categories/<int:id>/edit', methods=['PUT'])
@jwt_required()
def edit_category(id):
    category = ProductCategory.query.get_or_404(id)
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"msg": "Category name is required"}), 400

    category.name = name
    category.description = data.get('description')
    db.session.commit()
    return jsonify({"msg": "Category updated successfully!", "category": category.to_dict()})


@bp.route('/categories/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_category(id):
    category = ProductCategory.query.get_or_404(id)
    if EcoProduct.query.filter_by(category_id=id).first():
        return jsonify({"msg": "Cannot delete: products are still linked to this category"}), 400
    db.session.delete(category)
    db.session.commit()
    return jsonify({"msg": "Category deleted successfully!"})


# ==================== IMAGE UPLOAD ====================

@bp.route('/products/upload-image', methods=['POST'])
@jwt_required()
def upload_product_image():
    if 'file' not in request.files:
        return jsonify({"msg": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No file selected"}), 400
    if not _allowed_image(file.filename):
        return jsonify({"msg": "Invalid file type. Allowed: png, jpg, jpeg, webp"}), 400

    file.seek(0, os.SEEK_END)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    if size_mb > MAX_IMAGE_SIZE_MB:
        return jsonify({"msg": f"File too large. Max {MAX_IMAGE_SIZE_MB}MB"}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))

    url = f"{ROOT_URL}/static/uploads/products/{filename}"
    return jsonify({"msg": "Image uploaded successfully!", "url": url}), 201


# ==================== PRODUCTS ====================

@bp.route('/products', methods=['GET'])
def list_products_public():
    products = EcoProduct.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in products])


@bp.route('/products/admin', methods=['GET'])
@jwt_required()
def list_products_admin():
    products = EcoProduct.query.order_by(EcoProduct.date_created.desc()).all()
    return jsonify([p.to_dict() for p in products])


@bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = EcoProduct.query.get_or_404(id)
    return jsonify(product.to_dict())


def _slugify(name):
    slug = name.lower().strip().replace(' ', '-')
    base_slug, i = slug, 1
    while EcoProduct.query.filter_by(slug=slug).first():
        i += 1
        slug = f"{base_slug}-{i}"
    return slug


def _sync_images(product, image_urls):
    # Supprime les anciennes images et recrée la liste (simple et fiable)
    EcoProductImage.query.filter_by(product_id=product.id).delete()
    for idx, url in enumerate(image_urls or []):
        if url:
            db.session.add(EcoProductImage(
                product_id=product.id, url=url,
                is_primary=(idx == 0), position=idx,
            ))


@bp.route('/products/create', methods=['POST'])
@jwt_required()
def create_product():
    user_id = _get_user_id()
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"msg": "Product name is required"}), 400
    if not data.get('price'):
        return jsonify({"msg": "Price is required"}), 400
    if not data.get('category_id'):
        return jsonify({"msg": "Category is required"}), 400

    category = ProductCategory.query.get(data.get('category_id'))
    if not category:
        return jsonify({"msg": "Invalid category"}), 400

    try:
        price = float(data.get('price'))
        compare_at_price = float(data['compare_at_price']) if data.get('compare_at_price') else None
        stock = int(data.get('stock') or 0)
    except (TypeError, ValueError):
        return jsonify({"msg": "Price and stock must be valid numbers"}), 400

    harvest_year = data.get('harvest_year')
    try:
        harvest_year = int(harvest_year) if harvest_year not in (None, '') else None
    except (TypeError, ValueError):
        return jsonify({"msg": "Harvest year must be a valid number"}), 400

    product = EcoProduct(
        name=name,
        slug=_slugify(name),
        description=data.get('description'),
        category_id=category.id,
        price=price,
        compare_at_price=compare_at_price,
        currency=data.get('currency') or 'USD',
        unit=data.get('unit') or 'kg',
        stock=stock,
        sku=data.get('sku') or None,
        origin_country=data.get('origin_country'),
        is_deforestation_free=bool(data.get('is_deforestation_free')),
        certification_labels=data.get('certification_labels') or [],
        is_active=data.get('is_active', True),
        is_featured=bool(data.get('is_featured')),
        created_by=user_id,
        origin_story=data.get('origin_story'),
        farmer_name=data.get('farmer_name'),
        harvest_year=harvest_year,
    )
    db.session.add(product)
    db.session.flush()  # pour avoir product.id avant d'ajouter les images

    _sync_images(product, data.get('images'))

    db.session.commit()
    return jsonify({"msg": "Product created successfully!", "product": product.to_dict()}), 201


@bp.route('/products/<int:id>/edit', methods=['PUT'])
@jwt_required()
def edit_product(id):
    product = EcoProduct.query.get_or_404(id)
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"msg": "Product name is required"}), 400
    if not data.get('category_id'):
        return jsonify({"msg": "Category is required"}), 400

    category = ProductCategory.query.get(data.get('category_id'))
    if not category:
        return jsonify({"msg": "Invalid category"}), 400

    try:
        price = float(data.get('price'))
        compare_at_price = float(data['compare_at_price']) if data.get('compare_at_price') else None
        stock = int(data.get('stock') or 0)
    except (TypeError, ValueError):
        return jsonify({"msg": "Price and stock must be valid numbers"}), 400

    harvest_year = data.get('harvest_year')
    try:
        harvest_year = int(harvest_year) if harvest_year not in (None, '') else None
    except (TypeError, ValueError):
        return jsonify({"msg": "Harvest year must be a valid number"}), 400

    product.name = name
    product.description = data.get('description')
    product.category_id = category.id
    product.price = price
    product.compare_at_price = compare_at_price
    product.currency = data.get('currency') or product.currency
    product.unit = data.get('unit') or product.unit
    product.stock = stock
    product.sku = data.get('sku') or None
    product.origin_country = data.get('origin_country')
    product.origin_story = data.get('origin_story')
    product.farmer_name = data.get('farmer_name')
    product.harvest_year = harvest_year
    product.is_deforestation_free = bool(data.get('is_deforestation_free'))
    product.certification_labels = data.get('certification_labels') or []
    product.is_active = data.get('is_active', product.is_active)
    product.is_featured = bool(data.get('is_featured'))
    product.date_updated = datetime.utcnow()

    if 'images' in data:
        _sync_images(product, data.get('images'))

    db.session.commit()
    return jsonify({"msg": "Product updated successfully!", "product": product.to_dict()})


@bp.route('/products/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = EcoProduct.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"msg": "Product deleted successfully!"})


# ==================== CHECKOUT DPO ====================

@bp.route('/checkout/initiate', methods=['POST'])
def initiate_checkout():
    try:
        print("\n" + "=" * 60)
        print("[SHOP-DPO] NOUVELLE COMMANDE")
        print("=" * 60)

        # JWT optionnel, mode invité supporté
        user_id = None
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            user_id = identity['id'] if isinstance(identity, dict) else identity
        except Exception as jwt_error:
            print(f"[SHOP-DPO] JWT Error (continuing as guest): {str(jwt_error)}")
            user_id = None

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        cart_items = data.get('items', [])  # [{ "product_id": 1, "quantity": 2 }, ...]
        phone = data.get("phone_number", "")
        email = data.get("email", "")
        guest_name = data.get("guest_name", "")
        shipping_address = data.get("shipping_address", "")

        if not cart_items:
            return jsonify({"error": "Cart is empty"}), 400

        # ── Recalcul du total CÔTÉ SERVEUR (jamais confiance au front) ──────
        order_items = []
        total = 0.0
        currency = 'UGX'

        for entry in cart_items:
            product = EcoProduct.query.get(entry.get('product_id'))
            qty = int(entry.get('quantity', 1))
            if not product or not product.is_active:
                return jsonify({"error": f"Product {entry.get('product_id')} unavailable"}), 400
            if product.stock < qty:
                return jsonify({"error": f"Not enough stock for {product.name}"}), 400
            total += product.price * qty
            currency = product.currency
            order_items.append((product, qty))

        # ── Création de la commande en 'pending' ─────────────────────────────
        order = EcoOrder(
            user_id=user_id,
            guest_email=None if user_id else email,
            guest_name=None if user_id else guest_name,
            guest_phone=None if user_id else phone,
            shipping_address=shipping_address,
            total_amount=total,
            currency=currency,
            status='pending',
            payment_method='dpo',
        )
        db.session.add(order)
        db.session.flush()

        for product, qty in order_items:
            db.session.add(EcoOrderItem(
                order_id=order.id, product_id=product.id,
                quantity=qty, unit_price=product.price,
            ))
        db.session.commit()

        print(f"[SHOP-DPO] Order created (ID: {order.id}), total: {total} {currency}")

        # ── Création du token DPO ─────────────────────────────────────────
        dpo = DPOPayment()
        redirect_url = f"{BACKEND_URL}/ecommerce/checkout/success"
        back_url = f"{BACKEND_URL}/ecommerce/checkout/cancelled"

        result = dpo.create_payment_token(
            amount=total,
            currency=currency,
            reference=f"NKU-SHOP-{order.id}",
            redirect_url=redirect_url,
            back_url=back_url,
            customer_phone=phone,
            customer_email=email,
        )

        if not result.get('success'):
            print(f"[SHOP-DPO] FAILURE: {result.get('error')}")
            order.status = 'payment_failed'
            db.session.commit()
            return jsonify({
                "success": False,
                "error": result.get('error'),
                "result_code": result.get('result_code'),
            }), 400

        order.dpo_trans_token = result['trans_token']
        order.dpo_trans_ref = result['trans_ref']
        db.session.commit()

        print(f"[SHOP-DPO] SUCCESS! Payment URL: {result['payment_url']}")
        print("=" * 60 + "\n")

        return jsonify({
            "success": True,
            "order_id": order.id,
            "payment_url": result['payment_url'],
            "trans_token": result['trans_token'],
            "amount": total,
            "currency": currency,
        }), 200

    except Exception as e:
        print(f"[SHOP-DPO] EXCEPTION: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Unexpected server error"}), 500


@bp.route('/checkout/verify/<trans_token>', methods=['GET'])
def verify_checkout(trans_token):
    """
    Vérifie le statut d'un paiement boutique.
    Retourne 202 (pending) sauf si définitivement payé (200).
    Ne renvoie jamais 'failed' sur une erreur temporaire — même logique que /dpo/verify.
    """
    try:
        order = EcoOrder.query.filter_by(dpo_trans_token=trans_token).first()

        if not order:
            return jsonify({"success": False, "status": "pending",
                             "message": "Order not found yet"}), 202

        if order.status == "paid":
            return jsonify({"success": True, "status": "paid",
                             "order": order.to_dict()}), 200

        dpo = DPOPayment()
        verification = dpo.verify_payment(trans_token)

        if verification.get("success") and verification.get("status") == "verified":
            order.status = "paid"
            # décrémenter le stock uniquement à la confirmation
            for item in order.items:
                product = EcoProduct.query.get(item.product_id)
                if product:
                    product.stock = max(0, product.stock - item.quantity)
            db.session.commit()
            return jsonify({"success": True, "status": "paid",
                             "order": order.to_dict()}), 200

        if verification.get("status") in ["error", "rate_limited"]:
            return jsonify({"success": False, "status": "pending",
                             "message": "Temporary error, retrying later"}), 202

        return jsonify({"success": False, "status": "pending"}), 202

    except Exception as e:
        print(f"[SHOP-DPO VERIFY] Exception: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "status": "pending",
                         "message": "Verification error, will retry"}), 202


# ==================== ROUTES DE REDIRECTION DPO (boutique) ====================

@bp.route('/checkout/success', methods=['GET'])
def checkout_success():
    trans_token = request.args.get('TransactionToken')
    print(f"\n[SHOP-DPO REDIRECT] Success callback: {trans_token}")

    if not trans_token:
        return redirect(f"{FRONTEND_URL}/shop/payment/error?error=Missing+token")

    try:
        order = EcoOrder.query.filter_by(dpo_trans_token=trans_token).first()

        if order and order.status != "paid":
            order.status = "paid"
            for item in order.items:
                product = EcoProduct.query.get(item.product_id)
                if product:
                    product.stock = max(0, product.stock - item.quantity)
            db.session.commit()
            print("[SHOP-DPO REDIRECT] Order marked as paid")

        return redirect(f"{FRONTEND_URL}/shop/payment/success?TransactionToken={trans_token}")

    except Exception as e:
        print("[SHOP-DPO REDIRECT] Exception:", str(e))
        traceback.print_exc()
        return redirect(f"{FRONTEND_URL}/shop/payment/error?error=Server+error")


@bp.route('/checkout/cancelled', methods=['GET'])
def checkout_cancelled():
    """L'utilisateur peut encore payer après annulation — on ne touche pas au statut."""
    trans_token = request.args.get('TransactionToken')
    print(f"\n[SHOP-DPO REDIRECT] Cancel callback: {trans_token}")
    return redirect(f"{FRONTEND_URL}/shop/payment/cancelled?TransactionToken={trans_token}")