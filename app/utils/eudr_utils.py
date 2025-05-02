
import json
import requests
import os
import base64
import hashlib
import uuid
from datetime import datetime, timedelta, timezone

class EUDRClient:
    def __init__(self, username, auth_key, client_id='eudr-test'):
        self.username = username
        self.auth_key = auth_key
        self.client_id = client_id
        self.submission_url = 'https://eudr.webcloud.ec.europa.eu/tracesnt/ws/EUDRSubmissionServiceV1?wsdl'
        self.retrieval_url = 'https://eudr.webcloud.ec.europa.eu/tracesnt/ws/EUDRRetrievalServiceV1?wsdl'

    def _generate_security(self):
        nonce_bytes = os.urandom(16)
        nonce_b64 = base64.b64encode(nonce_bytes).decode()
        created_dt = datetime.now(timezone.utc)
        created = created_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        expires = (created_dt + timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        password_digest = base64.b64encode(
            hashlib.sha1(nonce_bytes + created.encode('utf-8') + self.auth_key.encode('utf-8')).digest()
        ).decode()
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
        geojson_b64 = base64.b64encode(json.dumps(geojson_data).encode()).decode()
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
                    <v11:producers>
                        <v11:country>{statement_data['producers']['country']}</v11:country>
                        <v11:name>{statement_data['producers']['name']}</v11:name>
                        <v11:geometryGeojson>{geojson_b64}</v11:geometryGeojson>
                    </v11:producers>
                </v11:commodities>
                <v11:geoLocationConfidential>{str(statement_data.get('geoLocationConfidential', False)).lower()}</v11:geoLocationConfidential>
            </v1:statement>
        </v1:SubmitStatementRequest>"""
        return self._post(body, is_submission=True)

    def amend_statement(self, geojson_data: dict, ddsIdentifier: str, statement_data: dict):
        geojson_b64 = base64.b64encode(json.dumps(geojson_data).encode()).decode()
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
                    <v11:producers>
                        <v11:country>{statement_data['producers']['country']}</v11:country>
                        <v11:name>{statement_data['producers']['name']}</v11:name>
                        <v11:geometryGeojson>{geojson_b64}</v11:geometryGeojson>
                    </v11:producers>
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
        body = f"<v1:GetStatementByIdentifiersRequest><v1:referenceNumber>{reference}</v1:referenceNumber><v1:verificationNumber>{verification}</v1:verificationNumber></v1:GetStatementByIdentifiersRequest>"
        return self._post(body, is_submission=False)
