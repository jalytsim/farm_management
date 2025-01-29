from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import Store, Product, db

api_store_bp = Blueprint('api_store', __name__, url_prefix='/api/store')

# Récupérer tous les magasins
@api_store_bp.route('/', methods=['GET'])
def get_stores():
    stores = Store.query.all()
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
        for store in stores
    ]
    return jsonify(stores=stores_list)

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
