import json
import re
import requests
import os
import base64
import hashlib
import uuid as uuid_lib
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as _xml_escape

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


def _txt(value):
    """Échappe &, <, > — un nom d'opérateur/produit contenant '&' cassait tout l'envelope."""
    return _xml_escape(str(value).strip()) if value is not None else ''


def _el(tag, value):
    """
    Élément optionnel: omis s'il est vide. Le XSD V3 rejette les éléments vides
    typés (decimal, integer, codes pays/qualifiers en énumération) — c'est ce qui
    faisait échouer submit/amend alors que les retrievals (sans champs optionnels)
    passaient.
    """
    if value is None or str(value).strip() == '':
        return ''
    return f"<{tag}>{_txt(value)}</{tag}>"


def _country(value):
    """Codes pays ISO alpha-2 en majuscules (le XSD est une énumération sensible à la casse)."""
    return str(value).strip().upper() if value is not None and str(value).strip() else None


def _decimal(value, field):
    """
    Normalise une quantité pour DecimalSixteenTotalSixPrecType: accepte 1000, "1000",
    "1 000,5", "1000 kg". Renvoie None si vide, lève ValueError si non numérique.
    """
    if value is None or str(value).strip() == '':
        return None
    raw = str(value).strip().lower().replace('kg', '').replace(' ', '').replace(' ', '')
    if ',' in raw and '.' not in raw:
        raw = raw.replace(',', '.')
    else:
        raw = raw.replace(',', '')
    try:
        num = float(raw)
    except ValueError:
        raise ValueError(f"'{field}' must be a number (got '{value}').")
    if num <= 0:
        raise ValueError(f"'{field}' must be greater than 0.")
    return f"{num:.6f}".rstrip('0').rstrip('.')


# ── Unité supplémentaire ─────────────────────────────────────────────────────
# TRACES n'accepte le qualificatif (EUDR-COMMODITIES-DESCRIPTOR-SUPPLEMENTARY-
# UNIT-QUALIFIER-INVALID) que s'il correspond à l'unité supplémentaire de la
# Nomenclature combinée (NC) pour le code HS. Unités connues des positions EUDR :
SUPPLEMENTARY_UNIT_BY_HS = {
    '0102': 'NAR',   # bovins vivants : nombre de têtes (p/st)
    '4011': 'NAR',   # pneumatiques neufs (p/st)
    '4012': 'NAR',   # pneumatiques rechapés / usagés (p/st)
    '4403': 'MTQ',   # bois brut (m³)
    '4406': 'MTQ',   # traverses (m³)
    '4407': 'MTQ',   # bois sciés (m³)
    '4408': 'MTQ',   # feuilles de placage (m³)
    '4412': 'MTQ',   # bois contreplaqués (m³)
}
# Chapitres sans unité supplémentaire en NC : seul le poids net (kg) est déclaré.
# Viandes (02, 16), café (09), soja (12), huiles (15), cacao (18), tourteaux (23).
NO_SUPPLEMENTARY_UNIT_CHAPTERS = ('02', '09', '12', '15', '16', '18', '23')


def _supplementary_unit(hs_digits, unit, qualifier):
    """
    Renvoie (supplementaryUnit, qualifier) cohérents avec le code HS :
      - chapitre sans unité supplémentaire → rien n'est envoyé (le qualificatif
        choisi dans le formulaire était rejeté par TRACES) ;
      - unité NC connue → qualificatif imposé (NAR, MTQ…) ;
      - sinon → valeurs saisies, à condition d'avoir l'unité ET le qualificatif.
    """
    unit = _decimal(unit, 'goodsMeasure.supplementaryUnit')
    qualifier = str(qualifier or '').strip().upper()
    if hs_digits[:2] in NO_SUPPLEMENTARY_UNIT_CHAPTERS:
        return None, ''
    expected = SUPPLEMENTARY_UNIT_BY_HS.get(hs_digits[:4])
    if expected:
        if not unit:
            raise ValueError(
                f"HS {hs_digits} requires a supplementary unit in {expected} "
                f"({'number of items' if expected == 'NAR' else 'cubic metres'}).")
        return unit, expected
    if not unit:
        return None, ''  # qualificatif seul = rejeté par TRACES
    if not qualifier:
        raise ValueError("goodsMeasure.supplementaryUnitQualifier is required when supplementaryUnit is set.")
    return unit, qualifier


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
        # Ordre imposé par EconomicOperatorIdentificationType (XSD V3):
        # operatorReferenceNumber, operatorAddress, operatorEmail, operatorPhone, operatorName.
        # L'ancien ordre (operatorName en 2e) et les valeurs non échappées / vides
        # faisaient rejeter toute soumission en REPRESENTATIVE_OPERATOR.
        op = operator_data or {}
        name = str(op.get('name') or '').strip()
        if not name:
            raise ValueError("operator.name is required when operatorRole is REPRESENTATIVE_OPERATOR.")

        ref_xml = ""
        id_type = str(op.get('identifierType') or '').strip().lower()
        id_value = str(op.get('identifierValue') or '').strip()
        if id_type or id_value:
            if id_type not in ('eori', 'vat') or not id_value:
                raise ValueError("operator.identifierType must be 'eori' or 'vat' and operator.identifierValue is required.")
            ref_xml = f"""<v3c:operatorReferenceNumber>
                    <v3c:identifierType>{id_type}</v3c:identifierType>
                    <v3c:identifierValue>{_txt(id_value)}</v3c:identifierValue>
                </v3c:operatorReferenceNumber>"""

        address_xml = ""
        addr = {k: str(op.get(k) or '').strip() for k in ('country', 'street', 'postalCode', 'city')}
        if any(addr.values()):
            missing = [k for k, v in addr.items() if not v]
            if missing:
                raise ValueError(f"Operator address incomplete, missing: {', '.join('operator.' + m for m in missing)}")
            address_xml = f"""<v3c:operatorAddress>
                    <v3c:country>{_country(addr['country'])}</v3c:country>
                    <v3c:street>{_txt(addr['street'])}</v3c:street>
                    <v3c:postalCode>{_txt(addr['postalCode'])}</v3c:postalCode>
                    <v3c:city>{_txt(addr['city'])}</v3c:city>
                    {_el('v3c:fullAddress', op.get('address') or op.get('fullAddress'))}
                </v3c:operatorAddress>"""

        email = str(op.get('email') or '').strip()
        if email and not re.fullmatch(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", email):
            raise ValueError(f"operator.email '{email}' is not a valid email address.")

        return f"""
            <v3:representedOperator>
                {ref_xml}
                {address_xml}
                {_el('v3c:operatorEmail', op.get('email'))}
                {_el('v3c:operatorPhone', op.get('phone'))}
                <v3c:operatorName>{_txt(name)}</v3c:operatorName>
            </v3:representedOperator>"""

    def _build_producer_xml(self, producers, geojson_b64, require_non_empty=False):
        producer_xml = ""
        if producers and isinstance(producers, list):
            for prod in producers:
                if not isinstance(prod, dict):
                    continue
                country = _country(prod.get('country'))
                position = prod.get('position', '')
                # Le nom du producteur est optionnel dans le XSD V3 : seul le pays est
                # obligatoire. Avant, un producteur sans nom était ignoré silencieusement,
                # ce qui envoyait une DDS sans géolocalisation (rejetée par TRACES).
                if not country:
                    continue
                producer_xml += f"""
                    <v3:producers>
                        {_el('v3:position', position)}
                        <v3:country>{country}</v3:country>
                        {_el('v3:name', prod.get('name'))}
                        <v3:geometryGeojson>{geojson_b64}</v3:geometryGeojson>
                    </v3:producers>"""
        if require_non_empty and not producer_xml:
            raise ValueError("At least one producer with a country (ISO alpha-2, e.g. 'UG') is required.")
        return producer_xml

    def _build_statement_xml(self, statement_data: dict, producer_xml: str) -> str:
        # operatorRole: OPERATOR / REPRESENTATIVE_OPERATOR uniquement (TRADER supprimé en V3)
        operator_role = statement_data.get('operatorRole', statement_data.get('operatorType', 'OPERATOR'))
        if operator_role in ('TRADER', 'REPRESENTATIVE_TRADER'):
            raise ValueError(f"operatorRole '{operator_role}' n'existe plus en V3 (traders exclus de la soumission DDS).")

        activity_type = str(statement_data.get('activityType') or '').strip().upper()
        if activity_type == 'TRADE':
            raise ValueError("activityType 'TRADE' n'existe plus en V3.")

        operator_block = ""
        if operator_role == 'REPRESENTATIVE_OPERATOR':
            operator_block = self._build_operator_block(statement_data.get('operator', {}))

        internal_ref = (statement_data.get('internalReferenceNumber') or '').strip()
        if not internal_ref:
            raise ValueError("internalReferenceNumber is required.")
        # InternalReferenceNumberType: maxLength 50 dans le XSD V3 publié par TRACES
        if len(internal_ref) > 50:
            raise ValueError("internalReferenceNumber must not exceed 50 characters.")

        missing = [k for k in ('activityType', 'countryOfActivity', 'descriptionOfGoods', 'hsHeading')
                   if not str(statement_data.get(k) or '').strip()]
        if missing:
            raise ValueError(f"Missing required field(s): {', '.join(missing)}")

        # HSHeadingType : 2 à 6 chiffres. TRACES accepte le code au niveau de l'Annexe I
        # (ex. 0901, vérifié en prod le 2026-10-03) ou une sous-position existante
        # (090111). L'existence du code est contrôlée en amont par la table
        # hscode/hscode_subheading (verdicts TRACES, cf. hscode_sync.py).
        hs_digits = ''.join(ch for ch in str(statement_data['hsHeading']) if ch.isdigit())
        if not 2 <= len(hs_digits) <= 6:
            raise ValueError(f"HS code '{statement_data['hsHeading']}' must have 2 to 6 digits.")
        statement_data = dict(statement_data, hsHeading=hs_digits)

        goods = statement_data.get('goodsMeasure') or {}
        net_weight = _decimal(goods.get('netWeight'), 'goodsMeasure.netWeight')
        supp_unit, supp_qualifier = _supplementary_unit(
            hs_digits, goods.get('supplementaryUnit'), goods.get('supplementaryUnitQualifier'))
        if not net_weight and not supp_unit:
            raise ValueError("goodsMeasure.netWeight (kg) is required.")
        species = statement_data.get('speciesInfo') or {}
        # speciesInfo n'est envoyé que s'il est renseigné (bloc vide = rejet XSD)
        species_xml = ""
        if str(species.get('scientificName') or '').strip() or str(species.get('commonName') or '').strip():
            species_xml = f"""<v3:speciesInfo>
                    {_el('v3:scientificName', species.get('scientificName'))}
                    {_el('v3:commonName', species.get('commonName'))}
                </v3:speciesInfo>"""

        return f"""
            <v3:internalReferenceNumber>{_txt(internal_ref)}</v3:internalReferenceNumber>
            <v3:activityType>{_txt(activity_type)}</v3:activityType>
            {operator_block}
            <v3:countryOfActivity>{_country(statement_data['countryOfActivity'])}</v3:countryOfActivity>
            {_el('v3:borderCrossCountry', _country(statement_data.get('borderCrossCountry')))}
            {_el('v3:comment', statement_data.get('comment'))}
            <v3:commodities>
                <v3:position>1</v3:position>
                <v3:descriptors>
                    <v3c:descriptionOfGoods>{_txt(statement_data['descriptionOfGoods'])}</v3c:descriptionOfGoods>
                    <v3c:goodsMeasure>
                        {_el('v3c:netWeight', net_weight)}
                        {_el('v3c:supplementaryUnit', supp_unit)}
                        {_el('v3c:supplementaryUnitQualifier', supp_qualifier)}
                    </v3c:goodsMeasure>
                </v3:descriptors>
                <v3:hsHeading>{_txt(statement_data['hsHeading'])}</v3:hsHeading>
                {species_xml}
                {producer_xml}
            </v3:commodities>
            <v3:geoLocationConfidential>{'true' if str(statement_data.get('geoLocationConfidential')).strip().lower() in ('true', '1', 'yes') else 'false'}</v3:geoLocationConfidential>"""
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
        producer_xml = self._build_producer_xml(statement_data.get('producers', []), geojson_b64, require_non_empty=True)
        operator_role = statement_data.get('operatorRole', statement_data.get('operatorType', 'OPERATOR'))
        statement_xml = self._build_statement_xml(statement_data, producer_xml)

        body = f"""<v3:SubmitDdsRequest>
            <v3:operatorRole>{operator_role}</v3:operatorRole>
            <v3:statement>{statement_xml}
            </v3:statement>
        </v3:SubmitDdsRequest>"""

        return self._post(body)

    # ------------------------------------------------------------------
    # VÉRIFICATION D'UN CODE HS (sans créer de DDS)
    # ------------------------------------------------------------------
    def check_hs_code(self, hs_code: str):
        """
        Demande à TRACES si un code HS existe, sans jamais créer de DDS : la
        déclaration envoyée a une géolocalisation volontairement invalide.
        TRACES contrôle le code HS AVANT la géolocalisation (vérifié en prod) :
          - EUDR-COMMODITIES-HS-CODE-INVALID   → False (code refusé)
          - EUDR-COMMODITIES-PRODUCER-GEO-INVALID → True (code accepté)
          - toute autre réponse                → None (indéterminé)
        """
        digits = ''.join(ch for ch in str(hs_code) if ch.isdigit())
        if not 2 <= len(digits) <= 6:
            return False
        invalid_geo = base64.b64encode(b"not-a-geojson").decode()
        body = f"""<v3:SubmitDdsRequest>
            <v3:operatorRole>OPERATOR</v3:operatorRole>
            <v3:statement>
                <v3:internalReferenceNumber>HSCHECK-{digits}</v3:internalReferenceNumber>
                <v3:activityType>IMPORT</v3:activityType>
                <v3:countryOfActivity>BE</v3:countryOfActivity>
                <v3:commodities>
                    <v3:position>1</v3:position>
                    <v3:descriptors>
                        <v3c:descriptionOfGoods>HS code check, never submitted</v3c:descriptionOfGoods>
                        <v3c:goodsMeasure><v3c:netWeight>1</v3c:netWeight></v3c:goodsMeasure>
                    </v3:descriptors>
                    <v3:hsHeading>{digits}</v3:hsHeading>
                    <v3:producers>
                        <v3:country>UG</v3:country>
                        <v3:geometryGeojson>{invalid_geo}</v3:geometryGeojson>
                    </v3:producers>
                </v3:commodities>
                <v3:geoLocationConfidential>false</v3:geoLocationConfidential>
            </v3:statement>
        </v3:SubmitDdsRequest>"""
        response = self._post(body)
        fault = extract_soap_fault(response.text)
        if not fault:
            # Ne devrait jamais arriver (géolocalisation invalide) : on retire la DDS par sécurité.
            uuid = extract_dds_identifier(response.text)
            if uuid:
                self.withdraw_statement(uuid)
            return None
        detail = fault.get('detail') or ''
        if 'EUDR-COMMODITIES-HS-CODE-INVALID' in detail:
            return False
        if 'EUDR-COMMODITIES-PRODUCER-GEO-INVALID' in detail:
            return True
        return None

    # ------------------------------------------------------------------
    # AMEND
    # ------------------------------------------------------------------
    def amend_statement(self, geojson_data: dict, uuid: str, statement_data: dict):
        if not uuid or not str(uuid).strip():
            raise ValueError("DDS identifier (uuid) is required to amend a statement.")
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
        if el is not None and el.text:
            return el.text.strip()
        # Fallback sans namespace (même problème que pour by-internal-ref)
        return _findtext_local(root, 'uuid') or None
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
        if status_el is not None and status_el.text:
            return status_el.text.strip()
        return _findtext_local(root, 'status') or None
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


def extract_operator_identity(xml_text):
    """
    Opérateur que TRACES a rattaché à la DDS (réponse GetDds / GetDdsByIdentifiers) :
    nom, identifiants (EORI, VAT, TIN, CBR…), pays, email. Recherche par nom
    local, sans dépendre du namespace (v3 / v3c varient selon l'élément).
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None
    local = lambda el: el.tag.rsplit('}', 1)[-1]
    identity = {'name': '', 'identifiers': [], 'country': '', 'email': ''}
    for el in root.iter():
        tag = local(el)
        text = (el.text or '').strip()
        if tag == 'operatorName' and text and not identity['name']:
            identity['name'] = text
        elif tag == 'operatorEmail' and text and not identity['email']:
            identity['email'] = text
        elif tag in ('operatorReferenceNumber', 'operatorIdentifier'):
            kids = {local(c): (c.text or '').strip() for c in el}
            pair = {'type': kids.get('identifierType', ''), 'value': kids.get('identifierValue', '')}
            if pair['value'] and pair not in identity['identifiers']:
                identity['identifiers'].append(pair)
        elif tag == 'operatorAddress' and not identity['country']:
            identity['country'] = next(((c.text or '').strip() for c in el if local(c) == 'country'), '')
    return identity


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
            # operatorName est en v3c (cf. NS_COMMON) : l'ancien './/v3:operatorName'
            # renvoyait toujours '' → impossible de voir à quel opérateur la DDS est rattachée.
            'operator': extract_operator_identity(xml_text) or {},
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


def _findtext_local(elem, local_name):
    """
    Cherche un descendant par nom local, sans tenir compte du préfixe de
    namespace (v3, v3c, ou autre) — la réponse TRACES mélange les namespaces
    entre les types 'response' (v3) et les types 'common' (v3c) réutilisés,
    et deviner le bon préfixe champ par champ s'est révélé peu fiable.
    """
    for child in elem.iter():
        if child.tag.rsplit('}', 1)[-1] == local_name:
            return (child.text or '').strip()
    return ''


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
                'identifier': _findtext_local(info, 'uuid'),
                'internalReferenceNumber': _findtext_local(info, 'internalReferenceNumber'),
                'referenceNumber': _findtext_local(info, 'referenceNumber'),
                'verificationNumber': _findtext_local(info, 'verificationNumber'),
                'status': _findtext_local(info, 'status'),
                'rejectionReason': _findtext_local(info, 'rejectionReason'),
                'date': _findtext_local(info, 'date'),
                'updatedBy': _findtext_local(info, 'updatedBy')
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
            # Les erreurs métier TRACES sont des éléments imbriqués dans <detail>
            # (Error/ID + Error/Message) — findtext('.//detail') renvoyait donc ''.
            errors = []
            for el in fault.iter():
                if el.tag.rsplit('}', 1)[-1] == 'Error':
                    err_id = _findtext_local(el, 'ID')
                    msg = _findtext_local(el, 'Message')
                    errors.append(f"{err_id}: {msg}" if err_id else msg)
            detail = "\n".join(e for e in errors if e) or fault.findtext('.//detail')
            return {
                'faultstring': faultstring or 'Unknown SOAP fault',
                'detail': detail or ''
            }
        return None
    except ET.ParseError:
        return None