# app/routes/ecommerce_customers.py
# =============================================================================
#  Buyers list — who ordered, how often, how much, and what is still to ship.
#
#  A buyer has no unique id in the database: the same person can order as a
#  guest, then signed in, with "+256 772 123 456" or "0772123456". Orders are
#  therefore grouped by, in this order: the user account, then the normalised
#  phone number, then the lowercased email. Without this, one person would
#  appear three times.
#
#  Grouping runs in Python rather than SQL: the normalisation rules would be
#  unreadable (and non-portable) as SQL, and a shop of this size holds at most
#  a few thousand orders.
# =============================================================================

import csv
import io
import re
from datetime import datetime

from flask import Blueprint, jsonify, request, Response

from app import db
from app.models import EcoOrder, EcoOrderItem, User
from app.utils.decorators import admin_required

bp = Blueprint('ecommerce_customers', __name__, url_prefix='/api/ecommerce/customers')

PAID_STATUSES = {'paid', 'shipped', 'delivered'}
TO_SHIP_STATUS = 'paid'


# ── Helpers ──────────────────────────────────────────────────────────────────
def _normalise_phone(phone):
    """Keeps the last 9 digits: enough to match a number written in any format,
    short enough to ignore country prefixes typed inconsistently."""
    if not phone:
        return None
    digits = re.sub(r'\D', '', phone)
    return digits[-9:] if len(digits) >= 9 else (digits or None)


def _normalise_email(email):
    return email.strip().lower() if email and email.strip() else None


def _customer_key(order):
    """Returns (key, kind). The key is stable and safe to put in a URL."""
    if order.user_id:
        return f"user:{order.user_id}", 'account'
    phone = _normalise_phone(order.guest_phone)
    if phone:
        return f"phone:{phone}", 'guest'
    email = _normalise_email(order.guest_email)
    if email:
        return f"email:{email}", 'guest'
    return f"order:{order.id}", 'guest'


def _build_customers():
    """Groups every order by buyer. Returns a dict {key: customer}."""
    orders = (EcoOrder.query
              .order_by(EcoOrder.date_created.asc())
              .all())

    usernames = {}
    user_ids = {o.user_id for o in orders if o.user_id}
    if user_ids:
        usernames = {u.id: u.username for u in User.query.filter(User.id.in_(user_ids)).all()}

    customers = {}
    for order in orders:
        key, kind = _customer_key(order)
        entry = customers.setdefault(key, {
            'key': key,
            'kind': kind,
            'name': None,
            'email': None,
            'phone': None,
            'user_id': None,
            'shipping_address': None,
            'orders_count': 0,
            'to_ship': 0,
            'unpaid': 0,
            'spent': {},               # {currency: amount}
            'first_order_at': None,
            'last_order_at': None,
            'order_ids': [],
        })

        # Orders are walked oldest first, so the latest contact details win.
        entry['name'] = order.guest_name or usernames.get(order.user_id) or entry['name']
        entry['email'] = order.guest_email or entry['email']
        entry['phone'] = order.guest_phone or entry['phone']
        entry['shipping_address'] = order.shipping_address or entry['shipping_address']
        if order.user_id:
            entry['user_id'] = order.user_id
            entry['kind'] = 'account'
            if not entry['email']:
                user = User.query.get(order.user_id)
                entry['email'] = user.email if user else None

        entry['orders_count'] += 1
        entry['order_ids'].append(order.id)
        if order.status == TO_SHIP_STATUS:
            entry['to_ship'] += 1
        if order.status in ('pending', 'payment_failed'):
            entry['unpaid'] += 1
        if order.status in PAID_STATUSES:
            currency = order.currency or 'USD'
            entry['spent'][currency] = entry['spent'].get(currency, 0) + float(order.total_amount or 0)

        created = order.date_created
        if created:
            if entry['first_order_at'] is None or created < entry['first_order_at']:
                entry['first_order_at'] = created
            if entry['last_order_at'] is None or created > entry['last_order_at']:
                entry['last_order_at'] = created

    return customers


def _serialise(entry):
    return {
        **entry,
        'first_order_at': entry['first_order_at'].isoformat() if entry['first_order_at'] else None,
        'last_order_at': entry['last_order_at'].isoformat() if entry['last_order_at'] else None,
        'spent': [{'currency': c, 'amount': round(a, 2)} for c, a in sorted(entry['spent'].items())],
        'order_ids': entry['order_ids'][-50:],
    }


def _matches(entry, needle):
    haystack = ' '.join(filter(None, [entry['name'], entry['email'], entry['phone']])).lower()
    return needle in haystack


# ── Buyers list ──────────────────────────────────────────────────────────────
@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
@admin_required
def list_customers():
    """?q= search · ?sort=recent|orders|spent · ?to_ship=1 · ?page= &per_page="""
    page = max(int(request.args.get('page') or 1), 1)
    per_page = min(int(request.args.get('per_page') or 20), 100)
    sort = (request.args.get('sort') or 'recent').lower()
    needle = (request.args.get('q') or '').strip().lower()

    customers = list(_build_customers().values())

    if needle:
        customers = [c for c in customers if _matches(c, needle)]
    if request.args.get('to_ship') == '1':
        customers = [c for c in customers if c['to_ship'] > 0]

    if sort == 'orders':
        customers.sort(key=lambda c: c['orders_count'], reverse=True)
    elif sort == 'spent':
        customers.sort(key=lambda c: sum(c['spent'].values()), reverse=True)
    else:
        customers.sort(key=lambda c: c['last_order_at'] or datetime.min, reverse=True)

    total = len(customers)
    start = (page - 1) * per_page
    window = customers[start:start + per_page]

    # Totals over the whole (filtered) selection, not just the page shown.
    spent_total = {}
    for c in customers:
        for currency, amount in c['spent'].items():
            spent_total[currency] = spent_total.get(currency, 0) + amount

    return jsonify({
        'items': [_serialise(c) for c in window],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': max((total + per_page - 1) // per_page, 1),
        'repeat_buyers': sum(1 for c in customers if c['orders_count'] > 1),
        'to_ship_buyers': sum(1 for c in customers if c['to_ship'] > 0),
        'selection_spent': [{'currency': c, 'amount': round(a, 2)}
                            for c, a in sorted(spent_total.items())],
    })


# ── One buyer, with every order ──────────────────────────────────────────────
@bp.route('/detail', methods=['GET'])
@admin_required
def customer_detail():
    """?key=user:12 | phone:772123456 | email:jane@example.com"""
    key = request.args.get('key')
    if not key:
        return jsonify({"msg": "key is required"}), 400

    entry = _build_customers().get(key)
    if not entry:
        return jsonify({"msg": "Buyer not found"}), 404

    orders = (EcoOrder.query
              .filter(EcoOrder.id.in_(entry['order_ids']))
              .order_by(EcoOrder.date_created.desc())
              .all())

    # What this buyer buys most often, by quantity.
    rows = (db.session.query(EcoOrderItem.product_id,
                             db.func.sum(EcoOrderItem.quantity))
            .filter(EcoOrderItem.order_id.in_(entry['order_ids']))
            .group_by(EcoOrderItem.product_id).all())
    from app.models import EcoProduct
    products = {p.id: p.name for p in EcoProduct.query.filter(
        EcoProduct.id.in_([r[0] for r in rows])).all()} if rows else {}
    favourites = sorted(
        [{'product_id': pid, 'name': products.get(pid, f'#{pid}'), 'quantity': float(qty or 0)}
         for pid, qty in rows],
        key=lambda x: x['quantity'], reverse=True)[:5]

    return jsonify({
        'customer': _serialise(entry),
        'favourites': favourites,
        'orders': [o.to_dict() for o in orders],
    })


# ── CSV export ───────────────────────────────────────────────────────────────
@bp.route('/export.csv', methods=['GET'])
@admin_required
def export_customers():
    customers = list(_build_customers().values())
    customers.sort(key=lambda c: c['last_order_at'] or datetime.min, reverse=True)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Name', 'Email', 'Phone', 'Type', 'Orders', 'To ship',
                     'Total spent', 'First order', 'Last order', 'Shipping address'])
    for c in customers:
        writer.writerow([
            c['name'] or '', c['email'] or '', c['phone'] or '',
            'Account' if c['kind'] == 'account' else 'Guest',
            c['orders_count'], c['to_ship'],
            ' / '.join(f"{round(a, 2)} {cur}" for cur, a in sorted(c['spent'].items())),
            c['first_order_at'].strftime('%Y-%m-%d') if c['first_order_at'] else '',
            c['last_order_at'].strftime('%Y-%m-%d') if c['last_order_at'] else '',
            (c['shipping_address'] or '').replace('\n', ' '),
        ])

    return Response(
        buffer.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition':
                 f'attachment; filename=nkusu-buyers-{datetime.utcnow():%Y-%m-%d}.csv'},
    )