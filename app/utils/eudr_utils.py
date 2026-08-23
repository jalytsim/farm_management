import json
import requests
import os
import base64
import hashlib
import uuid as uuid_lib
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

# Namespaces V3
NS_V3 = "http://ec.europa.eu/tracesnt/certificate/eudr/due-diligence-statement/v3"
# CONFIRMÉ (doc officielle EUDR, section "Common Types" vs "Types"):
# Un élément prend le namespace de la section où SON TYPE PARENT est défini,
# pas celui de son propre type. En v3c (common): descriptionOfGoods, goodsMeasure
# (et ses enfants netWeight/supplementaryUnit/supplementaryUnitQualifier),
# operatorReferenceNumber/operatorName/operatorAddress (et ses enfants)/operatorEmail/
# operatorPhone (car EconomicOperatorIdentificationType et AddressType sont des
# "Common Types"), et groupedDeclaration. Tout le reste (producers y compris
# son country, speciesInfo, hsHeading, commodities, geoLocationConfidential, etc.)
# reste en v3, car ce sont des enfants de types "Types" (DdsProducerType,
# SpeciesInformationType, DdsCommodityType, DueDiligenceStatementBaseType).
# ⚠️ 'volume' n'existe PAS dans GoodsMeasureType en V3 (supprimé depuis V2) —
# ne pas l'envoyer, le serveur le rejette.
NS_COMMON = "http://ec.europa.eu/tracesnt/certificate/eudr/common/v3"


class EUDRClient:
    def __init__(self, username, auth_key, client_id='eudr-repository'):
        self.username = username
        self.auth_key = auth_key
        self.client_id = client_id
        # V3 unifie submission + retrieval en un seul service
        self.service_url = 'https://eudr.webcloud.ec.europa.eu/tracesnt/ws/EUDRDueDiligenceStatementServiceV3?wsdl'
        # self.service_url = 'https://acceptance.eudr.webcloud.ec.europa.eu/tracesnt/ws/EUDRDueDiligenceStatementServiceV3?wsdl'

    def _generate_security(self):
        nonce_bytes = os.urandom(16)
        nonce_b64 = base64.b64encode(nonce_bytes).decode('utf-8')
        created_dt = datetime.now(timezone.utc)
        created = created_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        expires = (created_dt + timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        password_digest = base64.b64encode(
            hashlib.sha1(nonce_bytes + created.encode('utf-8') + self.auth_key.encode('utf-8')).digest()
        ).decode('utf-8')
        token_id = f"UsernameToken-{uuid_lib.uuid4().hex.upper()}"
        timestamp_id = f"TS-{uuid_lib.uuid4().hex.upper()}"

        # WS-Security n'est pas impacté par la migration V2->V3 d'après la doc
        header = f"""<wsse:Security>
            <wsu:Timestamp wsu:Id="{timestamp_id}">
                <wsu:Created>{created}</wsu:Created>
                <wsu:Expires>{expires}</wsu:Expires>
            </wsu:Timestamp>
            <wsse:UsernameToken wsu:Id="{token_id}">
                <wsse:Username>{self.username}</wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">{password_digest}</wsse:Password>
                <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">{nonce_b64}</wsse:Nonce>
                <wsu:Created>{created}</wsu:Created>
            </wsse:UsernameToken>
        </wsse:Security>
        <v4:WebServiceClientId>{self.client_id}</v4:WebServiceClientId>"""
        return header

    def _post(self, body: str):
        envelope = f"""<soapenv:Envelope
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:v4="http://ec.europa.eu/sanco/tracesnt/base/v4"
            xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
            xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
            xmlns:v3="{NS_V3}"
            xmlns:v3c="{NS_COMMON}">
            <soapenv:Header>{self._generate_security()}</soapenv:Header>
            <soapenv:Body>{body}</soapenv:Body>
        </soapenv:Envelope>"""
        return requests.post(self.service_url, data=envelope, headers={"Content-Type": "text/xml"}, verify=True)

    # ------------------------------------------------------------------
    # Bloc opérateur : construit soit <representedOperator> (si représentant),
    # soit rien si operatorRole == OPERATOR (dans ce cas l'opérateur est
    # déduit du compte authentifié, comme en V2/V1 déjà normalement).
    # ------------------------------------------------------------------
    def _build_operator_block(self, operator_data: dict) -> str:
        if not operator_data:
            return ""
        return f"""
            <v3:representedOperator>
                <v3c:operatorReferenceNumber>
                    <v3c:identifierType>{operator_data.get('identifierType', '')}</v3c:identifierType>
                    <v3c:identifierValue>{operator_data.get('identifierValue', '')}</v3c:identifierValue>
                </v3c:operatorReferenceNumber>
                <v3c:operatorName>{operator_data.get('name', '')}</v3c:operatorName>
                <v3c:operatorAddress>
                    <v3c:country>{operator_data.get('country', '')}</v3c:country>
                    <v3c:street>{operator_data.get('street', '')}</v3c:street>
                    <v3c:postalCode>{operator_data.get('postalCode', '')}</v3c:postalCode>
                    <v3c:city>{operator_data.get('city', '')}</v3c:city>
                    <v3c:fullAddress>{operator_data.get('address', operator_data.get('fullAddress', ''))}</v3c:fullAddress>
                </v3c:operatorAddress>
                <v3c:operatorEmail>{operator_data.get('email', '')}</v3c:operatorEmail>
                <v3c:operatorPhone>{operator_data.get('phone', '')}</v3c:operatorPhone>
            </v3:representedOperator>"""

    def _build_producer_xml(self, producers, geojson_b64, require_non_empty=False):
        producer_xml = ""
        if producers and isinstance(producers, list):
            for prod in producers:
                country = prod.get('country')
                name = prod.get('name')
                position = prod.get('position', '')
                if not country or not name or name.strip() == "":
                    continue
                producer_xml += f"""
                    <v3:producers>
                        <v3:position>{position}</v3:position>
                        <v3:country>{country}</v3:country>
                        <v3:name>{name}</v3:name>
                        <v3:geometryGeojson>{geojson_b64}</v3:geometryGeojson>
                    </v3:producers>"""
        elif require_non_empty:
            raise ValueError("'producers' must be a non-empty list of dictionaries.")
        return producer_xml

    def _build_statement_xml(self, statement_data: dict, producer_xml: str) -> str:
        # operatorRole: OPERATOR / REPRESENTATIVE_OPERATOR uniquement (TRADER supprimé en V3)
        operator_role = statement_data.get('operatorRole', statement_data.get('operatorType', 'OPERATOR'))
        if operator_role in ('TRADER', 'REPRESENTATIVE_TRADER'):
            raise ValueError(f"operatorRole '{operator_role}' n'existe plus en V3 (traders exclus de la soumission DDS).")

        activity_type = statement_data['activityType']
        if activity_type == 'TRADE':
            raise ValueError("activityType 'TRADE' n'existe plus en V3.")

        operator_block = ""
        if operator_role == 'REPRESENTATIVE_OPERATOR':
            operator_block = self._build_operator_block(statement_data.get('operator', {}))

        internal_ref = statement_data['internalReferenceNumber']
        if len(internal_ref) > 35:
            raise ValueError("internalReferenceNumber dépasse la longueur max de 35 caractères en V3 (était 50 en V2).")

        return f"""
            <v3:internalReferenceNumber>{internal_ref}</v3:internalReferenceNumber>
            <v3:activityType>{activity_type}</v3:activityType>
            {operator_block}
            <v3:countryOfActivity>{statement_data['countryOfActivity']}</v3:countryOfActivity>
            <v3:borderCrossCountry>{statement_data.get('borderCrossCountry', '')}</v3:borderCrossCountry>
            <v3:comment>{statement_data.get('comment', '')}</v3:comment>
            <v3:commodities>
                <v3:position>1</v3:position>
                <v3:descriptors>
                    <v3c:descriptionOfGoods>{statement_data['descriptionOfGoods']}</v3c:descriptionOfGoods>
                    <v3c:goodsMeasure>
                        <v3c:netWeight>{statement_data['goodsMeasure'].get('netWeight', '')}</v3c:netWeight>
                        <v3c:supplementaryUnit>{statement_data['goodsMeasure'].get('supplementaryUnit', '')}</v3c:supplementaryUnit>
                        <v3c:supplementaryUnitQualifier>{statement_data['goodsMeasure'].get('supplementaryUnitQualifier', '')}</v3c:supplementaryUnitQualifier>
                    </v3c:goodsMeasure>
                </v3:descriptors>
                <v3:hsHeading>{statement_data['hsHeading']}</v3:hsHeading>
                <v3:speciesInfo>
                    <v3:scientificName>{statement_data['speciesInfo'].get('scientificName', '')}</v3:scientificName>
                    <v3:commonName>{statement_data['speciesInfo'].get('commonName', '')}</v3:commonName>
                </v3:speciesInfo>
                {producer_xml}
            </v3:commodities>
            <v3:geoLocationConfidential>{str(statement_data.get('geoLocationConfidential', False)).lower()}</v3:geoLocationConfidential>"""
        # TODO VÉRIFIER: groupedDeclarations (ex-associatedStatements) non géré ici
        # faute de payload d'exemple côté app. À ajouter si utilisé:
        # <v3:groupedDeclarations><v3:groupedDeclaration>REF</v3:groupedDeclaration>...</v3:groupedDeclarations>

    # ------------------------------------------------------------------
    # SUBMIT
    # ------------------------------------------------------------------
    def submit_statement(self, geojson_data: dict, statement_data: dict):
        def validate_geojson(gj):
            if not isinstance(gj, dict):
                return False
            if gj.get("type") != "FeatureCollection":
                return False
            features = gj.get("features", [])
            if not isinstance(features, list) or len(features) == 0:
                return False
            for f in features:
                if "geometry" not in f or "type" not in f["geometry"] or "coordinates" not in f["geometry"]:
                    return False
            return True

        if not validate_geojson(geojson_data):
            raise ValueError("Invalid GeoJSON provided.")

        geojson_b64 = base64.b64encode(json.dumps(geojson_data).encode('utf-8')).decode('utf-8')
        producer_xml = self._build_producer_xml(statement_data.get('producers', []), geojson_b64)
        operator_role = statement_data.get('operatorRole', statement_data.get('operatorType', 'OPERATOR'))
        statement_xml = self._build_statement_xml(statement_data, producer_xml)

        body = f"""<v3:SubmitDdsRequest>
            <v3:operatorRole>{operator_role}</v3:operatorRole>
            <v3:statement>{statement_xml}
            </v3:statement>
        </v3:SubmitDdsRequest>"""

        return self._post(body)

    # ------------------------------------------------------------------
    # AMEND
    # ------------------------------------------------------------------
    def amend_statement(self, geojson_data: dict, uuid: str, statement_data: dict):
        geojson_b64 = base64.b64encode(json.dumps(geojson_data).encode('utf-8')).decode('utf-8')
        producer_xml = self._build_producer_xml(statement_data.get('producers', []), geojson_b64, require_non_empty=True)
        statement_xml = self._build_statement_xml(statement_data, producer_xml)

        body = f"""<v3:AmendDdsRequest>
            <v3:uuid>{uuid}</v3:uuid>
            <v3:statement>{statement_xml}
            </v3:statement>
        </v3:AmendDdsRequest>"""
        return self._post(body)

    # ------------------------------------------------------------------
    # WITHDRAW (ex-retract)
    # ------------------------------------------------------------------
    def withdraw_statement(self, uuid: str):
        body = f"<v3:WithdrawDdsRequest><v3:uuid>{uuid}</v3:uuid></v3:WithdrawDdsRequest>"
        return self._post(body)

    # Alias de compat pour ne pas casser le reste du code d'un coup
    def retract_statement(self, uuid: str):
        return self.withdraw_statement(uuid)

    # ------------------------------------------------------------------
    # RETRIEVAL
    # ------------------------------------------------------------------
    def get_by_internal_reference(self, reference_number: str):
        # ✅ CONFIRMÉ doc officielle: GetDdsByInternalReferenceRequestType.internalReference
        # (et non internalReferenceNumber)
        body = f"<v3:GetDdsByInternalReferenceRequest><v3:internalReference>{reference_number}</v3:internalReference></v3:GetDdsByInternalReferenceRequest>"
        return self._post(body)

    def get_by_dds_identifier(self, uuid_list):
        # ✅ CONFIRMÉ doc officielle: GetDdsRequestType.uuidList (répétable, jusqu'à 100 uuid)
        if isinstance(uuid_list, str):
            uuid_list = [uuid_list]
        uuid_xml = "".join(f"<v3:uuidList>{u}</v3:uuidList>" for u in uuid_list)
        body = f"<v3:GetDdsRequest>{uuid_xml}</v3:GetDdsRequest>"
        return self._post(body)

    def get_by_reference_and_verification(self, reference: str, verification: str):
        # ✅ CONFIRMÉ doc officielle: GetDdsByIdentifiersRequestType.referenceAndVerificationNumber
        # (ReferenceAndVerificationNumberType), et non les deux champs à plat
        body = f"""
        <v3:GetDdsByIdentifiersRequest>
            <v3:referenceAndVerificationNumber>
                <v3:referenceNumber>{reference}</v3:referenceNumber>
                <v3:verificationNumber>{verification}</v3:verificationNumber>
            </v3:referenceAndVerificationNumber>
        </v3:GetDdsByIdentifiersRequest>
        """
        response = self._post(body)
        print("\n🔽🔽🔽 [RESPONSE XML] 🔽🔽🔽\n")
        print(response.text)
        print("\n🔼🔼🔼 [END RESPONSE XML] 🔼🔼🔼\n")
        return response


# ==========================================================================
# EXTRACTEURS — namespace unique v3 pour tout (submit/amend/withdraw/retrieval)
# ==========================================================================

def extract_dds_identifier(xml_text):
    """V2 'ddsIdentifier' -> V3 'uuid'"""
    try:
        root = ET.fromstring(xml_text)
        ns = {'S': 'http://schemas.xmlsoap.org/soap/envelope/', 'v3': NS_V3}
        el = root.find('.//v3:uuid', ns)
        return el.text if el is not None else None
    except ET.ParseError:
        return None


def extract_amend_status(xml_text):
    """
    V3: AmendDdsResponse / WithdrawDdsResponse renvoient uuid + status
    (statut de cycle de vie, ex: AVAILABLE / WITHDRAWN), plus rejectionReason
    et communicationToOperator en cas de rejet (nouveautés V3).
    """
    try:
        root = ET.fromstring(xml_text)
        ns = {'S': 'http://schemas.xmlsoap.org/soap/envelope/', 'v3': NS_V3}
        status_el = root.find('.//v3:status', ns)
        return status_el.text if status_el is not None else None
    except ET.ParseError:
        return None


def extract_amend_response(xml_text):
    """Nouvelle fonction: extrait uuid + status + rejectionReason + communicationToOperator."""
    try:
        root = ET.fromstring(xml_text)
        ns = {'S': 'http://schemas.xmlsoap.org/soap/envelope/', 'v3': NS_V3}
        return {
            'uuid': root.findtext('.//v3:uuid', default='', namespaces=ns),
            'status': root.findtext('.//v3:status', default='', namespaces=ns),
            'rejectionReason': root.findtext('.//v3:rejectionReason', default='', namespaces=ns),
            'communicationToOperator': root.findtext('.//v3:communicationToOperator', default='', namespaces=ns),
        }
    except ET.ParseError:
        return None


def extract_statement_info(xml_text):
    try:
        root = ET.fromstring(xml_text)
        ns = {'S': 'http://schemas.xmlsoap.org/soap/envelope/', 'v3': NS_V3}
        info = {
            'identifier': root.findtext('.//v3:uuid', default='', namespaces=ns),
            'internalReferenceNumber': root.findtext('.//v3:internalReferenceNumber', default='', namespaces=ns),
            'referenceNumber': root.findtext('.//v3:referenceNumber', default='', namespaces=ns),
            'verificationCode': root.findtext('.//v3:verificationNumber', default='', namespaces=ns),
            'status': root.findtext('.//v3:status', default='', namespaces=ns),
            'date': root.findtext('.//v3:date', default='', namespaces=ns),
            'updatedBy': root.findtext('.//v3:updatedBy', default='', namespaces=ns)
        }
        return info
    except ET.ParseError:
        return None


def extract_verification_info(xml_text):
    try:
        root = ET.fromstring(xml_text)
        ns = {
            'S': 'http://schemas.xmlsoap.org/soap/envelope/',
            'v3': NS_V3,
            'v3c': NS_COMMON,
        }
        statement = root.find('.//v3:statement', ns)
        if statement is None:
            return {'error': 'Statement not found in XML'}

        info = {
            'referenceNumber': statement.findtext('v3:referenceNumber', default='', namespaces=ns),
            'activityType': statement.findtext('v3:activityType', default='', namespaces=ns),
            'status': statement.findtext('.//v3c:status', default='', namespaces=ns),
            'statusDate': statement.findtext('.//v3c:date', default='', namespaces=ns),
            'operator': {
                'name': statement.findtext('.//v3:operatorName', default='', namespaces=ns),
                'country': statement.findtext('.//v3c:country', default='', namespaces=ns)
            },
            'commodities': []
        }

        for commodity in statement.findall('.//v3:commodities', ns):
            descriptors = commodity.find('.//v3:descriptors', ns)
            species_info = commodity.find('.//v3:speciesInfo', ns)
            hs_heading = commodity.findtext('v3:hsHeading', default='', namespaces=ns)

            commodity_info = {
                'descriptionOfGoods': descriptors.findtext('v3:descriptionOfGoods', default='', namespaces=ns) if descriptors is not None else '',
                'goodsMeasure': {
                    'volume': descriptors.findtext('.//v3:volume', default='', namespaces=ns) if descriptors is not None else '',
                    'netWeight': descriptors.findtext('.//v3:netWeight', default='', namespaces=ns) if descriptors is not None else '',
                    'supplementaryUnit': descriptors.findtext('.//v3:supplementaryUnit', default='', namespaces=ns) if descriptors is not None else '',
                    'supplementaryUnitQualifier': descriptors.findtext('.//v3:supplementaryUnitQualifier', default='', namespaces=ns) if descriptors is not None else ''
                },
                'speciesInfo': {
                    'scientificName': species_info.findtext('v3:scientificName', default='', namespaces=ns) if species_info is not None else '',
                    'commonName': species_info.findtext('v3:commonName', default='', namespaces=ns) if species_info is not None else ''
                },
                'hsHeading': hs_heading,
                'producers': []
            }

            for producer in commodity.findall('.//v3:producers', ns):
                country = producer.findtext('v3c:country', default='', namespaces=ns)
                geo_b64 = producer.findtext('v3:geometryGeojson', default='', namespaces=ns)
                decoded_geometry = {}
                if geo_b64:
                    try:
                        decoded_json = base64.b64decode(geo_b64).decode('utf-8')
                        decoded_geometry = json.loads(decoded_json)
                    except Exception as e:
                        decoded_geometry = {'error': str(e)}
                commodity_info['producers'].append({
                    'country': country,
                    'geometryGeojson': geo_b64,
                    'decodedGeometry': decoded_geometry
                })

            info['commodities'].append(commodity_info)

        return info
    except ET.ParseError as e:
        return {'error': 'XML Parse Error', 'details': str(e)}


def extract_internal_ref_statements(xml_text):
    """
    ✅ CONFIRMÉ doc officielle: getDdsByInternalReference et getDds renvoient tous deux
    un DdsOverviewResponseType, dont le champ répété est 'ddsOverviewList' (type OverviewType),
    et non 'statementInfo' (qui n'existe pas dans le schéma V3).
    Champs de OverviewType: uuid, internalReferenceNumber, referenceNumber, verificationNumber,
    status, rejectionReason, communicationToOperator, date, updatedBy, version.
    """
    try:
        root = ET.fromstring(xml_text)
        ns = {'S': 'http://schemas.xmlsoap.org/soap/envelope/', 'v3': NS_V3}
        statements = []
        for info in root.findall('.//v3:ddsOverviewList', ns):
            statements.append({
                'identifier': info.findtext('v3:uuid', default='', namespaces=ns),
                'internalReferenceNumber': info.findtext('v3:internalReferenceNumber', default='', namespaces=ns),
                'referenceNumber': info.findtext('v3:referenceNumber', default='', namespaces=ns),
                'verificationNumber': info.findtext('v3:verificationNumber', default='', namespaces=ns),
                'status': info.findtext('v3:status', default='', namespaces=ns),
                'rejectionReason': info.findtext('v3:rejectionReason', default='', namespaces=ns),
                'date': info.findtext('v3:date', default='', namespaces=ns),
                'updatedBy': info.findtext('v3:updatedBy', default='', namespaces=ns)
            })
        return statements
    except ET.ParseError:
        return None


def extract_soap_fault(xml_text):
    """
    Détecte un SOAP Fault (erreur de validation, auth, etc.) dans la réponse brute.
    Un Fault est du XML valide donc invisible aux extracteurs ci-dessus: sans cette
    fonction, une erreur serveur se traduit silencieusement par une liste vide.
    """
    try:
        root = ET.fromstring(xml_text)
        ns = {'S': 'http://schemas.xmlsoap.org/soap/envelope/'}
        fault = root.find('.//S:Fault', ns)
        if fault is None:
            fault = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Fault')
        if fault is not None:
            faultstring = fault.findtext('faultstring')
            if faultstring is None:
                faultstring = fault.findtext('.//{http://schemas.xmlsoap.org/soap/envelope/}Reason//{http://schemas.xmlsoap.org/soap/envelope/}Text')
            detail = fault.findtext('.//detail')
            return {
                'faultstring': faultstring or 'Unknown SOAP fault',
                'detail': detail or ''
            }
        return None
    except ET.ParseError:
        return None