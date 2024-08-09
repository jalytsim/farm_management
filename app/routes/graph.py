# app/routes/farm_routes.py

from flask import Blueprint, jsonify
from flask_cors import cross_origin
from app.utils.graph_utils import get_farm_production_data

bp = Blueprint('graph', __name__)

@bp.route('/farm_data', methods=['GET'])
@cross_origin()
def farm_data():
    data =  get_farm_production_data()
    print(data)
    return jsonify({"status": "success", "data": data}), 200
