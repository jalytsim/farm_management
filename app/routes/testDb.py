from flask import Blueprint, jsonify
from ..models import db, District

test = Blueprint('test', __name__)

@test.route('/test_db')
def test_db():
    try:
        # Essayez de faire une requête simple pour tester la connexion
        districts = District.query.all()
        return jsonify({"message": "Connexion réussie", "districts": [district.name for district in districts]})
    except Exception as e:
        return jsonify({"message": "Erreur de connexion", "error": str(e)})
