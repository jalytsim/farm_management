
import json
import requests
import os
import base64
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

class EUDRClient:
    def __init__(self, username, auth_key, client_id='eudr-repository'):
        self.username = username
        self.auth_key = auth_key
        self.client_id = client_id
        self.submission_url = 'https://eudr.webcloud.ec.europa.eu/tracesnt/ws/EUDRSubmissionServiceV1?wsdl'
        self.retrieval_url = 'https://eudr.webcloud.ec.europa.eu/tracesnt/ws/EUDRRetrievalServiceV1?wsdl'
        # self.submission_url = 'https://acceptance.eudr.webcloud.ec.europa.eu/tracesnt/ws/EUDRSubmissionServiceV1?wsdl'
        # self.retrieval_url = 'https://acceptance.eudr.webcloud.ec.europa.eu/tracesnt/ws/EUDRRetrievalServiceV1?wsdl'

    def _generate_security(self):
        nonce_bytes = os.urandom(16)
        nonce_b64 = base64.b64encode(nonce_bytes).decode('utf-8')
        created_dt = datetime.now(timezone.utc)
        created = created_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        expires = (created_dt + timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        password_digest = base64.b64encode(
            hashlib.sha1(nonce_bytes + created.encode('utf-8') + self.auth_key.encode('utf-8')).digest()
        ).decode('utf-8')
        token_id = f"UsernameToken-{uuid.uuid4().hex.upper()}"
        timestamp_id = f"TS-{uuid.uuid4().hex.upper()}"

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

    def _post(self, body: str, is_submission=True):
        url = self.submission_url if is_submission else self.retrieval_url
        envelope = f"""<soapenv:Envelope 
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:v4="http://ec.europa.eu/sanco/tracesnt/base/v4"
            xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
            xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
            xmlns:v1="http://ec.europa.eu/tracesnt/certificate/eudr/{'submission' if is_submission else 'retrieval'}/v1"
            xmlns:v11="http://ec.europa.eu/tracesnt/certificate/eudr/model/v1">
            <soapenv:Header>{self._generate_security()}</soapenv:Header>
            <soapenv:Body>{body}</soapenv:Body>
        </soapenv:Envelope>"""
        return requests.post(url, data=envelope, headers={"Content-Type": "text/xml"}, verify=True)

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

        producers = statement_data.get('producers', [])
        print("🔍 PRODUCERS RECEIVED:", producers)
        producer_xml = ""
        if producers and isinstance(producers, list):
            for prod in producers:
                country = prod.get('country')
                name = prod.get('name')

                if not country or not name or name.strip() == "":
                    continue  # Ignore les producteurs incomplets ou vides

                block = f"""
                    <v11:producers>
                        <v11:country>{country}</v11:country>
                        <v11:name>{name}</v11:name>
                        <v11:geometryGeojson>{geojson_b64}</v11:geometryGeojson>
                    </v11:producers>"""
                producer_xml += block
                print("✅ Adding producer block:", block)
        else:
            print("⚠️ No valid producers provided or producers field is missing.")

        body = f"""<v1:SubmitStatementRequest>
            <v1:operatorType>{statement_data.get('operatorType', 'OPERATOR')}</v1:operatorType>
            <v1:statement>
                <v11:internalReferenceNumber>{statement_data['internalReferenceNumber']}</v11:internalReferenceNumber>
                <v11:activityType>{statement_data['activityType']}</v11:activityType>
                <v11:borderCrossCountry>{statement_data['borderCrossCountry']}</v11:borderCrossCountry>
                <v11:comment>{statement_data.get('comment', '')}</v11:comment>
                <v11:commodities>
                    <v11:descriptors>
                        <v11:descriptionOfGoods>{statement_data['descriptionOfGoods']}</v11:descriptionOfGoods>
                        <v11:goodsMeasure>
                            <v11:volume>{statement_data['goodsMeasure']['volume']}</v11:volume>
                            <v11:netWeight>{statement_data['goodsMeasure']['netWeight']}</v11:netWeight>
                            <v11:supplementaryUnit>{statement_data['goodsMeasure']['supplementaryUnit']}</v11:supplementaryUnit>
                            <v11:supplementaryUnitQualifier>{statement_data['goodsMeasure']['supplementaryUnitQualifier']}</v11:supplementaryUnitQualifier>
                        </v11:goodsMeasure>
                    </v11:descriptors>
                    <v11:hsHeading>{statement_data['hsHeading']}</v11:hsHeading>
                    <v11:speciesInfo>
                        <v11:scientificName>{statement_data['speciesInfo']['scientificName']}</v11:scientificName>
                        <v11:commonName>{statement_data['speciesInfo']['commonName']}</v11:commonName>
                    </v11:speciesInfo>
                    {producer_xml}
                </v11:commodities>
                <v11:geoLocationConfidential>{str(statement_data.get('geoLocationConfidential', False)).lower()}</v11:geoLocationConfidential>
            </v1:statement>
        </v1:SubmitStatementRequest>"""

        print("📤 FINAL SOAP BODY TO SUBMIT:")
        print(body)
        print("📤 END OF BODY")

        return self._post(body, is_submission=True)


    def amend_statement(self, geojson_data: dict, ddsIdentifier: str, statement_data: dict):
        geojson_b64 = base64.b64encode(json.dumps(geojson_data).encode('utf-8')).decode('utf-8')

        producers = statement_data.get('producers', [])
        producer_xml = ""
        if producers and isinstance(producers, list):
            for prod in producers:
                country = prod.get('country', '')
                name = prod.get('name', '')
                producer_xml += f"""
                    <v11:producers>
                        <v11:country>{country}</v11:country>
                        <v11:name>{name}</v11:name>
                        <v11:geometryGeojson>{geojson_b64}</v11:geometryGeojson>
                    </v11:producers>"""
        else:
            raise ValueError("'producers' must be a non-empty list of dictionaries.")

        body = f"""<v1:AmendStatementRequest>
            <v1:ddsIdentifier>{ddsIdentifier}</v1:ddsIdentifier>
            <v1:statement>
                <v11:internalReferenceNumber>{statement_data['internalReferenceNumber']}</v11:internalReferenceNumber>
                <v11:activityType>{statement_data['activityType']}</v11:activityType>
                <v11:operator>
                    <v11:referenceNumber>
                        <v11:identifierType>{statement_data['operator']['identifierType']}</v11:identifierType>
                        <v11:identifierValue>{statement_data['operator']['identifierValue']}</v11:identifierValue>
                    </v11:referenceNumber>
                    <v11:nameAndAddress>
                        <v4:name>{statement_data['operator']['name']}</v4:name>
                        <v4:country>{statement_data['operator']['country']}</v4:country>
                        <v4:address>{statement_data['operator']['address']}</v4:address>
                    </v11:nameAndAddress>
                    <v11:email>{statement_data['operator']['email']}</v11:email>
                    <v11:phone>{statement_data['operator']['phone']}</v11:phone>
                </v11:operator>
                <v11:countryOfActivity>{statement_data['countryOfActivity']}</v11:countryOfActivity>
                <v11:borderCrossCountry>{statement_data['borderCrossCountry']}</v11:borderCrossCountry>
                <v11:comment>{statement_data['comment']}</v11:comment>
                <v11:commodities>
                    <v11:descriptors>
                        <v11:descriptionOfGoods>{statement_data['descriptionOfGoods']}</v11:descriptionOfGoods>
                        <v11:goodsMeasure>
                            <v11:netWeight>{statement_data['goodsMeasure']['netWeight']}</v11:netWeight>
                            <v11:supplementaryUnit>{statement_data['goodsMeasure']['supplementaryUnit']}</v11:supplementaryUnit>
                            <v11:supplementaryUnitQualifier>{statement_data['goodsMeasure']['supplementaryUnitQualifier']}</v11:supplementaryUnitQualifier>
                        </v11:goodsMeasure>
                    </v11:descriptors>
                    <v11:hsHeading>{statement_data['hsHeading']}</v11:hsHeading>
                    <v11:speciesInfo>
                        <v11:scientificName>{statement_data['speciesInfo']['scientificName']}</v11:scientificName>
                        <v11:commonName>{statement_data['speciesInfo']['commonName']}</v11:commonName>
                    </v11:speciesInfo>
                    {producer_xml}
                </v11:commodities>
                <v11:geoLocationConfidential>{str(statement_data.get('geoLocationConfidential', False)).lower()}</v11:geoLocationConfidential>
            </v1:statement>
        </v1:AmendStatementRequest>"""
        return self._post(body, is_submission=True)

    def retract_statement(self, ddsIdentifier: str):
        body = f"<v1:RetractStatementRequest><v1:ddsIdentifier>{ddsIdentifier}</v1:ddsIdentifier></v1:RetractStatementRequest>"
        return self._post(body, is_submission=True)

    def get_by_internal_reference(self, reference_number: str):
        body = f"<v1:GetDdsInfoByInternalReferenceNumberRequest>{reference_number}</v1:GetDdsInfoByInternalReferenceNumberRequest>"
        return self._post(body, is_submission=False)

    def get_by_dds_identifier(self, ddsIdentifier: str):
        body = f"<v1:GetStatementInfoRequest><v1:identifier>{ddsIdentifier}</v1:identifier></v1:GetStatementInfoRequest>"
        return self._post(body, is_submission=False)

    def get_by_reference_and_verification(self, reference: str, verification: str):
        body = f"""
        <v1:GetStatementByIdentifiersRequest>
            <v1:referenceNumber>{reference}</v1:referenceNumber>
            <v1:verificationNumber>{verification}</v1:verificationNumber>
        </v1:GetStatementByIdentifiersRequest>
        """
        response = self._post(body, is_submission=False)

        # 🔽 Print de la réponse XML
        print("\n🔽🔽🔽 [RESPONSE XML] 🔽🔽🔽\n")
        print(response.text)
        print("\n🔼🔼🔼 [END RESPONSE XML] 🔼🔼🔼\n")

        return response

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
            'verificationCode': root.findtext('.//ns5:verificationCode', default='', namespaces=ns),  # <-- modif
            'status': root.findtext('.//ns5:status', default='', namespaces=ns),
            'date': root.findtext('.//ns5:date', default='', namespaces=ns),
            'updatedBy': root.findtext('.//ns5:updatedBy', default='', namespaces=ns)
        }
        return info
    except ET.ParseError:
        return None


def extract_verification_info(xml_text):
    print("HOLAAA",xml_text)
    try:
        root = ET.fromstring(xml_text)
        ns = {
            'S': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns5': 'http://ec.europa.eu/tracesnt/certificate/eudr/retrieval/v1',
            'ns3': 'http://ec.europa.eu/tracesnt/certificate/eudr/model/v1',
        }

        statement = root.find('.//ns5:statement', ns)
        if statement is None:
            return {'error': 'Statement not found in XML'}

        info = {
            'referenceNumber': statement.findtext('ns5:referenceNumber', default='', namespaces=ns),
            'activityType': statement.findtext('ns5:activityType', default='', namespaces=ns),
            'status': statement.findtext('.//ns3:status', default='', namespaces=ns),
            'statusDate': statement.findtext('.//ns3:date', default='', namespaces=ns),
            'operator': {
                'name': statement.findtext('.//ns3:name', default='', namespaces=ns),
                'country': statement.findtext('.//ns3:country', default='', namespaces=ns)
            },
            'commodities': []
        }

        # 🔍 Boucle sur tous les <commodities>
        for commodity in statement.findall('.//ns5:commodities', ns):
            descriptors = commodity.find('.//ns3:descriptors', ns)
            species_info = commodity.find('.//ns3:speciesInfo', ns)
            hs_heading = commodity.findtext('ns3:hsHeading', default='', namespaces=ns)

            commodity_info = {
                'descriptionOfGoods': descriptors.findtext('ns3:descriptionOfGoods', default='', namespaces=ns) if descriptors is not None else '',
                'goodsMeasure': {
                    'volume': descriptors.findtext('.//ns3:volume', default='', namespaces=ns) if descriptors is not None else '',
                    'netWeight': descriptors.findtext('.//ns3:netWeight', default='', namespaces=ns) if descriptors is not None else '',
                    'supplementaryUnit': descriptors.findtext('.//ns3:supplementaryUnit', default='', namespaces=ns) if descriptors is not None else '',
                    'supplementaryUnitQualifier': descriptors.findtext('.//ns3:supplementaryUnitQualifier', default='', namespaces=ns) if descriptors is not None else ''
                },
                'speciesInfo': {
                    'scientificName': species_info.findtext('ns3:scientificName', default='', namespaces=ns) if species_info is not None else '',
                    'commonName': species_info.findtext('ns3:commonName', default='', namespaces=ns) if species_info is not None else ''
                },
                'hsHeading': hs_heading,
                'producers': []
            }

            # 🔄 Extraire les producteurs de ce commodity
            for producer in commodity.findall('.//ns3:producers', ns):
                country = producer.findtext('ns3:country', default='', namespaces=ns)
                geo_b64 = producer.findtext('ns3:geometryGeojson', default='', namespaces=ns)

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
