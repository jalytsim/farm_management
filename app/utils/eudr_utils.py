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


# ── Règles métier TRACES vérifiées avant l'envoi ─────────────────────────────
# Toutes testées en prod le 2026-10-08 (soumissions vouées à l'échec, aucune DDS
# créée). Les vérifier ici donne un message clair au lieu d'un Fault TRACES.

# EuropeanCountryType (XSD) : countryOfActivity / borderCrossCountry hors de
# cette liste → SAXParseException "cvc-enumeration-valid" (ex. 'UG').
EU_COUNTRIES = ('AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU',
                'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'XI')

# Bovins (Annexe I) : seuls produits autorisés au-delà de 4 ha pour un Point.
CATTLE_HS_PREFIXES = ('0102', '0201', '0202', '0206', '1602', '4101', '4104', '4107')

# Bois : TRACES exige nom scientifique + nom commun (EUDR-COMMODITIES-SPECIES-INFORMATION-EMPTY).
TIMBER_HS_CHAPTERS = ('44', '47', '48', '49')

# Opérateur du compte WS : hors UE → seule l'activité IMPORT est admise (doc
# "Validation rules"). REPRESENTATIVE_OPERATOR est refusé pour ce compte
# (EUDR-WEBSERVICE-USER-ACTIVITY-NOT-ALLOWED).
OPERATOR_COUNTRY = (os.environ.get('EUDR_OPERATOR_COUNTRY') or 'UG').strip().upper()
OPERATOR_IS_EU = OPERATOR_COUNTRY in EU_COUNTRIES
ALLOWED_ACTIVITY_TYPES = ('DOMESTIC', 'IMPORT', 'EXPORT') if OPERATOR_IS_EU else ('IMPORT',)
ALLOW_REPRESENTATIVE = str(os.environ.get('EUDR_ALLOW_REPRESENTATIVE') or '').strip().lower() in ('1', 'true', 'yes')
ALLOWED_OPERATOR_ROLES = ('OPERATOR', 'REPRESENTATIVE_OPERATOR') if ALLOW_REPRESENTATIVE else ('OPERATOR',)

GEOJSON_GEOMETRY_TYPES = ('Point', 'MultiPoint', 'Polygon', 'MultiPolygon')


def _check_position(pos, where, errors):
    if not (isinstance(pos, (list, tuple)) and len(pos) >= 2
            and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in pos[:2])):
        errors.append(f"{where}: each coordinate must be [longitude, latitude] in decimal degrees.")
        return
    lon, lat = pos[0], pos[1]
    if not -180 <= lon <= 180:
        errors.append(f"{where}: longitude {lon} must be between -180 and 180.")
    if not -90 <= lat <= 90:
        errors.append(f"{where}: latitude {lat} must be between -90 and 90 (coordinates are [longitude, latitude]).")


def _check_polygon(rings, where, errors):
    if not isinstance(rings, list) or not rings:
        errors.append(f"{where}: a Polygon needs at least one ring of coordinates.")
        return
    for ring in rings:
        if not isinstance(ring, list) or len(ring) < 4:
            errors.append(f"{where}: a Polygon ring needs at least 4 positions (first = last).")
            continue
        for pos in ring:
            _check_position(pos, where, errors)
        if list(ring[0][:2]) != list(ring[-1][:2]):
            errors.append(f"{where}: the Polygon is not closed (the first and last positions must be identical).")


def geojson_errors(gj, hs_digits=''):
    """
    Erreurs bloquantes d'un GeoJSON au regard des règles TRACES (doc "GeoJSON
    description" + validation rules). Liste vide = rien à signaler.
    """
    if not isinstance(gj, dict) or gj.get('type') != 'FeatureCollection':
        return ["The geolocation must be a GeoJSON FeatureCollection."]
    features = gj.get('features')
    if not isinstance(features, list) or not features:
        return ["The geolocation must contain at least one plot (Feature)."]
    errors = []
    is_cattle = str(hs_digits).startswith(CATTLE_HS_PREFIXES)
    for i, f in enumerate(features, start=1):
        where = f"Plot {i}"
        geom = (f or {}).get('geometry') if isinstance(f, dict) else None
        if not isinstance(geom, dict) or 'coordinates' not in geom:
            errors.append(f"{where}: missing geometry.")
            continue
        gtype, coords = geom.get('type'), geom.get('coordinates')
        if gtype not in GEOJSON_GEOMETRY_TYPES:
            errors.append(f"{where}: geometry type '{gtype}' is not accepted (use Point, MultiPoint, Polygon or MultiPolygon).")
            continue
        if gtype == 'Point':
            _check_position(coords, where, errors)
        elif gtype == 'MultiPoint':
            for pos in coords or []:
                _check_position(pos, where, errors)
        elif gtype == 'Polygon':
            _check_polygon(coords, where, errors)
        else:
            for poly in coords or []:
                _check_polygon(poly, where, errors)
        if gtype in ('Point', 'MultiPoint'):
            area = ((f.get('properties') or {}).get('Area'))
            if area not in (None, ''):
                try:
                    area = float(area)
                except (TypeError, ValueError):
                    errors.append(f"{where}: Area must be a number of hectares.")
                    continue
                if area < 0.0001:
                    errors.append(f"{where}: Area must be at least 0.0001 ha.")
                elif area > 4 and not is_cattle:
                    errors.append(f"{where}: a Point cannot exceed 4 ha (Area={area}). Draw the plot as a Polygon instead.")
    return errors


class EUDRClient:
    def __init__(self, username, auth_key, client_id='eudr-repository', operator_access_identifier=None):
        self.username = username
        self.auth_key = auth_key
        self.client_id = client_id
        # Web Service Access Identifier (Directory → Operators → [opérateur] →
        # Operator Identifiers). Obligatoire si le login est lié à plusieurs
        # opérateurs, optionnel mais pris en compte sinon (doc Operator API).
        self.operator_access_identifier = (operator_access_identifier or '').strip() or None
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
        if self.operator_access_identifier:
            # OperatorAccessIdentifier doit être non qualifié (sans namespace)
            header += f"""
        <body:BodyIdentity xmlns:body="http://ec.europa.eu/tracesnt/body/v3">
            <OperatorAccessIdentifier xmlns="">{_txt(self.operator_access_identifier)}</OperatorAccessIdentifier>
        </body:BodyIdentity>"""
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

        if operator_role not in ALLOWED_OPERATOR_ROLES:
            raise ValueError(
                f"operatorRole '{operator_role}' is not allowed for this TRACES account "
                f"(allowed: {', '.join(ALLOWED_OPERATOR_ROLES)}).")

        activity_type = str(statement_data.get('activityType') or '').strip().upper()
        if activity_type == 'TRADE':
            raise ValueError("activityType 'TRADE' n'existe plus en V3.")
        if activity_type and activity_type not in ALLOWED_ACTIVITY_TYPES:
            raise ValueError(
                f"activityType '{activity_type}' is not allowed: the operator is established outside the EU "
                f"({OPERATOR_COUNTRY}), only {', '.join(ALLOWED_ACTIVITY_TYPES)} is accepted.")

        for field in ('countryOfActivity', 'borderCrossCountry'):
            code = _country(statement_data.get(field))
            if code and code not in EU_COUNTRIES:
                raise ValueError(f"{field} must be an EU member state (got '{code}').")

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
        if hs_digits[:2] in TIMBER_HS_CHAPTERS and not (
                str(species.get('scientificName') or '').strip() and str(species.get('commonName') or '').strip()):
            raise ValueError(f"HS {hs_digits} is a timber product: scientific name and common name are required.")
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

    @staticmethod
    def _validate_geojson(geojson_data, statement_data):
        hs_digits = ''.join(ch for ch in str(statement_data.get('hsHeading') or '') if ch.isdigit())
        errors = geojson_errors(geojson_data, hs_digits)
        if errors:
            raise ValueError("Invalid geolocation: " + " ".join(errors[:10]))

    # ------------------------------------------------------------------
    # SUBMIT
    # ------------------------------------------------------------------
    def submit_statement(self, geojson_data: dict, statement_data: dict):
        self._validate_geojson(geojson_data, statement_data)
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
        déclaration envoyée a une géolocalisation lisible mais hors limites
        (latitude 95). ⚠️ Un GeoJSON illisible arrête TRACES AVANT le contrôle
        du code HS : l'ancienne version déclarait ainsi 0901 ou 1201 valides
        alors qu'ils sont refusés (testé en prod le 2026-10-08).
          - EUDR-COMMODITIES-HS-CODE-INVALID           → False (code refusé)
          - EUDR-COMMODITIES-PRODUCER-GEO-LATITUDE-INVALID seul → True (accepté)
          - toute autre réponse                        → None (indéterminé)
        """
        digits = ''.join(ch for ch in str(hs_code) if ch.isdigit())
        if not 2 <= len(digits) <= 6:
            return False
        invalid_geo = base64.b64encode(json.dumps({"type": "FeatureCollection", "features": [{
            "type": "Feature", "properties": {"Area": 1},
            "geometry": {"type": "Point", "coordinates": [32.58, 95.0]}}]}).encode()).decode()
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
        if 'EUDR-COMMODITIES-PRODUCER-GEO-LATITUDE-INVALID' in detail:
            return True
        return None

    # ------------------------------------------------------------------
    # AMEND
    # ------------------------------------------------------------------
    def amend_statement(self, geojson_data: dict, uuid: str, statement_data: dict):
        if not uuid or not str(uuid).strip():
            raise ValueError("DDS identifier (uuid) is required to amend a statement.")
        self._validate_geojson(geojson_data, statement_data)
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
        # GetDdsByIdentifiersRequestType.referenceAndVerificationNumber : ses enfants
        # sont en v3c (common). En v3, TRACES renvoyait toujours une SAXParseException
        # (testé en prod le 2026-10-08).
        body = f"""
        <v3:GetDdsByIdentifiersRequest>
            <v3:referenceAndVerificationNumber>
                <v3c:referenceNumber>{_txt(reference)}</v3c:referenceNumber>
                <v3c:verificationNumber>{_txt(verification)}</v3c:verificationNumber>
            </v3:referenceAndVerificationNumber>
        </v3:GetDdsByIdentifiersRequest>
        """
        return self._post(body)


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
    """
    GetDds : les champs de ddsOverviewList sont en v3c (common). Les chercher en
    v3 renvoyait tout vide, et la route by-dds-id effaçait alors la référence
    et le statut en base (testé en prod le 2026-10-08).
    """
    statements = extract_internal_ref_statements(xml_text)
    if not statements:
        return None
    s = statements[0]
    return {
        'identifier': s['identifier'],
        'internalReferenceNumber': s['internalReferenceNumber'],
        'referenceNumber': s['referenceNumber'],
        'verificationCode': s['verificationNumber'],
        'status': s['status'],
        'rejectionReason': s['rejectionReason'],
        'date': s['date'],
        'updatedBy': s['updatedBy'],
    }


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

        # Réponse réelle : descriptors/goodsMeasure en v3c, producers/country en v3
        # (l'inverse de ce qui était cherché → champs vides). Recherche par nom local.
        info = {
            'referenceNumber': _findtext_local(statement, 'referenceNumber'),
            'activityType': _findtext_local(statement, 'activityType'),
            'status': _findtext_local(statement, 'status'),
            'statusDate': _findtext_local(statement, 'date'),
            'geoLocationConfidential': _findtext_local(statement, 'geoLocationConfidential'),
            'operator': extract_operator_identity(xml_text) or {},
            'commodities': []
        }

        for commodity in statement.findall('v3:commodities', ns):
            commodity_info = {
                'descriptionOfGoods': _findtext_local(commodity, 'descriptionOfGoods'),
                'goodsMeasure': {
                    'netWeight': _findtext_local(commodity, 'netWeight'),
                    'supplementaryUnit': _findtext_local(commodity, 'supplementaryUnit'),
                    'supplementaryUnitQualifier': _findtext_local(commodity, 'supplementaryUnitQualifier'),
                },
                'speciesInfo': {
                    'scientificName': _findtext_local(commodity, 'scientificName'),
                    'commonName': _findtext_local(commodity, 'commonName'),
                },
                'hsHeading': _findtext_local(commodity, 'hsHeading'),
                'producers': []
            }

            for producer in commodity.findall('v3:producers', ns):
                country = _findtext_local(producer, 'country')
                geo_b64 = _findtext_local(producer, 'geometryGeojson')
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


# Erreurs métier TRACES dont la cause n'est pas dans l'enveloppe envoyée.
TRACES_ERROR_HINTS = {
    # En operatorRole=OPERATOR, l'opérateur est celui du compte WS : aucun TIN/CBR
    # n'est envoyé par l'app. TRACES contrôle les identifiants de la fiche
    # opérateur ; pour un opérateur hors UE (ex. UG), seuls EORI/GLN/DUNS… sont admis.
    'EUDR-OPERATOR-IDENTIFIER-NOT-ALLOWED-FOR-NON-EU-OPERATOR':
        "The TRACES operator profile linked to the web-service account (non-EU operator) "
        "contains TIN and/or Central Business Register identifiers. Remove them from the "
        "operator profile in TRACES (keep the EORI) and submit again.",
    'EUDR-WEBSERVICE-USER-ACTIVITY-NOT-ALLOWED':
        "This TRACES web-service account does not have the requested role "
        "(e.g. REPRESENTATIVE_OPERATOR). Submit as OPERATOR.",
    'EUDR-COMMODITIES-HS-CODE-INVALID':
        "TRACES does not accept this HS code. Use a 6-digit subheading (e.g. 090111 instead of 0901).",
    'EUDR-COMMODITIES-SPECIES-INFORMATION-EMPTY':
        "Timber products require a scientific name and a common name.",
    'EUDR-COMMODITIES-PRODUCER-GEO-AREA-INVALID':
        "A plot drawn as a Point cannot exceed 4 ha (except cattle): draw it as a Polygon.",
    'EUDR-COMMODITIES-PRODUCER-GEO-LATITUDE-INVALID':
        "A latitude is out of range: coordinates must be [longitude, latitude].",
    'EUDR-COMMODITIES-PRODUCER-GEO-INVALID':
        "The geolocation is invalid (unclosed polygon, crossing lines, wrong geometry type…). "
        "Fix the plot boundaries and submit again.",
    'EUDR-COMMODITITY-PRODUCER-COUNTRY-CODE-INVALID':
        "The producer country code is not a valid ISO alpha-2 code.",
}


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
            result = {
                'faultstring': faultstring or 'Unknown SOAP fault',
                'detail': detail or ''
            }
            # Codes en entier (GEO-INVALID est un préfixe de GEO-AREA-INVALID…)
            codes = set(re.findall(r'EUDR-[A-Z-]+', result['detail']))
            hints = [hint for code, hint in TRACES_ERROR_HINTS.items() if code in codes]
            if 'SAXParseException' in result['faultstring'] and 'cvc-enumeration-valid' in result['faultstring']:
                hints.append("A code value (country, unit…) is not in the list accepted by TRACES; "
                             "the country of activity must be an EU member state.")
            if hints:
                result['hint'] = "\n".join(hints)
            return result
        return None
    except ET.ParseError:
        return None