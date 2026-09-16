# app/routes/ecommerce_stats.py
# =============================================================================
#  Statistiques de vente — nouveau fichier, rien à remplacer.
#
#  À enregistrer dans app/__init__.py :
#      from app.routes.ecommerce_stats import bp as ecommerce_stats_bp
#      app.register_blueprint(ecommerce_stats_bp)
#
#  Principes retenus :
#
#   1. TOUT est groupé par devise. EcoOrder porte sa propre `currency` :
#      additionner des total_amount sans grouper donnerait un CA faux dès
#      qu'une commande USD côtoie une commande UGX.
#
#   2. Le CA ne compte que les statuts qui représentent de l'argent encaissé
#      (paid, shipped, delivered). Une commande 'pending' n'est pas du CA :
#      elle n'est qu'une intention. Les remboursées et annulées sont exclues.
#
#   3. La séparation boutique / enchères se fait sur EcoOrderItem.auction_lot_id.
#      Une commande contenant au moins un lot adjugé est une vente d'enchère.
#      Aucun champ à ajouter, aucune migration.
#
#   4. La date retenue est date_created. Il n'existe pas de `paid_at` sur
#      EcoOrder : le paiement DPO suit la création de quelques minutes, l'écart
#      est négligeable à l'échelle du jour. Si un jour tu ajoutes `paid_at`,
#      c'est la seule constante à changer (DATE_COLUMN ci-dessous).
# =============================================================================

import csv
import io
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, Response
from sqlalchemy import func, distinct

from app import db
from app.models import (
    EcoOrder, EcoOrderItem, EcoProduct, ProductCategory,
)
from app.utils.decorators import admin_required

bp = Blueprint('ecommerce_stats', __name__, url_prefix='/api/ecommerce/stats')

# Statuts qui comptent comme du chiffre d'affaires encaissé.
REVENUE_STATUSES = ('paid', 'shipped', 'delivered')

# Colonne de référence pour toutes les fenêtres de temps.
DATE_COLUMN = EcoOrder.date_created

# Formats de regroupement : MySQL à gauche, l'équivalent Python à droite.
# Les deux doivent produire exactement la même chaîne, sinon le remplissage
# des trous ne retrouverait pas ses propres seaux.
BUCKETS = {
    'day':   ('%Y-%m-%d', '%Y-%m-%d'),
    'week':  ('%x-W%v',   '%G-W%V'),
    'month': ('%Y-%m',    '%Y-%m'),
}


# ==================== HELPERS ====================

def _f(value):
    return float(value) if value is not None else 0.0


def _parse_range(default_days=30):
    """Lit ?from= et ?to= (YYYY-MM-DD). Retourne des bornes [start, end[.

    `end` est exclusif et calé sur le lendemain de `to` : sans ça, une commande
    passée à 14 h le dernier jour de la période serait exclue du total.
    """
    today = datetime.utcnow().date()

    try:
        d_from = datetime.strptime(request.args['from'], '%Y-%m-%d').date()
    except (KeyError, ValueError):
        d_from = today - timedelta(days=default_days - 1)

    try:
        d_to = datetime.strptime(request.args['to'], '%Y-%m-%d').date()
    except (KeyError, ValueError):
        d_to = today

    if d_from > d_to:
        d_from, d_to = d_to, d_from

    start = datetime.combine(d_from, datetime.min.time())
    end = datetime.combine(d_to, datetime.min.time()) + timedelta(days=1)
    return d_from, d_to, start, end


def _auction_exists():
    """EXISTS corrélé : la commande contient-elle au moins un lot d'enchère ?"""
    return (db.session.query(EcoOrderItem.id)
            .filter(EcoOrderItem.order_id == EcoOrder.id,
                    EcoOrderItem.auction_lot_id.isnot(None))
            .exists())


def _apply_source(query, source=None):
    """Filtre boutique / enchères / tout."""
    source = (source or request.args.get('source') or 'all').lower()
    if source == 'shop':
        return query.filter(~_auction_exists())
    if source == 'auction':
        return query.filter(_auction_exists())
    return query


def _revenue_filter(query, start, end):
    return query.filter(
        EcoOrder.status.in_(REVENUE_STATUSES),
        DATE_COLUMN >= start,
        DATE_COLUMN < end,
    )


def _pct_change(current, previous):
    """Variation en %. None quand la période précédente est vide : afficher
    « +100 % » à partir de zéro ne veut rien dire."""
    if not previous:
        return None
    return round((current - previous) / previous * 100, 1)


# ==================== RÉSUMÉ ====================

@bp.route('/summary', methods=['GET'])
@admin_required
def summary():
    """Les chiffres d'en-tête, par devise, avec comparaison à la période
    précédente de même durée."""
    d_from, d_to, start, end = _parse_range()
    span = end - start
    prev_start, prev_end = start - span, start

    def revenue_rows(s, e):
        q = db.session.query(
            EcoOrder.currency.label('currency'),
            func.coalesce(func.sum(EcoOrder.total_amount), 0).label('revenue'),
            func.count(EcoOrder.id).label('orders'),
        )
        q = _apply_source(_revenue_filter(q, s, e))
        return {r.currency: r for r in q.group_by(EcoOrder.currency).all()}

    current = revenue_rows(start, end)
    previous = revenue_rows(prev_start, prev_end)

    # Quantités vendues : elles vivent sur les lignes, pas sur la commande.
    units_q = db.session.query(
        EcoOrder.currency.label('currency'),
        func.coalesce(func.sum(EcoOrderItem.quantity), 0).label('units'),
        func.count(distinct(EcoOrderItem.product_id)).label('distinct_products'),
    ).join(EcoOrderItem, EcoOrderItem.order_id == EcoOrder.id)
    units_q = _apply_source(_revenue_filter(units_q, start, end))
    units = {r.currency: r for r in units_q.group_by(EcoOrder.currency).all()}

    by_currency = []
    for currency, row in sorted(current.items(), key=lambda kv: -_f(kv[1].revenue)):
        revenue = _f(row.revenue)
        orders = row.orders or 0
        prev = previous.get(currency)
        prev_revenue = _f(prev.revenue) if prev else 0.0
        u = units.get(currency)
        by_currency.append({
            'currency': currency,
            'revenue': revenue,
            'orders': orders,
            'average_order_value': round(revenue / orders, 2) if orders else 0.0,
            'units_sold': _f(u.units) if u else 0.0,
            'distinct_products': (u.distinct_products if u else 0),
            'previous_revenue': prev_revenue,
            'revenue_change_pct': _pct_change(revenue, prev_revenue),
            'previous_orders': prev.orders if prev else 0,
            'orders_change_pct': _pct_change(orders, prev.orders if prev else 0),
        })

    # Répartition par statut : TOUS les statuts, pas seulement ceux du CA.
    # C'est là qu'on voit combien de paniers meurent avant paiement.
    status_q = db.session.query(
        EcoOrder.status.label('status'),
        func.count(EcoOrder.id).label('count'),
    ).filter(DATE_COLUMN >= start, DATE_COLUMN < end)
    status_q = _apply_source(status_q)
    by_status = [{'status': r.status, 'count': r.count}
                 for r in status_q.group_by(EcoOrder.status).all()]

    total_orders = sum(s['count'] for s in by_status)
    paid_orders = sum(s['count'] for s in by_status if s['status'] in REVENUE_STATUSES)

    # Ce qui demande une action de l'admin, indépendamment de la période.
    to_ship = EcoOrder.query.filter_by(status='paid').count()
    unpaid = EcoOrder.query.filter(EcoOrder.status.in_(('pending', 'payment_failed'))).count()

    return jsonify({
        'range': {'from': d_from.isoformat(), 'to': d_to.isoformat(),
                  'days': (end - start).days},
        'by_currency': by_currency,
        'by_status': by_status,
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        # Taux de conversion du panier : part des commandes créées qui ont
        # réellement été payées.
        'payment_rate': round(paid_orders / total_orders * 100, 1) if total_orders else None,
        'action_required': {'to_ship': to_ship, 'unpaid': unpaid},
    })


# ==================== SÉRIE TEMPORELLE ====================

@bp.route('/timeseries', methods=['GET'])
@admin_required
def timeseries():
    """CA et nombre de commandes par jour / semaine / mois, par devise.

    Les périodes sans vente sont remplies à zéro : une courbe qui saute les
    jours creux donne l'illusion d'une activité continue.
    """
    d_from, d_to, start, end = _parse_range()
    granularity = (request.args.get('granularity') or 'day').lower()
    if granularity not in BUCKETS:
        granularity = 'day'
    sql_fmt, py_fmt = BUCKETS[granularity]

    bucket = func.date_format(DATE_COLUMN, sql_fmt)

    q = db.session.query(
        bucket.label('bucket'),
        EcoOrder.currency.label('currency'),
        func.coalesce(func.sum(EcoOrder.total_amount), 0).label('revenue'),
        func.count(EcoOrder.id).label('orders'),
    )
    q = _apply_source(_revenue_filter(q, start, end))
    rows = q.group_by('bucket', EcoOrder.currency).order_by('bucket').all()

    # Liste ordonnée et complète des seaux de la période.
    labels, seen = [], set()
    cursor = d_from
    while cursor <= d_to:
        label = cursor.strftime(py_fmt)
        if label not in seen:
            seen.add(label)
            labels.append(label)
        cursor += timedelta(days=1)

    data = {}
    for r in rows:
        entry = data.setdefault(r.currency, {})
        entry[r.bucket] = {'revenue': _f(r.revenue), 'orders': r.orders}

    series = [{
        'currency': currency,
        'revenue': [buckets.get(l, {}).get('revenue', 0.0) for l in labels],
        'orders': [buckets.get(l, {}).get('orders', 0) for l in labels],
    } for currency, buckets in data.items()]

    return jsonify({'granularity': granularity, 'labels': labels, 'series': series})


# ==================== PRODUITS VENDUS ====================

@bp.route('/products-sold', methods=['GET'])
@admin_required
def products_sold():
    """Le tableau de bord des produits vendus.

    unit_price est GELÉ dans EcoOrderItem au moment de l'achat : on recalcule
    le CA ligne par ligne (quantity × unit_price) plutôt que de repartir du
    prix courant du produit, qui a pu changer depuis.
    """
    _, _, start, end = _parse_range()
    limit = min(int(request.args.get('limit') or 100), 500)

    q = db.session.query(
        EcoProduct.id.label('product_id'),
        EcoProduct.name.label('name'),
        EcoProduct.unit.label('unit'),
        EcoProduct.sale_mode.label('sale_mode'),
        EcoProduct.stock_qty.label('stock_qty'),
        EcoProduct.is_active.label('is_active'),
        ProductCategory.name.label('category'),
        EcoOrder.currency.label('currency'),
        func.sum(EcoOrderItem.quantity).label('qty_sold'),
        func.sum(EcoOrderItem.quantity * EcoOrderItem.unit_price).label('revenue'),
        func.count(distinct(EcoOrder.id)).label('order_count'),
        func.avg(EcoOrderItem.unit_price).label('avg_unit_price'),
        func.max(DATE_COLUMN).label('last_sold'),
        func.sum(func.if_(EcoOrderItem.auction_lot_id.isnot(None), 1, 0)).label('auction_lines'),
    ).join(EcoOrderItem, EcoOrderItem.product_id == EcoProduct.id) \
     .join(EcoOrder, EcoOrder.id == EcoOrderItem.order_id) \
     .outerjoin(ProductCategory, ProductCategory.id == EcoProduct.category_id)

    q = _apply_source(_revenue_filter(q, start, end))
    rows = (q.group_by(EcoProduct.id, EcoOrder.currency)
             .order_by(func.sum(EcoOrderItem.quantity * EcoOrderItem.unit_price).desc())
             .limit(limit).all())

    products = [{
        'product_id': r.product_id,
        'name': r.name,
        'category': r.category,
        'unit': r.unit,
        'sale_mode': r.sale_mode,
        'currency': r.currency,
        'qty_sold': _f(r.qty_sold),
        'revenue': _f(r.revenue),
        'order_count': r.order_count,
        'avg_unit_price': round(_f(r.avg_unit_price), 2),
        'stock_qty': _f(r.stock_qty),
        'is_active': r.is_active,
        'from_auction': bool(r.auction_lines),
        'last_sold': r.last_sold.isoformat() if r.last_sold else None,
    } for r in rows]

    # Répartition par catégorie, pour le camembert.
    cat_q = db.session.query(
        func.coalesce(ProductCategory.name, 'Uncategorised').label('category'),
        EcoOrder.currency.label('currency'),
        func.sum(EcoOrderItem.quantity * EcoOrderItem.unit_price).label('revenue'),
        func.sum(EcoOrderItem.quantity).label('qty_sold'),
    ).join(EcoProduct, EcoProduct.category_id == ProductCategory.id) \
     .join(EcoOrderItem, EcoOrderItem.product_id == EcoProduct.id) \
     .join(EcoOrder, EcoOrder.id == EcoOrderItem.order_id)
    cat_q = _apply_source(_revenue_filter(cat_q, start, end))
    categories = [{
        'category': r.category,
        'currency': r.currency,
        'revenue': _f(r.revenue),
        'qty_sold': _f(r.qty_sold),
    } for r in cat_q.group_by('category', EcoOrder.currency)
                    .order_by(func.sum(EcoOrderItem.quantity * EcoOrderItem.unit_price).desc())
                    .all()]

    return jsonify({'products': products, 'categories': categories})


@bp.route('/never-sold', methods=['GET'])
@admin_required
def never_sold():
    """Le catalogue dormant : produits actifs qui n'ont jamais été vendus.

    Aussi utile que le classement des meilleures ventes — c'est là que dort
    du stock immobilisé.
    """
    sold_ids = db.session.query(distinct(EcoOrderItem.product_id)) \
        .join(EcoOrder, EcoOrder.id == EcoOrderItem.order_id) \
        .filter(EcoOrder.status.in_(REVENUE_STATUSES)).subquery()

    products = (EcoProduct.query
                .filter(EcoProduct.is_active.is_(True),
                        ~EcoProduct.id.in_(db.session.query(sold_ids)))
                .order_by(EcoProduct.date_created.desc())
                .limit(50).all())

    return jsonify([{
        'product_id': p.id,
        'name': p.name,
        'category': p.category.name if p.category else None,
        'price': _f(p.price),
        'currency': p.currency,
        'unit': p.unit,
        'stock_qty': _f(p.stock_qty),
        'stock_value': _f(p.price) * _f(p.stock_qty),
        'created': p.date_created.isoformat() if p.date_created else None,
    } for p in products])


# ==================== CLIENTS ====================

@bp.route('/top-customers', methods=['GET'])
@admin_required
def top_customers():
    """Qui achète. Un invité est identifié par son email, un compte par son id.

    On regroupe sur COALESCE(email invité, email du compte) : le même acheteur
    qui commande une fois en invité puis une fois connecté n'apparaît pas deux
    fois.
    """
    _, _, start, end = _parse_range()

    from app.models import User
    identity = func.coalesce(EcoOrder.guest_email, User.email, EcoOrder.guest_phone)

    q = db.session.query(
        identity.label('identity'),
        func.coalesce(func.max(EcoOrder.guest_name), func.max(User.username)).label('name'),
        EcoOrder.currency.label('currency'),
        func.count(EcoOrder.id).label('orders'),
        func.sum(EcoOrder.total_amount).label('revenue'),
        func.max(DATE_COLUMN).label('last_order'),
    ).outerjoin(User, User.id == EcoOrder.user_id)

    q = _apply_source(_revenue_filter(q, start, end))
    rows = (q.filter(identity.isnot(None))
             .group_by('identity', EcoOrder.currency)
             .order_by(func.sum(EcoOrder.total_amount).desc())
             .limit(20).all())

    return jsonify([{
        'identity': r.identity,
        'name': r.name,
        'currency': r.currency,
        'orders': r.orders,
        'revenue': _f(r.revenue),
        'average_order_value': round(_f(r.revenue) / r.orders, 2) if r.orders else 0.0,
        'last_order': r.last_order.isoformat() if r.last_order else None,
    } for r in rows])


# ==================== EXPORT ====================

@bp.route('/export/orders.csv', methods=['GET'])
@admin_required
def export_orders():
    """Export CSV des commandes de la période — une ligne par article.

    Le format « une ligne par article » est celui qui se recoupe le mieux avec
    une comptabilité : chaque ligne porte son produit, sa quantité et son prix
    gelé, et l'identifiant de commande sert de clé de regroupement.
    """
    d_from, d_to, start, end = _parse_range(default_days=90)

    q = db.session.query(EcoOrder, EcoOrderItem, EcoProduct) \
        .join(EcoOrderItem, EcoOrderItem.order_id == EcoOrder.id) \
        .outerjoin(EcoProduct, EcoProduct.id == EcoOrderItem.product_id) \
        .filter(DATE_COLUMN >= start, DATE_COLUMN < end)
    q = _apply_source(q)

    status = request.args.get('status')
    if status:
        q = q.filter(EcoOrder.status == status)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        'order_id', 'date', 'status', 'customer', 'email', 'phone', 'country_address',
        'product', 'sku', 'quantity', 'unit', 'unit_price', 'line_total',
        'currency', 'order_total', 'source', 'dpo_ref',
    ])

    for order, item, product in q.order_by(DATE_COLUMN.desc()).all():
        writer.writerow([
            order.id,
            order.date_created.strftime('%Y-%m-%d %H:%M') if order.date_created else '',
            order.status,
            order.guest_name or (order.user.username if order.user else ''),
            order.guest_email or (order.user.email if order.user else ''),
            order.guest_phone or '',
            (order.shipping_address or '').replace('\n', ' '),
            product.name if product else 'Deleted product',
            product.sku if product else '',
            _f(item.quantity),
            item.unit or (product.unit if product else ''),
            _f(item.unit_price),
            _f(item.quantity) * _f(item.unit_price),
            order.currency,
            _f(order.total_amount),
            'auction' if item.auction_lot_id else 'shop',
            order.dpo_trans_ref or '',
        ])

    filename = f"nkusu-orders-{d_from}-to-{d_to}.csv"
    return Response(
        buffer.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )