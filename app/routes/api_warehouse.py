from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import WarehouseMovement, Store, User
from app.utils.warehouse_utils import (
    daily_flows, stock_lines, capacity_summary, today_totals, top_depositors,
)

bp = Blueprint('api_warehouse', __name__, url_prefix='/api/warehouse')

VIEWING_ROLES = {'admin', 'warehouse_operator', 'qa_tester'}


def _current_user():
    identity = get_jwt_identity()
    user_id = identity['id'] if isinstance(identity, dict) else identity
    return User.query.get(user_id)


def _can_view(user):
    return bool(user and (user.is_admin or user.user_type in VIEWING_ROLES))


@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """?store_id= (omit for the whole network) · ?days=30"""
    user = _current_user()
    if not _can_view(user):
        return jsonify({"message": "Only warehouse staff can see this dashboard."}), 403

    store_id = request.args.get('store_id', type=int)
    days = min(max(request.args.get('days', 30, type=int), 7), 180)

    store = None
    if store_id:
        store = Store.query.get(store_id)
        if not store or store.store_type != 'warehouse':
            return jsonify({"message": "Warehouse not found."}), 404

    return jsonify({
        'warehouse': ({'id': store.id, 'code': store.code, 'name': store.name,
                       'country': store.country, 'district': store.district}
                      if store else None),
        'days': days,
        'today': today_totals(store_id),
        'capacity': capacity_summary(store_id),
        'flows': daily_flows(store_id, days),
        'stock': stock_lines(store_id),
        'top_depositors': top_depositors(store_id),
    })


@bp.route('/movements', methods=['GET'])
@jwt_required()
def movements():
    """The ledger itself: every kilogram in and out. ?store_id= ?page= ?per_page="""
    user = _current_user()
    if not _can_view(user):
        return jsonify({"message": "Only warehouse staff can see the movements."}), 403

    page = max(request.args.get('page', 1, type=int), 1)
    per_page = min(request.args.get('per_page', 25, type=int), 100)

    query = WarehouseMovement.query
    store_id = request.args.get('store_id', type=int)
    if store_id:
        query = query.filter_by(store_id=store_id)
    direction = request.args.get('direction')
    if direction in ('in', 'out'):
        query = query.filter_by(direction=direction)

    for key, comparison in (('from', 'ge'), ('to', 'le')):
        raw = request.args.get(key)
        if not raw:
            continue
        try:
            moment = datetime.strptime(raw, '%Y-%m-%d')
        except ValueError:
            continue
        query = (query.filter(WarehouseMovement.date_created >= moment) if comparison == 'ge'
                 else query.filter(WarehouseMovement.date_created
                                   < moment.replace(hour=23, minute=59, second=59)))

    total = query.count()
    rows = (query.order_by(WarehouseMovement.date_created.desc())
            .limit(per_page).offset((page - 1) * per_page).all())

    return jsonify({
        'items': [m.to_dict() for m in rows],
        'total': total,
        'page': page,
        'pages': max((total + per_page - 1) // per_page, 1),
    })