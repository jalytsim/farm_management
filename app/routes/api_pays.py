from flask import Blueprint, jsonify, request
from app.models import Pays, db

bp = Blueprint('api_pays', __name__, url_prefix='/api/pays')

# Get all pays records
@bp.route('/', methods=['GET'])
def index():
    pays_list = Pays.query.all()
    pays_data = [
        {
            "id": pays.id,
            "code": pays.code,
            "alpha2": pays.alpha2,
            "alpha3": pays.alpha3,
            "nom_en_gb": pays.nom_en_gb,
            "nom_fr_fr": pays.nom_fr_fr
        } 
        for pays in pays_list
    ]
    return jsonify(pays=pays_data)

# Create a new pays record
@bp.route('/create', methods=['POST'])
def create_pays():
    data = request.json
    code = data.get('code')
    alpha2 = data.get('alpha2')
    alpha3 = data.get('alpha3')
    nom_en_gb = data.get('nom_en_gb')
    nom_fr_fr = data.get('nom_fr_fr')

    new_pays = Pays(
        code=code,
        alpha2=alpha2,
        alpha3=alpha3,
        nom_en_gb=nom_en_gb,
        nom_fr_fr=nom_fr_fr
    )

    db.session.add(new_pays)
    db.session.commit()
    return jsonify({"msg": "Pays created successfully!"}), 201

# Edit an existing pays record
@bp.route('/<int:id>/edit', methods=['PUT'])
def edit_pays(id):
    pays = Pays.query.get_or_404(id)
    data = request.json

    pays.code = data.get('code')
    pays.alpha2 = data.get('alpha2')
    pays.alpha3 = data.get('alpha3')
    pays.nom_en_gb = data.get('nom_en_gb')
    pays.nom_fr_fr = data.get('nom_fr_fr')

    db.session.commit()
    return jsonify({"msg": "Pays updated successfully!"})

# Get a specific pays record by id
@bp.route('/<int:id>', methods=['GET'])
def get_pays(id):
    pays = Pays.query.get_or_404(id)
    pays_data = {
        'id': pays.id,
        'code': pays.code,
        'alpha2': pays.alpha2,
        'alpha3': pays.alpha3,
        'nom_en_gb': pays.nom_en_gb,
        'nom_fr_fr': pays.nom_fr_fr
    }
    return jsonify(pays_data)

# Delete a pays record
@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_pays(id):
    pays = Pays.query.get_or_404(id)
    db.session.delete(pays)
    db.session.commit()
    return jsonify({"msg": "Pays deleted successfully!"})
