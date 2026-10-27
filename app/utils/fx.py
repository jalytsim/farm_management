# app/utils/fx.py
# =============================================================================
#  Conversion vers le shilling ougandais, au taux du jour.
#
#  La passerelle Mobile Money Nkusu (IO / nkusu-iot) ne prélève qu'en UGX :
#  un prix en USD (ou autre) est converti ici avant d'être envoyé.
#  DPO, lui, reçoit la devise d'origine et gère ses propres moyens de paiement.
#
#  Taux : open.er-api.com (gratuit, sans clé, mis à jour une fois par jour),
#  gardé en mémoire pour la journée. Si l'API ne répond pas, on reprend le
#  dernier taux connu, puis UGX_PER_USD (.env) pour l'USD.
# =============================================================================

import logging
import math
from datetime import date
from decimal import Decimal

import requests
from flask import current_app

logger = logging.getLogger(__name__)

MOBILE_MONEY_CURRENCY = 'UGX'
RATES_URL = 'https://open.er-api.com/v6/latest/{base}'

# {devise: (date, taux en UGX pour 1 unité)}
_cache = {}


def ugx_rate(currency):
    """Nombre de UGX pour 1 unité de `currency`, au taux du jour. None si inconnu."""
    currency = (currency or '').upper()
    if currency == MOBILE_MONEY_CURRENCY:
        return Decimal(1)

    today = date.today()
    cached = _cache.get(currency)
    if cached and cached[0] == today:
        return cached[1]

    try:
        res = requests.get(RATES_URL.format(base=currency), timeout=10)
        data = res.json()
        rate = data.get('rates', {}).get(MOBILE_MONEY_CURRENCY) if data.get('result') == 'success' else None
        if rate:
            rate = Decimal(str(rate))
            _cache[currency] = (today, rate)
            logger.info("[FX] 1 %s = %s UGX (%s)", currency, rate, today)
            return rate
        logger.warning("[FX] No UGX rate for %s: %s", currency, data.get('error-type'))
    except (requests.RequestException, ValueError):
        logger.exception("[FX] Rate API unreachable for %s", currency)

    if cached:                       # taux d'hier plutôt que rien
        return cached[1]
    if currency == 'USD':
        fallback = current_app.config.get('UGX_PER_USD')
        if fallback:
            return Decimal(str(fallback))
    return None


def to_ugx(amount, currency):
    """Montant converti en UGX, arrondi au shilling supérieur (Mobile Money ne
    prend pas de décimales). Retourne (montant_ugx, taux) ou (None, None)."""
    rate = ugx_rate(currency)
    if rate is None or amount is None:
        return None, None
    return Decimal(math.ceil(Decimal(str(amount)) * rate)), rate
