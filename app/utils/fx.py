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


# ── Conversion entre deux devises quelconques (paiement carte Cybersource) ──

# Devises sans décimales (ISO 4217, exposant 0) : montant arrondi à l'unité.
ZERO_DECIMAL_CURRENCIES = {'UGX', 'JPY', 'KRW', 'XOF', 'XAF', 'RWF', 'BIF', 'CLP', 'VND',
                           'GNF', 'KMF', 'DJF', 'PYG', 'VUV', 'XPF', 'ISK'}

_pair_cache = {}   # {(de, vers): (date, taux)}


def fx_rate(from_currency, to_currency):
    """Nombre d'unités de `to_currency` pour 1 `from_currency`, au taux du jour. None si inconnu."""
    src, dst = (from_currency or '').upper(), (to_currency or '').upper()
    if src == dst:
        return Decimal(1)
    if dst == MOBILE_MONEY_CURRENCY:
        return ugx_rate(src)
    today = date.today()
    cached = _pair_cache.get((src, dst))
    if cached and cached[0] == today:
        return cached[1]
    try:
        data = requests.get(RATES_URL.format(base=src), timeout=10).json()
        rate = data.get('rates', {}).get(dst) if data.get('result') == 'success' else None
        if rate:
            rate = Decimal(str(rate))
            _pair_cache[(src, dst)] = (today, rate)
            logger.info("[FX] 1 %s = %s %s (%s)", src, rate, dst, today)
            return rate
        logger.warning("[FX] No %s rate for %s: %s", dst, src, data.get('error-type'))
    except (requests.RequestException, ValueError):
        logger.exception("[FX] Rate API unreachable for %s", src)
    return cached[1] if cached else None


def round_up_amount(amount, currency):
    """Arrondi supérieur au centime (ou à l'unité pour les devises sans décimales)."""
    amount = Decimal(str(amount))
    if (currency or '').upper() in ZERO_DECIMAL_CURRENCIES:
        return Decimal(math.ceil(amount))
    return Decimal(math.ceil(amount * 100)) / 100


def convert(amount, from_currency, to_currency):
    """(montant converti arrondi au-dessus, taux) ou (None, None)."""
    rate = fx_rate(from_currency, to_currency)
    if rate is None or amount is None:
        return None, None
    return round_up_amount(Decimal(str(amount)) * rate, to_currency), rate
