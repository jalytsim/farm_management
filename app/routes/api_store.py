from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import Store, Product, db

from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Store, User

api_store_bp = Blueprint('api_store', __name__, url_prefix='/api/store')

# Récupérer tous les magasins

@api_store_bp.route('/', methods=['GET'])
@jwt_required()
def get_stores():
    identity = get_jwt_identity()  # {'id': user.id, 'user_type': ...}
    user_id = identity['id']

    user = User.query.get(user_id)

    # Pagination (optionnel)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if user.is_admin:
        stores = Store.query.paginate(page=page, per_page=per_page)
    else:
        stores = Store.query.filter_by(created_by=user_id).paginate(page=page, per_page=per_page)

    stores_list = [
        {
            "id": store.id,
            "name": store.name,
            "location": store.location,
            "country": store.country,
            "district": store.district,
            "store_type": store.store_type,
            "status": store.status,
            "phone_number": store.phone_number,
            "email": store.email,
            "inventory_count": store.inventory_count,
            "sales_count": store.sales_count,
            "revenue": store.revenue
        }
        for store in stores.items
    ]

    return jsonify(
        stores=stores_list,
        total_pages=stores.pages,
        current_page=stores.page,
    )


# Créer un magasin
@api_store_bp.route('/create', methods=['POST'])
def create_store():
    data = request.json
    new_store = Store(
        name=data.get('name'),
        location=data.get('location'),
        country=data.get('country'),
        district=data.get('district'),
        store_type=data.get('store_type', 'agricultural'),
        status=data.get('status', True),
        phone_number=data.get('phone_number'),
        email=data.get('email'),
        owner_id=data.get('owner_id'),
        farm_id=data.get('farm_id'),
        created_by=data.get('created_by'),
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )
    db.session.add(new_store)
    db.session.commit()
    return jsonify({"msg": "Store created successfully!"}), 201

# Modifier un magasin
@api_store_bp.route('/<int:id>/edit', methods=['PUT'])
def edit_store(id):
    store = Store.query.get_or_404(id)
    data = request.json
    store.name = data.get('name', store.name)
    store.location = data.get('location', store.location)
    store.country = data.get('country', store.country)
    store.district = data.get('district', store.district)
    store.store_type = data.get('store_type', store.store_type)
    store.status = data.get('status', store.status)
    store.phone_number = data.get('phone_number', store.phone_number)
    store.email = data.get('email', store.email)
    store.modified_by = data.get('modified_by', store.modified_by)
    store.date_updated = datetime.utcnow()
    
    db.session.commit()
    return jsonify({"msg": "Store updated successfully!"})

# Récupérer un magasin spécifique
@api_store_bp.route('/<int:id>', methods=['GET'])
def get_store(id):
    store = Store.query.get_or_404(id)
    store_data = {
        "id": store.id,
        "name": store.name,
        "location": store.location,
        "country": store.country,
        "district": store.district,
        "store_type": store.store_type,
        "status": store.status,
        "phone_number": store.phone_number,
        "email": store.email,
        "inventory_count": store.inventory_count,
        "sales_count": store.sales_count,
        "revenue": store.revenue
    }
    return jsonify(store_data)

# Supprimer un magasin
@api_store_bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_store(id):
    store = Store.query.get_or_404(id)
    db.session.delete(store)
    db.session.commit()
    return jsonify({"msg": "Store deleted successfully!"})
