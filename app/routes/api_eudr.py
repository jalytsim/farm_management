# api/eudr.py

from flask import Blueprint, request, jsonify
from app.utils.eudr_utils import EUDRClient  # Ton fichier contenant la classe EUDRClient
import xml.etree.ElementTree as ET

api_eudr_bp = Blueprint('api_eudr', __name__, url_prefix='/api/eudr')

# Crée une instance du client EUDR (à adapter pour intégrer à un système de configuration sécurisé)
eudr_client = EUDRClient(username="n00hsq5u", auth_key="nWy8y9w4HtDOcWMPdjjeGGkDIvoo7j13y3R9qT8j")
def extract_dds_identifier(xml_text):
    try:
        root = ET.fromstring(xml_text)
        ns = {
            'S': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns5': 'http://ec.europa.eu/tracesnt/certificate/eudr/submission/v1'
        }
        dds = root.find('.//ns5:ddsIdentifier', ns)
        return dds.text if dds is not None else None
    except ET.ParseError:
        return None
    
def extract_amend_status(xml_text):
    try:
        root = ET.fromstring(xml_text)
        ns = {
            'S': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns5': 'http://ec.europa.eu/tracesnt/certificate/eudr/submission/v1'
        }
        status_el = root.find('.//ns5:status', ns)
        return status_el.text if status_el is not None else None
    except ET.ParseError:
        return None
    
def extract_statement_info(xml_text):
    try:
        root = ET.fromstring(xml_text)
        ns = {
            'S': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns5': 'http://ec.europa.eu/tracesnt/certificate/eudr/retrieval/v1'
        }
        info = {
            'identifier': root.findtext('.//ns5:identifier', default='', namespaces=ns),
            'internalReferenceNumber': root.findtext('.//ns5:internalReferenceNumber', default='', namespaces=ns),
            'referenceNumber': root.findtext('.//ns5:referenceNumber', default='', namespaces=ns),
            'verificationNumber': root.findtext('.//ns5:verificationNumber', default='', namespaces=ns),
            'status': root.findtext('.//ns5:status', default='', namespaces=ns),
            'date': root.findtext('.//ns5:date', default='', namespaces=ns),
            'updatedBy': root.findtext('.//ns5:updatedBy', default='', namespaces=ns)
        }
        return info
    except ET.ParseError:
        return None
    
def extract_verification_info(xml_text):
    try:
        root = ET.fromstring(xml_text)
        ns = {
            'S': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns5': 'http://ec.europa.eu/tracesnt/certificate/eudr/retrieval/v1',
            'ns3': 'http://ec.europa.eu/tracesnt/certificate/eudr/model/v1'
        }

        info = {
            'referenceNumber': root.findtext('.//ns5:referenceNumber', default='', namespaces=ns),
            'activityType': root.findtext('.//ns5:activityType', default='', namespaces=ns),
            'status': root.findtext('.//ns3:status', default='', namespaces=ns),
            'statusDate': root.findtext('.//ns3:date', default='', namespaces=ns),
            'operatorName': root.findtext('.//ns3:name', default='', namespaces=ns),
            'operatorCountry': root.findtext('.//ns3:country', default='', namespaces=ns),
            'descriptionOfGoods': root.findtext('.//ns3:descriptionOfGoods', default='', namespaces=ns),
            'netWeight': root.findtext('.//ns3:netWeight', default='', namespaces=ns),
            'supplementaryUnit': root.findtext('.//ns3:supplementaryUnit', default='', namespaces=ns),
            'supplementaryUnitQualifier': root.findtext('.//ns3:supplementaryUnitQualifier', default='', namespaces=ns),
            'hsHeading': root.findtext('.//ns3:hsHeading', default='', namespaces=ns),
            'scientificName': root.findtext('.//ns3:scientificName', default='', namespaces=ns),
            'commonName': root.findtext('.//ns3:commonName', default='', namespaces=ns)
        }

        return info
    except ET.ParseError:
        return None
    
def extract_internal_ref_statements(xml_text):
    try:
        root = ET.fromstring(xml_text)
        ns = {
            'S': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns5': 'http://ec.europa.eu/tracesnt/certificate/eudr/retrieval/v1'
        }

        statements = []

        for info in root.findall('.//ns5:statementInfo', ns):
            statements.append({
                'identifier': info.findtext('ns5:identifier', default='', namespaces=ns),
                'internalReferenceNumber': info.findtext('ns5:internalReferenceNumber', default='', namespaces=ns),
                'referenceNumber': info.findtext('ns5:referenceNumber', default='', namespaces=ns),
                'verificationNumber': info.findtext('ns5:verificationNumber', default='', namespaces=ns),
                'status': info.findtext('ns5:status', default='', namespaces=ns),
                'date': info.findtext('ns5:date', default='', namespaces=ns),
                'updatedBy': info.findtext('ns5:updatedBy', default='', namespaces=ns)
            })

        return statements
    except ET.ParseError:
        return None




@api_eudr_bp.route('/submit', methods=['POST'])
def submit_statement():
    data = request.json
    geojson = data.get("geojson")
    statement = data.get("statement")
    response = eudr_client.submit_statement(geojson, statement)

    dds_identifier = extract_dds_identifier(response.text)
    return jsonify({
        "status": response.status_code,
        "ddsIdentifier": dds_identifier,
        "raw": response.text if not dds_identifier else None  # optionnel, pour debug
    })

@api_eudr_bp.route('/amend', methods=['POST'])
def amend_statement():
    data = request.json
    geojson = data.get("geojson")
    dds_id = data.get("ddsIdentifier")
    statement = data.get("statement")
    response = eudr_client.amend_statement(geojson, dds_id, statement)

    status = extract_amend_status(response.text)

    return jsonify({
        "status": response.status_code,
        "amendStatus": status,
        "raw": response.text if not status else None
    })


@api_eudr_bp.route('/retract/<dds_id>', methods=['DELETE'])
def retract_statement(dds_id):
    response = eudr_client.retract_statement(dds_id)
    return jsonify({"status": response.status_code, "response": response.text})

@api_eudr_bp.route('/info/by-internal-ref/<reference>', methods=['GET'])
def get_by_internal_reference(reference):
    response = eudr_client.get_by_internal_reference(reference)
    statements = extract_internal_ref_statements(response.text)

    if statements is not None:
        return jsonify({
            "status": response.status_code,
            "statements": statements
        })
    else:
        return jsonify({
            "status": response.status_code,
            "error": "Unable to parse XML",
            "raw": response.text
        })


@api_eudr_bp.route('/info/by-dds-id/<dds_id>', methods=['GET'])
def get_by_dds_identifier(dds_id):
    response = eudr_client.get_by_dds_identifier(dds_id)
    info = extract_statement_info(response.text)
    
    if info:
        return jsonify({
            "status": response.status_code,
            **info
        })
    else:
        return jsonify({
            "status": response.status_code,
            "error": "Unable to parse XML",
            "raw": response.text
        })


@api_eudr_bp.route('/info/by-ref-verification', methods=['POST'])
def get_by_reference_and_verification():
    data = request.json
    reference = data.get("reference")
    verification = data.get("verification")
    response = eudr_client.get_by_reference_and_verification(reference, verification)

    info = extract_verification_info(response.text)

    if info:
        return jsonify({
            "status": response.status_code,
            **info
        })
    else:
        return jsonify({
            "status": response.status_code,
            "error": "Unable to parse XML",
            "raw": response.text
        })

