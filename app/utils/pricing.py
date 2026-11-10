# app/utils/pricing.py
# =============================================================================
#  Prix régionaux : prix de base du produit × coefficient de la région du pays
#  de LIVRAISON.
#
#  · Les pays de chaque région sont fixés ici (une seule source : le front les
#    reçoit par /api/pricing/regions).
#  · Les COEFFICIENTS sont en base (table priceregion), réglables par l'admin.
#    Les régions manquantes sont créées avec les valeurs par défaut.
#  · Union européenne : un seul prix pour toute la région « europe » — on ne
#    différencie pas les clients européens selon leur pays.
# =============================================================================

from decimal import Decimal, ROUND_HALF_UP

from app import db

EAST_AFRICA = {'UG', 'KE', 'TZ', 'RW', 'BI', 'SS', 'CD', 'SO', 'ET'}

AFRICA_OTHER = {
    'DZ', 'AO', 'BJ', 'BW', 'BF', 'CV', 'CM', 'CF', 'TD', 'KM', 'CG', 'CI', 'DJ',
    'EG', 'GQ', 'ER', 'SZ', 'GA', 'GM', 'GH', 'GN', 'GW', 'LS', 'LR', 'LY', 'MG',
    'MW', 'ML', 'MR', 'MU', 'MA', 'MZ', 'NA', 'NE', 'NG', 'ST', 'SN', 'SC', 'SL',
    'ZA', 'SD', 'TG', 'TN', 'ZM', 'ZW', 'EH', 'RE', 'YT', 'SH',
}

EUROPE = {
    # Union européenne
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU',
    'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE',
    # Reste de l'Europe
    'GB', 'CH', 'NO', 'IS', 'LI', 'AD', 'MC', 'SM', 'VA', 'AL', 'BA', 'ME', 'MK',
    'RS', 'XK', 'MD', 'UA', 'BY', 'GI', 'IM', 'JE', 'GG', 'FO',
}

NORTH_AMERICA = {'US', 'CA'}

# (code, nom affiché, coefficient par défaut, pays). L'ordre est l'ordre d'affichage.
DEFAULT_REGIONS = [
    ('east_africa',   'East Africa',    Decimal('1.00'), EAST_AFRICA),
    ('africa_other',  'Rest of Africa', Decimal('1.10'), AFRICA_OTHER),
    ('europe',        'Europe',         Decimal('1.30'), EUROPE),
    ('north_america', 'North America',  Decimal('1.35'), NORTH_AMERICA),
    ('rest_of_world', 'Rest of world',  Decimal('1.25'), None),     # tous les autres pays
]
FALLBACK_REGION = 'rest_of_world'

# Devises sans centimes : le prix régional est arrondi à l'unité.
NO_DECIMAL_CURRENCIES = {'UGX', 'KES', 'TZS', 'RWF', 'BIF', 'MGA'}


def normalize_country(country):
    code = (country or '').strip().upper()
    return code if len(code) == 2 and code.isalpha() else None


def region_for_country(country):
    code = normalize_country(country)
    if not code:
        return None
    for region_code, _name, _mult, countries in DEFAULT_REGIONS:
        if countries and code in countries:
            return region_code
    return FALLBACK_REGION


def ensure_default_regions():
    """Crée les régions manquantes avec leur coefficient par défaut."""
    from app.models import PriceRegion
    existing = {r.code for r in PriceRegion.query.all()}
    created = False
    for position, (code, name, mult, _countries) in enumerate(DEFAULT_REGIONS, start=1):
        if code not in existing:
            db.session.add(PriceRegion(code=code, name=name, multiplier=mult, position=position))
            created = True
    if created:
        db.session.commit()


def multiplier_for_country(country):
    """Coefficient du pays de livraison. Sans pays : 1 (prix de base)."""
    region_code = region_for_country(country)
    if not region_code:
        return Decimal('1')
    from app.models import PriceRegion
    region = PriceRegion.query.filter_by(code=region_code).first()
    if region is None:
        ensure_default_regions()
        region = PriceRegion.query.filter_by(code=region_code).first()
    return Decimal(str(region.multiplier)) if region else Decimal('1')


def round_price(amount, currency):
    step = Decimal('1') if (currency or '').upper() in NO_DECIMAL_CURRENCIES else Decimal('0.01')
    return Decimal(str(amount)).quantize(step, rounding=ROUND_HALF_UP)


def regional_price(base_price, currency, country):
    """Prix au kilo (ou à l'unité) pour un client livré dans `country`."""
    if base_price is None:
        return None
    return round_price(Decimal(str(base_price)) * multiplier_for_country(country), currency)


def regions_payload():
    """Ce que le front reçoit : régions, coefficients et pays de chaque région."""
    from app.models import PriceRegion
    ensure_default_regions()
    countries = {code: sorted(cs) if cs else None for code, _n, _m, cs in DEFAULT_REGIONS}
    return {
        'regions': [{
            'id': r.id, 'code': r.code, 'name': r.name,
            'multiplier': float(r.multiplier), 'position': r.position,
            'countries': countries.get(r.code),
        } for r in PriceRegion.query.order_by(PriceRegion.position).all()],
        'fallback_region': FALLBACK_REGION,
        'no_decimal_currencies': sorted(NO_DECIMAL_CURRENCIES),
    }