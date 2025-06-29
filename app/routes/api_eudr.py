# api/eudr.py
import base64
import json
from flask import Blueprint, request, jsonify
from app.utils.eudr_utils import EUDRClient, extract_amend_status, extract_dds_identifier, extract_internal_ref_statements, extract_statement_info, extract_verification_info  # Ton fichier contenant la classe EUDRClient
import xml.etree.ElementTree as ET
from app.models import db, EUDRStatement
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from dateutil import parser  # pip install python-dateutil si nécessaire



api_eudr_bp = Blueprint('api_eudr', __name__, url_prefix='/api/eudr')

# Crée une instance du client EUDR (à adapter pour intégrer à un système de configuration sécurisé)
eudr_client = EUDRClient(username="n00hsq5u", auth_key="axtAeJM0216XSNGfI7RCztDKOSh99NkuAjLmXAHR")


@api_eudr_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_statement():
    data = request.json
    geojson = data.get("geojson")
    statement = data.get("statement")
    identity = get_jwt_identity()
    user_id = identity['id'] if identity else None

    response = eudr_client.submit_statement(geojson, statement)
    dds_identifier = extract_dds_identifier(response.text)

    if response.status_code == 200 and dds_identifier:
        try:
            new_record = EUDRStatement(
                internal_reference_number=statement.get('internalReferenceNumber'),
                dds_identifier=dds_identifier,
                activity_type=statement.get('activityType'),
                border_cross_country=statement.get('borderCrossCountry'),
                country_of_activity=statement.get('countryOfActivity'),
                comment=statement.get('comment'),
                geo_location_confidential=statement.get('geoLocationConfidential', False),

                operator_identifier_type=statement.get('operator', {}).get('identifierType'),
                operator_identifier_value=statement.get('operator', {}).get('identifierValue'),
                operator_name=statement.get('operator', {}).get('name'),
                operator_country=statement.get('operator', {}).get('country'),
                operator_address=statement.get('operator', {}).get('address'),
                operator_email=statement.get('operator', {}).get('email'),
                operator_phone=statement.get('operator', {}).get('phone'),

                description_of_goods=statement.get('descriptionOfGoods'),
                hs_heading=statement.get('hsHeading'),
                scientific_name=statement.get('speciesInfo', {}).get('scientificName'),
                common_name=statement.get('speciesInfo', {}).get('commonName'),

                volume=statement.get('goodsMeasure', {}).get('volume'),
                net_weight=statement.get('goodsMeasure', {}).get('netWeight'),
                supplementary_unit=statement.get('goodsMeasure', {}).get('supplementaryUnit'),
                supplementary_unit_qualifier=statement.get('goodsMeasure', {}).get('supplementaryUnitQualifier'),

                producers_json=json.dumps(statement.get('producers', [])),
                last_response_code=response.status_code,
                last_response_text=response.text[:3000],

                created_by=user_id,
                updated_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.session.add(new_record)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": 500,
                "error": "Failed to save EUDR statement locally.",
                "details": str(e)
            }), 500

    return jsonify({
        "status": response.status_code,
        "ddsIdentifier": dds_identifier,
        "raw": response.text if not dds_identifier else None
    })


@api_eudr_bp.route('/amend', methods=['POST'])
@jwt_required()
def amend_statement():
    data = request.json
    geojson = data.get("geojson")
    dds_id = data.get("ddsIdentifier")
    statement = data.get("statement")
    identity = get_jwt_identity()
    user_id = identity['id'] if identity else None

    response = eudr_client.amend_statement(geojson, dds_id, statement)
    status = extract_amend_status(response.text)

    if response.status_code == 200 and status:
        try:
            record = EUDRStatement.query.filter_by(dds_identifier=dds_id).first()
            if record:
                record.internal_reference_number = statement.get('internalReferenceNumber', record.internal_reference_number)
                record.activity_type = statement.get('activityType', record.activity_type)
                record.border_cross_country = statement.get('borderCrossCountry', record.border_cross_country)
                record.country_of_activity = statement.get('countryOfActivity', record.country_of_activity)
                record.comment = statement.get('comment', record.comment)
                record.geo_location_confidential = statement.get('geoLocationConfidential', record.geo_location_confidential)

                record.operator_identifier_type = statement.get('operator', {}).get('identifierType', record.operator_identifier_type)
                record.operator_identifier_value = statement.get('operator', {}).get('identifierValue', record.operator_identifier_value)
                record.operator_name = statement.get('operator', {}).get('name', record.operator_name)
                record.operator_country = statement.get('operator', {}).get('country', record.operator_country)
                record.operator_address = statement.get('operator', {}).get('address', record.operator_address)
                record.operator_email = statement.get('operator', {}).get('email', record.operator_email)
                record.operator_phone = statement.get('operator', {}).get('phone', record.operator_phone)

                record.description_of_goods = statement.get('descriptionOfGoods', record.description_of_goods)
                record.hs_heading = statement.get('hsHeading', record.hs_heading)
                record.scientific_name = statement.get('speciesInfo', {}).get('scientificName', record.scientific_name)
                record.common_name = statement.get('speciesInfo', {}).get('commonName', record.common_name)

                record.volume = statement.get('goodsMeasure', {}).get('volume', record.volume)
                record.net_weight = statement.get('goodsMeasure', {}).get('netWeight', record.net_weight)
                record.supplementary_unit = statement.get('goodsMeasure', {}).get('supplementaryUnit', record.supplementary_unit)
                record.supplementary_unit_qualifier = statement.get('goodsMeasure', {}).get('supplementaryUnitQualifier', record.supplementary_unit_qualifier)

                record.producers_json = json.dumps(statement.get('producers', []))
                record.last_response_code = response.status_code
                record.last_response_text = response.text[:3000]
                record.modified_by = user_id
                record.updated_at = datetime.utcnow()

                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": 500,
                "error": "Failed to update EUDR statement locally.",
                "details": str(e)
            }), 500

    return jsonify({
        "status": response.status_code,
        "amendStatus": status,
        "raw": response.text if not status else None
    })

@api_eudr_bp.route('/retract/<dds_id>', methods=['DELETE'])
def retract_statement(dds_id):
    response = eudr_client.retract_statement(dds_id)

    if response.status_code == 200:
        try:
            record = EUDRStatement.query.filter_by(dds_identifier=dds_id).first()
            if record:
                db.session.delete(record)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": 500,
                "error": "Failed to delete local EUDR statement.",
                "details": str(e)
            }), 500

    return jsonify({"status": response.status_code, "response": response.text})


@api_eudr_bp.route('/info/by-internal-ref/<reference>', methods=['GET'])
@jwt_required()
def get_by_internal_reference(reference):
    from dateutil import parser
    import traceback

    identity = get_jwt_identity()
    user_id = identity['id'] if identity else None

    response = eudr_client.get_by_internal_reference(reference)
    statements = extract_internal_ref_statements(response.text)

    if statements is not None:
        print("🧪 DEBUG - Statements reçus :", statements)
        try:
            for stmt_data in statements:
                print("📄 Traitement de l'entrée DDS :", stmt_data)

                identifier = stmt_data.get("identifier")
                record = EUDRStatement.query.filter_by(dds_identifier=identifier).first()

                if record:
                    record.status = stmt_data.get("status", record.status)
                    record.reference_number = stmt_data.get("referenceNumber", record.reference_number)
                    record.verification_code = stmt_data.get("verificationNumber", record.verification_code)

                    try:
                        raw_date = stmt_data.get("date")
                        if raw_date:
                            record.status_date = parser.isoparse(raw_date)
                    except Exception as e:
                        print("❌ Erreur parsing date (update):", raw_date, str(e))

                    record.modified_by = user_id
                    record.updated_at = datetime.utcnow()
                else:
                    try:
                        raw_date = stmt_data.get("date")
                        status_date = parser.isoparse(raw_date) if raw_date else None
                    except Exception as e:
                        print("❌ Erreur parsing date (nouveau):", raw_date, str(e))
                        status_date = None

                    new_stmt = EUDRStatement(
                        dds_identifier=identifier,
                        internal_reference_number=stmt_data.get("internalReferenceNumber"),
                        reference_number=stmt_data.get("referenceNumber"),
                        verification_code=stmt_data.get("verificationNumber"),
                        status=stmt_data.get("status"),
                        status_date=status_date,
                        created_by=user_id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(new_stmt)

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": 500,
                "error": "Exception raised during internal-ref sync.",
                "trace": traceback.format_exc()
            }), 500

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
@jwt_required()
def get_by_dds_identifier(dds_id):
    identity = get_jwt_identity()
    user_id = identity['id'] if identity else None

    response = eudr_client.get_by_dds_identifier(dds_id)
    info = extract_statement_info(response.text)

    if not info:
        return jsonify({
            "status": response.status_code,
            "error": "Unable to parse XML",
            "raw": response.text
        }), 500

    try:
        stmt = EUDRStatement.query.filter_by(dds_identifier=dds_id).first()
        if stmt:
            stmt.reference_number = info.get('referenceNumber', stmt.reference_number)
            stmt.verification_code = info.get('verificationCode', stmt.verification_code)
            stmt.status = info.get('status', stmt.status)

            date_str = info.get('date')
            if date_str:
                try:
                    stmt.status_date = datetime.fromisoformat(date_str)
                except ValueError:
                    pass

            if user_id:
                stmt.modified_by = user_id

            stmt.updated_at = datetime.utcnow()
            db.session.commit()
    except Exception as e:
        return jsonify({
            "status": 500,
            "error": "Failed to update reference/verification numbers.",
            "details": str(e)
        }), 500

    return jsonify({
        "status": response.status_code,
        **info
    })

@api_eudr_bp.route('/info/by-ref-verification', methods=['POST'])
def get_by_reference_and_verification():
    data = request.json
    reference = data.get("reference")
    verification = data.get("verification")

    # Requête distante (SOAP)
    response = eudr_client.get_by_reference_and_verification(reference, verification)
    info = extract_verification_info(response.text)

    # Requête locale (base de données)
    local_record = EUDRStatement.query.filter_by(
        reference_number=reference,
        verification_code=verification
    ).first()

    local_data = None
    if local_record:
        local_data = {
            "id": local_record.id,
            "internal_reference_number": local_record.internal_reference_number,
            "dds_identifier": local_record.dds_identifier,
            "activity_type": local_record.activity_type,
            "border_cross_country": local_record.border_cross_country,
            "country_of_activity": local_record.country_of_activity,
            "comment": local_record.comment,
            "geo_location_confidential": local_record.geo_location_confidential,
            "operator_name": local_record.operator_name,
            "operator_country": local_record.operator_country,
            "operator_address": local_record.operator_address,
            "operator_email": local_record.operator_email,
            "operator_phone": local_record.operator_phone,
            "description_of_goods": local_record.description_of_goods,
            "hs_heading": local_record.hs_heading,
            "scientific_name": local_record.scientific_name,
            "common_name": local_record.common_name,
            "volume": local_record.volume,
            "net_weight": local_record.net_weight,
            "supplementary_unit": local_record.supplementary_unit,
            "supplementary_unit_qualifier": local_record.supplementary_unit_qualifier,
            "producers_json": local_record.producers_json,
            "reference_number": local_record.reference_number,
            "verification_code": local_record.verification_code,
            "status": local_record.status,
            "status_date": local_record.status_date.isoformat() if local_record.status_date else None,
            "created_at": local_record.created_at.isoformat() if local_record.created_at else None,
            "updated_at": local_record.updated_at.isoformat() if local_record.updated_at else None
        }

    if info:
        return jsonify({
            "status": response.status_code,
            "remote_data": info,
            "local_data": local_data
        })
    else:
        return jsonify({
            "status": response.status_code,
            "error": "Unable to parse XML",
            "raw": response.text,
            "local_data": local_data
        })



@api_eudr_bp.route('/', methods=['GET'])
def list_statements():
    statements = EUDRStatement.query.all()
    results = []
    for s in statements:
        results.append({
            "id": s.id,
            "internal_reference_number": s.internal_reference_number,
            "dds_identifier": s.dds_identifier,
            "activity_type": s.activity_type,
            "border_cross_country": s.border_cross_country,
            "country_of_activity": s.country_of_activity,
            "comment": s.comment,
            "geo_location_confidential": s.geo_location_confidential,
            "operator_name": s.operator_name,
            "operator_country": s.operator_country,
            "description_of_goods": s.description_of_goods,
            "hs_heading": s.hs_heading,
            "scientific_name": s.scientific_name,
            "common_name": s.common_name,
            "producers_json": s.producers_json,
            "created_at": s.created_at,
            "updated_at": s.updated_at
        })
    return jsonify({"status": "success", "statements": results})
