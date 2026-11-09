"""
cybersource_payment.py
──────────────────────────────────────────────────────────────────────────────
Paiement par carte via Cybersource Unified Checkout (fonctionnalités payantes),
en complément de DPO : Cybersource accepte EUR, GBP, CHF… que DPO ne prend pas.

Flux :
  1. create_capture_context() — le backend demande un « capture context »
     (JWT) pour le montant et la devise figés en base (PaidFeatureAccess).
  2. Le frontend charge la bibliothèque indiquée dans ce JWT (clientLibrary +
     clientLibraryIntegrity), affiche le formulaire carte et reçoit un
     transient token (valable 15 min). Le numéro de carte ne passe jamais par
     nos serveurs.
  3. pay_with_transient_token() — le backend autorise ET capture le paiement
     avec ce token, au montant de la base (jamais celui envoyé par le client).

Authentification : signature HTTP (HmacSHA256) avec la clé partagée REST du
Business Center (CYBERSOURCE_KEY_ID / CYBERSOURCE_SECRET_KEY).
"""

import base64
import hashlib
import hmac
import json
import logging
from email.utils import formatdate

import requests
from flask import current_app

logger = logging.getLogger(__name__)

HOSTS = {'test': 'apitest.cybersource.com', 'production': 'api.cybersource.com'}
CLIENT_VERSION = '0.31'
TIMEOUT = 30


class CybersourceError(Exception):
    pass


def is_configured():
    cfg = current_app.config
    return bool(cfg.get('CYBERSOURCE_MERCHANT_ID') and cfg.get('CYBERSOURCE_KEY_ID')
                and cfg.get('CYBERSOURCE_SECRET_KEY'))


def _host():
    return HOSTS.get(current_app.config.get('CYBERSOURCE_ENV', 'test'), HOSTS['test'])


def _request(method, path, body=None):
    """Appel REST signé. Retourne la réponse requests (le statut est géré par l'appelant)."""
    cfg = current_app.config
    merchant_id, key_id = cfg['CYBERSOURCE_MERCHANT_ID'], cfg['CYBERSOURCE_KEY_ID']
    secret = base64.b64decode(cfg['CYBERSOURCE_SECRET_KEY'])
    host = _host()
    payload = json.dumps(body, separators=(',', ':')) if body is not None else ''

    headers = {'host': host, 'date': formatdate(usegmt=True), 'v-c-merchant-id': merchant_id}
    signed = ['host', 'date', '(request-target)']
    if method in ('POST', 'PUT', 'PATCH'):
        headers['digest'] = 'SHA-256=' + base64.b64encode(hashlib.sha256(payload.encode()).digest()).decode()
        signed.append('digest')
    signed.append('v-c-merchant-id')

    lines = [f'(request-target): {method.lower()} {path}' if h == '(request-target)' else f'{h}: {headers[h]}'
             for h in signed]
    signature = base64.b64encode(hmac.new(secret, '\n'.join(lines).encode(), hashlib.sha256).digest()).decode()
    headers['signature'] = (f'keyid="{key_id}", algorithm="HmacSHA256", '
                            f'headers="{" ".join(signed)}", signature="{signature}"')
    headers['content-type'] = 'application/json;charset=utf-8'
    del headers['host']   # requests le pose lui-même, à l'identique

    return requests.request(method, f'https://{host}{path}', headers=headers,
                            data=payload or None, timeout=TIMEOUT)


def format_amount(amount, currency):
    from app.utils.fx import ZERO_DECIMAL_CURRENCIES
    return f'{amount:.0f}' if currency.upper() in ZERO_DECIMAL_CURRENCIES else f'{amount:.2f}'


def create_capture_context(amount, currency, target_origin):
    """JWT capture context pour afficher le formulaire carte sur `target_origin`."""
    body = {
        'targetOrigins': [target_origin],
        'clientVersion': CLIENT_VERSION,
        'allowedCardNetworks': ['VISA', 'MASTERCARD', 'AMEX'],
        'allowedPaymentTypes': ['PANENTRY'],
        'country': 'US',
        'locale': 'en_US',
        'captureMandate': {
            'billingType': 'PARTIAL',          # pays + code postal (contrôle AVS)
            'requestEmail': False,
            'requestPhone': False,
            'requestShipping': False,
            'showAcceptedNetworkIcons': True,
        },
        'orderInformation': {'amountDetails': {
            'totalAmount': format_amount(amount, currency), 'currency': currency.upper(),
        }},
    }
    res = _request('POST', '/up/v1/capture-contexts', body)
    if res.status_code not in (200, 201):
        logger.warning('[Cybersource] capture context %s: %s', res.status_code, res.text[:500])
        raise CybersourceError(f'Card payment could not be started ({res.status_code}).')
    return res.text.strip()


def pay_with_transient_token(transient_token, amount, currency, reference, email=None):
    """
    Autorise et capture le paiement. Retourne un dict :
      {status: 'paid'|'pending'|'failed', cybs_status, transaction_id, message}
    """
    body = {
        'clientReferenceInformation': {'code': reference[:50]},
        'processingInformation': {'capture': True, 'commerceIndicator': 'internet'},
        'tokenInformation': {'transientTokenJwt': transient_token},
        'orderInformation': {'amountDetails': {
            'totalAmount': format_amount(amount, currency), 'currency': currency.upper(),
        }},
    }
    if email:
        body['orderInformation']['billTo'] = {'email': email}
    res = _request('POST', '/pts/v2/payments', body)
    try:
        data = res.json()
    except ValueError:
        data = {}
    cybs_status = data.get('status')
    message = (data.get('errorInformation') or {}).get('message') or data.get('message') or data.get('reason')
    logger.info('[Cybersource] payment %s -> HTTP %s, status %s, id %s',
                reference, res.status_code, cybs_status, data.get('id'))

    if res.status_code == 201 and cybs_status == 'AUTHORIZED':
        status = 'paid'
    elif cybs_status in ('PENDING_REVIEW', 'AUTHORIZED_PENDING_REVIEW', 'PENDING'):
        status = 'pending'           # revue manuelle / anti-fraude : jamais d'accès avant confirmation
    elif res.status_code >= 500 or cybs_status == 'SERVER_ERROR':
        status = 'error'             # incident Cybersource : le client peut réessayer
    else:
        status = 'failed'            # DECLINED, INVALID_REQUEST, AUTHORIZED_RISK_DECLINED…
    return {'status': status, 'cybs_status': cybs_status, 'transaction_id': data.get('id'),
            'message': message, 'http_status': res.status_code}
