from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import Product, db

api_product_bp = Blueprint('api_product', __name__, url_prefix='/api/product')

# Récupérer tous les produits
@api_product_bp.route('/', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_list = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "store_id": product.store_id
        }
        for product in products
    ]
    return jsonify(products=products_list)

# Créer un produit
@api_product_bp.route('/create', methods=['POST'])
def create_product():
    data = request.json
    new_product = Product(
        name=data.get('name'),
        description=data.get('description'),
        price=data.get('price'),
        stock=data.get('stock', 0),
        store_id=data.get('store_id')
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"msg": "Product created successfully!"}), 201

# Modifier un produit
@api_product_bp.route('/<int:id>/edit', methods=['PUT'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    data = request.json
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    product.store_id = data.get('store_id', product.store_id)
    
    db.session.commit()
    return jsonify({"msg": "Product updated successfully!"})

# Récupérer un produit spécifique
@api_product_bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    product_data = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "store_id": product.store_id
    }
    return jsonify(product_data)

# Supprimer un produit
@api_product_bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"msg": "Product deleted successfully!"})
