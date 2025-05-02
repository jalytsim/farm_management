# api/eudr.py

from flask import Blueprint, request, jsonify
from app.utils.eudr_utils import EUDRClient  # Ton fichier contenant la classe EUDRClient

api_eudr_bp = Blueprint('api_eudr', __name__, url_prefix='/api/eudr')

# Crée une instance du client EUDR (à adapter pour intégrer à un système de configuration sécurisé)
eudr_client = EUDRClient(username="your_username", auth_key="your_auth_key")

@api_eudr_bp.route('/submit', methods=['POST'])
def submit_statement():
    data = request.json
    geojson = data.get("geojson")
    statement = data.get("statement")
    response = eudr_client.submit_statement(geojson, statement)
    return jsonify({"status": response.status_code, "response": response.text})

@api_eudr_bp.route('/amend', methods=['POST'])
def amend_statement():
    data = request.json
    geojson = data.get("geojson")
    dds_id = data.get("ddsIdentifier")
    statement = data.get("statement")
    response = eudr_client.amend_statement(geojson, dds_id, statement)
    return jsonify({"status": response.status_code, "response": response.text})

@api_eudr_bp.route('/retract/<dds_id>', methods=['DELETE'])
def retract_statement(dds_id):
    response = eudr_client.retract_statement(dds_id)
    return jsonify({"status": response.status_code, "response": response.text})

@api_eudr_bp.route('/info/by-internal-ref/<reference>', methods=['GET'])
def get_by_internal_reference(reference):
    response = eudr_client.get_by_internal_reference(reference)
    return jsonify({"status": response.status_code, "response": response.text})

@api_eudr_bp.route('/info/by-dds-id/<dds_id>', methods=['GET'])
def get_by_dds_identifier(dds_id):
    response = eudr_client.get_by_dds_identifier(dds_id)
    return jsonify({"status": response.status_code, "response": response.text})

@api_eudr_bp.route('/info/by-ref-verification', methods=['POST'])
def get_by_reference_and_verification():
    data = request.json
    reference = data.get("reference")
    verification = data.get("verification")
    response = eudr_client.get_by_reference_and_verification(reference, verification)
    return jsonify({"status": response.status_code, "response": response.text})
