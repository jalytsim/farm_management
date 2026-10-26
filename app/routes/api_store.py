# app/routes/api_store.py
# =============================================================================
#  Magasins et entrepôts.
#
#  ★ MODIFIÉ — champs entrepôt (bourse 2tume) :
#    code, is_certified, capacity_tonnes, accepted_crop_ids
#  · GET / accepte ?store_type=warehouse (ReceiptReception et WarehouseDashboard
#    l'envoyaient déjà, mais le filtre était ignoré) et ?per_page=.
#  · Le personnel d'entrepôt (warehouse_operator, qa_tester) voit tous les
#    entrepôts, pas seulement ceux qu'il a créés.
#  · Seul un admin peut certifier un entrepôt : c'est la certification qui
#    autorise l'émission de reçus.
# =============================================================================

from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Store, Product, User, Crop, db

api_store_bp = Blueprint('api_store', __name__, url_prefix='/api/store')

# Rôles qui travaillent dans les entrepôts (mêmes valeurs que api_receipt.py).
WAREHOUSE_ROLES = {'warehouse_operator', 'qa_tester'}


# ── Helpers ──────────────────────────────────────────────────────────────────
def _current_user():
    identity = get_jwt_identity()
    user_id = identity['id'] if isinstance(identity, dict) else identity
    return User.query.get(user_id)


def _store_dict(store):
    return {
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
        # ★ Entrepôt
        "code":              store.code,
        "is_certified":      bool(store.is_certified),
        "capacity_tonnes":   float(store.capacity_tonnes) if store.capacity_tonnes is not None else None,
        "accepted_crop_ids": [c.id for c in (store.accepted_crops or [])],
        "accepted_crops":    [c.name for c in (store.accepted_crops or [])],
    }


def _apply_warehouse_fields(store, data, user):
    """Lit code, capacité, marchandises acceptées et certification.
    Retourne un message d'erreur, ou None."""
    if 'code' in data:
        code = (data.get('code') or '').strip().upper() or None
        if code:
            other = Store.query.filter(Store.code == code, Store.id != store.id).first()
            if other:
                return f"The code {code} is already used by {other.name}."
        store.code = code

    if 'capacity_tonnes' in data:
        raw = data.get('capacity_tonnes')
        if raw in (None, ''):
            store.capacity_tonnes = None
        else:
            try:
                capacity = Decimal(str(raw))
            except (InvalidOperation, ValueError):
                return "Capacity must be a number."
            if capacity < 0:
                return "Capacity cannot be negative."
            store.capacity_tonnes = capacity

    if 'accepted_crop_ids' in data:
        ids = [int(i) for i in (data.get('accepted_crop_ids') or []) if str(i).isdigit()]
        store.accepted_crops = Crop.query.filter(Crop.id.in_(ids)).all() if ids else []

    # La certification autorise l'émission de reçus : réservée à l'admin.
    if 'is_certified' in data and user.is_admin:
        store.is_certified = bool(data.get('is_certified'))

    return None


# ── GET all stores (filtered by account) ─────────────────────────────────────
@api_store_bp.route('/', methods=['GET'])
@jwt_required()
def get_stores():
    user = _current_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    page     = request.args.get('page',     1,  type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    query = Store.query
    store_type = request.args.get('store_type')
    if store_type:
        query = query.filter(Store.store_type == store_type)

    # Admin → tout. Personnel d'entrepôt → tous les entrepôts. Sinon → ses magasins.
    if not user.is_admin:
        if user.user_type in WAREHOUSE_ROLES:
            query = query.filter(Store.store_type == 'warehouse')
        else:
            query = query.filter(Store.created_by == user.id)

    stores = query.order_by(Store.name).paginate(page=page, per_page=per_page)

    return jsonify(
        stores=[_store_dict(s) for s in stores.items],
        total_pages=stores.pages,
        current_page=stores.page,
    )


# ── CREATE store ─────────────────────────────────────────────────────────────
@api_store_bp.route('/create', methods=['POST'])
@jwt_required()
def create_store():
    user = _current_user()
    data = request.get_json(silent=True) or {}

    for field in ('name', 'location', 'country', 'district'):
        if not (data.get(field) or '').strip():
            return jsonify({"msg": f"{field.capitalize()} is required"}), 400

    new_store = Store(
        name         = data.get('name').strip(),
        location     = data.get('location').strip(),
        country      = data.get('country').strip(),
        district     = data.get('district').strip(),
        store_type   = data.get('store_type', 'agricultural'),
        status       = data.get('status', True),
        phone_number = data.get('phone_number'),
        email        = data.get('email'),
        owner_id     = data.get('owner_id'),
        farm_id      = data.get('farm_id'),
        created_by   = user.id,
        date_created = datetime.utcnow(),
        date_updated = datetime.utcnow(),
    )
    error = _apply_warehouse_fields(new_store, data, user)
    if error:
        return jsonify({"msg": error}), 400

    db.session.add(new_store)
    db.session.commit()
    return jsonify({"msg": "Store created successfully!", "store": _store_dict(new_store)}), 201


# ── EDIT store ───────────────────────────────────────────────────────────────
@api_store_bp.route('/<int:id>/edit', methods=['PUT'])
@jwt_required()
def edit_store(id):
    user  = _current_user()
    store = Store.query.get_or_404(id)

    # Seul le propriétaire ou un admin peut modifier
    if not user.is_admin and store.created_by != user.id:
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    store.name         = data.get('name',         store.name)
    store.location     = data.get('location',     store.location)
    store.country      = data.get('country',      store.country)
    store.district     = data.get('district',     store.district)
    store.store_type   = data.get('store_type',   store.store_type)
    store.status       = data.get('status',       store.status)
    store.phone_number = data.get('phone_number', store.phone_number)
    store.email        = data.get('email',        store.email)

    error = _apply_warehouse_fields(store, data, user)
    if error:
        db.session.rollback()
        return jsonify({"msg": error}), 400

    store.modified_by  = user.id
    store.date_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Store updated successfully!", "store": _store_dict(store)})


# ── GET single store ─────────────────────────────────────────────────────────
@api_store_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_store(id):
    user  = _current_user()
    store = Store.query.get_or_404(id)

    allowed = (user.is_admin or store.created_by == user.id
               or (user.user_type in WAREHOUSE_ROLES and store.store_type == 'warehouse'))
    if not allowed:
        return jsonify({"msg": "Unauthorized"}), 403

    return jsonify(_store_dict(store))


# ── DELETE store ─────────────────────────────────────────────────────────────
@api_store_bp.route('/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_store(id):
    user  = _current_user()
    store = Store.query.get_or_404(id)

    if not user.is_admin and store.created_by != user.id:
        return jsonify({"msg": "Unauthorized"}), 403

    # Un entrepôt qui a émis des reçus ne se supprime pas : les reçus et la
    # vérification publique en dépendent. On le désactive à la place.
    if store.store_type == 'warehouse' and getattr(store, 'receipts', None):
        return jsonify({"msg": "This warehouse has issued receipts. Deactivate it instead."}), 409

    db.session.delete(store)
    db.session.commit()
    return jsonify({"msg": "Store deleted successfully!"})