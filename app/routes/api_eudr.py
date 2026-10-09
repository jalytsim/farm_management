# api/eudr.py
import base64
import json
from flask import Blueprint, request, jsonify
from app.utils.eudr_utils import (
    geojson_errors, EU_COUNTRIES, CATTLE_HS_PREFIXES, TIMBER_HS_CHAPTERS, GEOJSON_GEOMETRY_TYPES,
    OPERATOR_COUNTRY, OPERATOR_IS_EU, ALLOWED_ACTIVITY_TYPES, ALLOWED_OPERATOR_ROLES,
)
from app.utils.eudr_utils import EUDRClient, extract_amend_status, extract_dds_identifier, extract_internal_ref_statements, extract_statement_info, extract_verification_info, extract_soap_fault, extract_operator_identity  # Ton fichier contenant la classe EUDRClient
import xml.etree.ElementTree as ET
from app.models import db, EUDRStatement
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app.utils.decorators import permission_required, load_current_user

# Clé du JSON User.permissions cochée dans User Manager (admins toujours autorisés)
DDS_PERMISSION = 'eudr_dds'
from dateutil import parser  # pip install python-dateutil si nécessaire
import os


api_eudr_bp = Blueprint('api_eudr', __name__, url_prefix='/api/eudr')


def _hs_code_error(statement):
    """
    Refuse d'avance un code HS que TRACES a déjà rejeté (verdicts stockés par
    hscode_sync.py), avec les codes acceptés de la même position. Code inconnu
    de la table : on laisse TRACES trancher.
    """
    from app.models import HSCodeSubheading
    from app.utils.hscode_sync import lookup_hs_status
    digits = ''.join(ch for ch in str(statement.get('hsHeading') or '') if ch.isdigit())
    if not digits or lookup_hs_status(digits) is not False:
        return None
    from app.models import HSCode
    valid = [s.code for s in HSCodeSubheading.query
             .filter(HSCodeSubheading.code.like(digits[:4] + '%'), HSCodeSubheading.traces_valid.is_(True)).all()]
    valid += [h.digits for h in HSCode.query.filter_by(traces_valid=True).all()
              if h.digits and digits.startswith(h.digits[:4])]
    valid = sorted(set(valid))
    # Correction automatique quand il n'y a aucun doute : position "…00" (ex.
    # 180100, envoyé par d'anciennes versions du formulaire) ou position à
    # 4 chiffres seule acceptée (ex. 010221 → 0102). TRACES accepte la position.
    heading = digits[:4]
    if len(digits) > 4 and heading in valid and (digits[4:].strip('0') == '' or valid == [heading]):
        print(f"[EUDR] HS code {digits} refused by TRACES, sent as {heading}", flush=True)
        statement['hsHeading'] = heading
        return None
    hint = f" Accepted codes for heading {heading}: {', '.join(valid)}." if valid else ""
    return f"HS code {digits} is not accepted by the EUDR information system (TRACES).{hint}"


def _owned_query(user):
    """DDS visibles par le compte : toutes pour un admin, les siennes sinon."""
    query = EUDRStatement.query
    return query if user.is_admin else query.filter(EUDRStatement.created_by == user.id)


def _forbidden_dds(dds_id):
    """Réponse 404 si un non-admin vise une DDS qu'il n'a pas créée, sinon None."""
    user = load_current_user()
    if user.is_admin or _owned_query(user).filter_by(dds_identifier=dds_id).first():
        return None
    return jsonify({"status": 404, "error": "DDS not found for this account."}), 404


def _sent_summary(statement):
    """Champs clés réellement envoyés à TRACES, renvoyés avec l'erreur : le
    Fault TRACES ne dit jamais quelle valeur il rejette (ex. HS-CODE-INVALID)."""
    goods = statement.get('goodsMeasure') or {}
    return {
        'hsHeading':  ''.join(ch for ch in str(statement.get('hsHeading') or '') if ch.isdigit()),
        'activityType': statement.get('activityType'),
        'countryOfActivity': statement.get('countryOfActivity'),
        'descriptionOfGoods': statement.get('descriptionOfGoods'),
        'netWeight': goods.get('netWeight'),
        'supplementaryUnit': goods.get('supplementaryUnit'),
        'supplementaryUnitQualifier': goods.get('supplementaryUnitQualifier'),
        'producerCountries': [p.get('country') for p in (statement.get('producers') or []) if isinstance(p, dict)],
    }


def _to_float(value):
    """Les colonnes Float rejettent '' ou '1 000 kg' : on stocke None si non numérique."""
    if value is None or str(value).strip() == '':
        return None
    raw = str(value).lower().replace('kg', '').replace(' ', '').replace(' ', '')
    raw = raw.replace(',', '.') if (',' in raw and '.' not in raw) else raw.replace(',', '')
    try:
        return float(raw)
    except ValueError:
        return None

# Crée une instance du client EUDR (à adapter pour intégrer à un système de configuration sécurisé)
# 1. Credentials via variable d'env, avec fallback statique si absente
# ⚠️ C'est le login WS-Security (EUDR_USERNAME) qui décide de l'opérateur
# sous lequel TRACES enregistre une DDS en operatorRole=OPERATOR : aucun
# identifiant d'entreprise (EORI, TIN…) n'est envoyé dans l'enveloppe.
EUDR_USERNAME_FROM_ENV = bool(os.environ.get("EUDR_USERNAME"))
eudr_client = EUDRClient(
    username=os.environ.get("EUDR_USERNAME", "n00hsq5u"),
    auth_key=os.environ.get("EUDR_AUTH_KEY", "axtAeJM0216XSNGfI7RCztDKOSh99NkuAjLmXAHR"),
    client_id=os.environ.get("EUDR_CLIENT_ID", "eudr-repository"),
    # En-tête BodyIdentity désactivé par défaut : avec "UGhPT7Jq", TRACES répond
    # UnauthenticatedException (testé en prod le 2026-10-06). Variable dédiée,
    # distincte de EUDR_OPERATOR_WS_IDENTIFIER (simple valeur de comparaison).
    operator_access_identifier=os.environ.get("EUDR_OPERATOR_ACCESS_IDENTIFIER"),
)
print(f"[EUDR] WS login={eudr_client.username} (from {'env' if EUDR_USERNAME_FROM_ENV else 'code fallback'}) "
      f"client_id={eudr_client.client_id} endpoint={eudr_client.service_url.split('?')[0]}", flush=True)

# Identifiants attendus de l'opérateur (fiche TRACES AGRIYIELDS ENTERPRISES UG SMC LTD)
EXPECTED_OPERATOR = {
    'name': os.environ.get("EUDR_OPERATOR_NAME", "AGRIYIELDS ENTERPRISES UG SMC LTD"),
    'identifiers': {
        'eori': os.environ.get("EUDR_OPERATOR_EORI", "HRUG000004679"),
        'tin':  os.environ.get("EUDR_OPERATOR_TIN", "1043535141"),
        'cbr':  os.environ.get("EUDR_OPERATOR_CBR", "8003457050645"),
    },
    'webservice_access_identifier': os.environ.get("EUDR_OPERATOR_WS_IDENTIFIER", "UGhPT7Jq"),
}


def _norm_id(value):
    return ''.join(ch for ch in str(value or '').upper() if ch.isalnum())


def _compare_operator(found):
    """Compare l'opérateur renvoyé par TRACES aux identifiants attendus."""
    if not found:
        return None
    found_values = {_norm_id(i.get('value')) for i in found.get('identifiers', [])}
    return {
        'name_matches': _norm_id(found.get('name')) == _norm_id(EXPECTED_OPERATOR['name']) if found.get('name') else None,
        'identifiers': {
            kind: (_norm_id(value) in found_values) if found_values else None
            for kind, value in EXPECTED_OPERATOR['identifiers'].items()
        },
    }


@api_eudr_bp.route('/identity-check', methods=['GET'])
@permission_required(DDS_PERMISSION)
def identity_check():
    """
    GET /api/eudr/identity-check[?dds_id=<uuid>]
    Montre le login WS réellement utilisé et, avec dds_id, l'opérateur auquel
    TRACES a rattaché cette DDS comparé aux identifiants AGRIYIELDS attendus.
    """
    user = load_current_user()
    if not user or not user.is_admin:
        return jsonify({"status": 403, "error": "Admin only."}), 403
    result = {
        'sent_in_envelope': {
            'ws_username': eudr_client.username,
            'ws_username_source': 'env (EUDR_USERNAME)' if EUDR_USERNAME_FROM_ENV else 'code fallback',
            'auth_key_source': 'env (EUDR_AUTH_KEY)' if os.environ.get("EUDR_AUTH_KEY") else 'code fallback',
            'web_service_client_id': eudr_client.client_id,
            'operator_access_identifier': eudr_client.operator_access_identifier,
            'endpoint': eudr_client.service_url.split('?')[0],
            'company_identifiers_sent': 'none when operatorRole=OPERATOR; EORI/VAT of the represented '
                                        'operator only when operatorRole=REPRESENTATIVE_OPERATOR',
        },
        'expected_operator': EXPECTED_OPERATOR,
    }
    dds_id = request.args.get('dds_id')
    if dds_id:
        response = eudr_client.get_by_dds_identifier(dds_id)
        fault = extract_soap_fault(response.text)
        if fault:
            result['traces_error'] = fault
        else:
            found = extract_operator_identity(response.text)
            result['operator_in_traces'] = found
            result['match'] = _compare_operator(found)
    return jsonify(result), 200

@api_eudr_bp.route('/config', methods=['GET'])
@permission_required(DDS_PERMISSION)
def submission_config():
    """Contraintes TRACES du compte, pour que le formulaire ne propose que des valeurs acceptées."""
    return jsonify({
        "operatorCountry": OPERATOR_COUNTRY,
        "operatorIsEU": OPERATOR_IS_EU,
        "operatorRoles": list(ALLOWED_OPERATOR_ROLES),
        "activityTypes": list(ALLOWED_ACTIVITY_TYPES),
        "countriesOfActivity": list(EU_COUNTRIES),
        "geometryTypes": list(GEOJSON_GEOMETRY_TYPES),
        "pointMaxAreaHa": 4,
        "pointMinAreaHa": 0.0001,
        "cattleHsPrefixes": list(CATTLE_HS_PREFIXES),
        "timberHsChapters": list(TIMBER_HS_CHAPTERS),
        "internalReferenceMaxLength": 50,
    })


@api_eudr_bp.route('/validate', methods=['POST'])
@permission_required(DDS_PERMISSION)
def validate_statement():
    """
    Vérifie un formulaire avec les mêmes règles que /submit, sans rien envoyer
    à TRACES. Body : {"geojson": {...}, "statement": {...}}.
    """
    data = request.get_json(silent=True) or {}
    statement = data.get("statement") or {}
    errors = []
    hs_error = _hs_code_error(dict(statement))
    if hs_error:
        errors.append(hs_error)
    try:
        hs_digits = ''.join(ch for ch in str(statement.get('hsHeading') or '') if ch.isdigit())
        errors += geojson_errors(data.get("geojson"), hs_digits)
        producer_xml = eudr_client._build_producer_xml(statement.get('producers', []), '', require_non_empty=True)
        eudr_client._build_statement_xml(statement, producer_xml)
    except ValueError as e:
        errors.append(str(e))
    return jsonify({"valid": not errors, "errors": errors}), 200


@api_eudr_bp.route('/submit', methods=['POST'])
@permission_required(DDS_PERMISSION)
def submit_statement():
    data = request.get_json(silent=True) or {}
    geojson = data.get("geojson")
    statement = data.get("statement")
    identity = get_jwt_identity()
    user_id = identity['id'] if identity else None

    if not statement:
        return jsonify({"status": 400, "error": "Missing 'statement' payload."}), 400

    hs_error = _hs_code_error(statement)
    if hs_error:
        return jsonify({"status": 400, "error": hs_error}), 400

    try:
        response = eudr_client.submit_statement(geojson, statement)
    except ValueError as e:
        return jsonify({"status": 400, "error": str(e)}), 400

    fault = extract_soap_fault(response.text)
    if fault:
        sent = _sent_summary(statement)
        # flush=True : sans ça gunicorn bufferise stdout et rien n'arrive dans journalctl
        print("🔥 SOAP Fault (submit) :", fault, "| sent:", sent, "| raw:", response.text[:2000], flush=True)
        return jsonify({
            "status": response.status_code,
            "error": fault.get("faultstring"),
            "detail": fault.get("detail"),
            "hint": fault.get("hint"),
            "sent": sent,
            "raw": response.text
        }), 502

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
                operator_street=statement.get('operator', {}).get('street'),              # ★ NOUVEAU
                operator_postal_code=statement.get('operator', {}).get('postalCode'),     # ★ NOUVEAU
                operator_city=statement.get('operator', {}).get('city'),                  # ★ NOUVEAU
                operator_email=statement.get('operator', {}).get('email'),
                operator_phone=statement.get('operator', {}).get('phone'),

                description_of_goods=statement.get('descriptionOfGoods'),
                hs_heading=statement.get('hsHeading'),
                scientific_name=statement.get('speciesInfo', {}).get('scientificName'),
                common_name=statement.get('speciesInfo', {}).get('commonName'),

                volume=_to_float((statement.get('goodsMeasure') or {}).get('volume')),
                net_weight=_to_float((statement.get('goodsMeasure') or {}).get('netWeight')),
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
            # La DDS EST déjà enregistrée côté TRACES : renvoyer une erreur ici poussait
            # l'utilisateur à resoumettre et créait des doublons. On renvoie l'uuid
            # avec un avertissement.
            print("⚠️ DDS soumise mais sauvegarde locale échouée :", dds_identifier, e)
            return jsonify({
                "status": response.status_code,
                "ddsIdentifier": dds_identifier,
                "warning": "DDS submitted to EUDR but could not be saved locally.",
                "details": str(e)
            }), 200

    if not dds_identifier:
        return jsonify({
            "status": response.status_code,
            "error": "EUDR did not return a DDS identifier.",
            "raw": response.text
        }), 502

    return jsonify({
        "status": response.status_code,
        "ddsIdentifier": dds_identifier,
    })


@api_eudr_bp.route('/amend', methods=['POST'])
@permission_required(DDS_PERMISSION)
def amend_statement():
    data = request.json
    geojson = data.get("geojson")
    dds_id = data.get("ddsIdentifier")
    statement = data.get("statement")
    identity = get_jwt_identity()
    user_id = identity['id'] if identity else None

    if not statement:
        return jsonify({"status": 400, "error": "Missing 'statement' payload."}), 400

    denied = _forbidden_dds(dds_id)
    if denied:
        return denied

    hs_error = _hs_code_error(statement)
    if hs_error:
        return jsonify({"status": 400, "error": hs_error}), 400

    try:
        response = eudr_client.amend_statement(geojson, dds_id, statement)
    except ValueError as e:
        return jsonify({"status": 400, "error": str(e)}), 400

    fault = extract_soap_fault(response.text)
    if fault:
        sent = _sent_summary(statement)
        # flush=True : sans ça gunicorn bufferise stdout et rien n'arrive dans journalctl
        print("🔥 SOAP Fault (amend) :", fault, "| sent:", sent, "| raw:", response.text[:2000], flush=True)
        return jsonify({
            "status": response.status_code,
            "error": fault.get("faultstring"),
            "detail": fault.get("detail"),
            "hint": fault.get("hint"),
            "sent": sent,
            "raw": response.text
        }), 502

    # Un HTTP 200 sans Fault = amendement accepté, même si la réponse ne
    # contient pas de <status> (auparavant considéré à tort comme un échec).
    status = extract_amend_status(response.text) or ("AMENDED" if response.status_code == 200 else None)

    if response.status_code == 200:
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
                record.operator_street = statement.get('operator', {}).get('street', record.operator_street)              # ★ NOUVEAU
                record.operator_postal_code = statement.get('operator', {}).get('postalCode', record.operator_postal_code)  # ★ NOUVEAU
                record.operator_city = statement.get('operator', {}).get('city', record.operator_city)                    # ★ NOUVEAU
                record.operator_email = statement.get('operator', {}).get('email', record.operator_email)
                record.operator_phone = statement.get('operator', {}).get('phone', record.operator_phone)

                record.description_of_goods = statement.get('descriptionOfGoods', record.description_of_goods)
                record.hs_heading = statement.get('hsHeading', record.hs_heading)
                record.scientific_name = statement.get('speciesInfo', {}).get('scientificName', record.scientific_name)
                record.common_name = statement.get('speciesInfo', {}).get('commonName', record.common_name)

                record.volume = _to_float((statement.get('goodsMeasure') or {}).get('volume', record.volume))
                record.net_weight = _to_float((statement.get('goodsMeasure') or {}).get('netWeight', record.net_weight))
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

    if response.status_code != 200:
        return jsonify({
            "status": response.status_code,
            "error": "EUDR rejected the amendment.",
            "raw": response.text
        }), 502

    return jsonify({
        "status": response.status_code,
        "ddsIdentifier": dds_id,
        "amendStatus": status,
    })

@api_eudr_bp.route('/retract/<dds_id>', methods=['DELETE'])
@permission_required(DDS_PERMISSION)
def retract_statement(dds_id):
    denied = _forbidden_dds(dds_id)
    if denied:
        return denied
    response = eudr_client.withdraw_statement(dds_id)
    fault = extract_soap_fault(response.text)
    if fault:
        # Ex. délai de retrait expiré ou DDS référencée : la DDS reste en base
        print("🔥 SOAP Fault (withdraw) :", fault, flush=True)
        return jsonify({
            "status": response.status_code,
            "error": fault.get("faultstring"),
            "detail": fault.get("detail"),
            "hint": fault.get("hint"),
        }), 502

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

    return jsonify({
        "status": response.status_code,
        "ddsStatus": extract_amend_status(response.text),
        "response": response.text,
    })


@api_eudr_bp.route('/info/by-internal-ref/<reference>', methods=['GET'])
@permission_required(DDS_PERMISSION)
def get_by_internal_reference(reference):
    from dateutil import parser
    import traceback

    user = load_current_user()
    if not user:
        return jsonify({"msg": "Account not found"}), 401
    user_id = user.id

    response = eudr_client.get_by_internal_reference(reference)

    fault = extract_soap_fault(response.text)
    if fault:
        print("🔥 SOAP Fault reçu :", fault, "| raw:", response.text[:2000])
        return jsonify({
            "status": response.status_code,
            "statements": [],
            "error": fault.get("faultstring"),
            "detail": fault.get("detail"),
            "hint": fault.get("hint"),
            "raw": response.text
        }), 502

    statements = extract_internal_ref_statements(response.text)
    if statements and not user.is_admin:
        # Le compte TRACES est partagé : un non-admin ne voit que ses propres DDS
        owned = {s.dds_identifier for s in _owned_query(user).all()}
        statements = [s for s in statements if s.get("identifier") in owned]
    if statements and not any(s.get("identifier") for s in statements):
        print("⚠️ Tous les champs sont vides — XML brut pour diagnostic :", response.text[:4000])

    if statements is not None:
        print("🧪 DEBUG - Statements reçus :", statements)
        try:
            for stmt_data in statements:
                # 🛑 Ignore les entrées invalides ou WITHDRAWN
                if not stmt_data.get("identifier") or stmt_data.get("status") == "WITHDRAWN":
                    continue

                print("📄 Traitement de l'entrée DDS :", stmt_data)

                identifier = stmt_data["identifier"]
                record = EUDRStatement.query.filter_by(dds_identifier=identifier).first()

                try:
                    raw_date = stmt_data.get("date")
                    status_date = parser.isoparse(raw_date) if raw_date else None
                except Exception as e:
                    print("❌ Erreur parsing date :", raw_date, str(e))
                    status_date = None

                if record:
                    record.status = stmt_data.get("status", record.status)
                    record.reference_number = stmt_data.get("referenceNumber") or record.reference_number
                    record.verification_code = stmt_data.get("verificationNumber") or record.verification_code
                    record.status_date = status_date
                    record.modified_by = user_id
                    record.updated_at = datetime.utcnow()
                elif user.is_admin:
                    new_stmt = EUDRStatement(
                        dds_identifier=identifier,
                        internal_reference_number=stmt_data.get("internalReferenceNumber"),
                        reference_number=stmt_data.get("referenceNumber") or None,
                        verification_code=stmt_data.get("verificationNumber") or None,
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
            print("🔥 Exception attrapée :", traceback.format_exc())
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
@permission_required(DDS_PERMISSION)
def get_by_dds_identifier(dds_id):
    user = load_current_user()
    if not user:
        return jsonify({"msg": "Account not found"}), 401
    user_id = user.id
    denied = _forbidden_dds(dds_id)
    if denied:
        return denied

    response = eudr_client.get_by_dds_identifier(dds_id)
    fault = extract_soap_fault(response.text)
    if fault:
        return jsonify({
            "status": response.status_code,
            "error": fault.get("faultstring"),
            "detail": fault.get("detail"),
            "hint": fault.get("hint"),
        }), 502
    info = extract_statement_info(response.text)

    if not info:
        return jsonify({
            "status": response.status_code,
            "error": "DDS not found in TRACES.",
            "raw": response.text
        }), 404

    try:
        stmt = EUDRStatement.query.filter_by(dds_identifier=dds_id).first()
        if stmt:
            # `or` : une valeur vide renvoyée par TRACES n'efface pas la base
            stmt.reference_number = info.get('referenceNumber') or stmt.reference_number
            stmt.verification_code = info.get('verificationCode') or stmt.verification_code
            stmt.status = info.get('status') or stmt.status

            date_str = info.get('date')
            if date_str:
                try:
                    stmt.status_date = parser.isoparse(date_str).replace(tzinfo=None)
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

    operator = extract_operator_identity(response.text)
    return jsonify({
        "status": response.status_code,
        **info,
        "operator": operator,
        "operator_match": _compare_operator(operator),
    })

@api_eudr_bp.route('/info/by-ref-verification', methods=['POST'])
def get_by_reference_and_verification():
    data = request.get_json(silent=True) or {}
    reference = data.get("reference")
    verification = data.get("verification")

    # Requête distante (SOAP)
    if not reference or not verification:
        return jsonify({"status": 400, "error": "'reference' and 'verification' are required."}), 400
    response = eudr_client.get_by_reference_and_verification(reference, verification)
    fault = extract_soap_fault(response.text)
    info = None if fault else extract_verification_info(response.text)

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
            "operator_street": local_record.operator_street,               # ★ NOUVEAU
            "operator_postal_code": local_record.operator_postal_code,     # ★ NOUVEAU
            "operator_city": local_record.operator_city,                  # ★ NOUVEAU
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
            "error": fault.get("faultstring") if fault else "Unable to parse XML",
            "detail": fault.get("detail") if fault else None,
            "hint": fault.get("hint") if fault else None,
            "raw": response.text,
            "local_data": local_data
        })



@api_eudr_bp.route('/', methods=['GET'])
@permission_required(DDS_PERMISSION)
def list_statements():
    user = load_current_user()
    if not user:
        return jsonify({"msg": "Account not found"}), 401
    statements = _owned_query(user).all()
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