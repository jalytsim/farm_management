from datetime import date
from flask import Blueprint, jsonify
from flask_cors import cross_origin

bp = Blueprint('stgl', __name__)


@bp.route('/stgl', methods=['GET'])
@cross_origin()  # Permet à toutes les origines de faire des requêtes à cette route
def stgl():
    return jsonify(data) 