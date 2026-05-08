from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Store, Product, User, db

api_store_bp = Blueprint('api_store', __name__, url_prefix='/api/store')


# ── GET all stores (filtered by account) ─────────────────────
@api_store_bp.route('/', methods=['GET'])
@jwt_required()
def get_stores():
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)

    page     = request.args.get('page',     1,  type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Admin → voit tout / sinon → seulement ses propres stores
    if user.is_admin:
        stores = Store.query.paginate(page=page, per_page=per_page)
    else:
        stores = Store.query.filter_by(created_by=user_id).paginate(
            page=page, per_page=per_page
        )

    stores_list = [
        {
            "id":              store.id,
            "name":            store.name,
            "location":        store.location,
            "country":         store.country,
            "district":        store.district,
            "store_type":      store.store_type,
            "status":          store.status,
            "phone_number":    store.phone_number,
            "email":           store.email,
            "inventory_count": store.inventory_count,
            "sales_count":     store.sales_count,
            "revenue":         store.revenue,
        }
        for store in stores.items
    ]

    return jsonify(
        stores=stores_list,
        total_pages=stores.pages,
        current_page=stores.page,
    )


# ── CREATE store ──────────────────────────────────────────────
@api_store_bp.route('/create', methods=['POST'])
@jwt_required()
def create_store():
    identity   = get_jwt_identity()
    user_id    = identity['id']
    data       = request.json

    new_store = Store(
        name         = data.get('name'),
        location     = data.get('location'),
        country      = data.get('country'),
        district     = data.get('district'),
        store_type   = data.get('store_type', 'agricultural'),
        status       = data.get('status', True),
        phone_number = data.get('phone_number'),
        email        = data.get('email'),
        owner_id     = data.get('owner_id'),
        farm_id      = data.get('farm_id'),
        created_by   = user_id,          # ← toujours l'utilisateur connecté
        date_created = datetime.utcnow(),
        date_updated = datetime.utcnow(),
    )
    db.session.add(new_store)
    db.session.commit()
    return jsonify({"msg": "Store created successfully!"}), 201


# ── EDIT store ────────────────────────────────────────────────
@api_store_bp.route('/<int:id>/edit', methods=['PUT'])
@jwt_required()
def edit_store(id):
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)
    store    = Store.query.get_or_404(id)

    # Seul le propriétaire ou un admin peut modifier
    if not user.is_admin and store.created_by != user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json
    store.name         = data.get('name',         store.name)
    store.location     = data.get('location',     store.location)
    store.country      = data.get('country',      store.country)
    store.district     = data.get('district',     store.district)
    store.store_type   = data.get('store_type',   store.store_type)
    store.status       = data.get('status',       store.status)
    store.phone_number = data.get('phone_number', store.phone_number)
    store.email        = data.get('email',        store.email)
    store.modified_by  = user_id
    store.date_updated = datetime.utcnow()

    db.session.commit()
    return jsonify({"msg": "Store updated successfully!"})


# ── GET single store ──────────────────────────────────────────
@api_store_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_store(id):
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)
    store    = Store.query.get_or_404(id)

    # Non-admin ne peut voir que ses propres stores
    if not user.is_admin and store.created_by != user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    return jsonify({
        "id":              store.id,
        "name":            store.name,
        "location":        store.location,
        "country":         store.country,
        "district":        store.district,
        "store_type":      store.store_type,
        "status":          store.status,
        "phone_number":    store.phone_number,
        "email":           store.email,
        "inventory_count": store.inventory_count,
        "sales_count":     store.sales_count,
        "revenue":         store.revenue,
    })


# ── DELETE store ──────────────────────────────────────────────
@api_store_bp.route('/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_store(id):
    identity = get_jwt_identity()
    user_id  = identity['id']
    user     = User.query.get(user_id)
    store    = Store.query.get_or_404(id)

    if not user.is_admin and store.created_by != user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(store)
    db.session.commit()
    return jsonify({"msg": "Store deleted successfully!"})