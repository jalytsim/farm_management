"""Warehouse movements and the figures built from them.

Every kilogram entering or leaving a warehouse is written here, one row per
event. The receipt holds the current state; this table holds the history —
which is what a daily in/out dashboard needs, and what an auditor asks for.
"""

from datetime import datetime, timedelta, date
from decimal import Decimal

from app import db
from app.models import (
    WarehouseMovement, WarehouseReceipt, Store, Crop, CropVariety, Grade,
    OPEN_RECEIPT_STATUSES,
)

ZERO = Decimal('0')

# Why the weight moved. 'reception' and 'release' are the everyday ones.
MOVEMENT_REASONS = ('reception', 'release', 'cancellation', 'adjustment', 'loss')


def log_movement(store_id, receipt, direction, weight_kg, reason,
                 note=None, created_by=None):
    """Writes one line of history. The caller has already changed the receipt."""
    db.session.add(WarehouseMovement(
        store_id=store_id,
        receipt_id=receipt.id if receipt else None,
        direction=direction,                 # 'in' or 'out'
        weight_kg=Decimal(str(weight_kg)),
        reason=reason,
        crop_id=receipt.crop_id if receipt else None,
        variety_id=receipt.variety_id if receipt else None,
        grade_id=receipt.grade_id if receipt else None,
        note=note,
        created_by=created_by,
    ))


# ── Figures ──────────────────────────────────────────────────────────────────
def daily_flows(store_id=None, days=30):
    """In and out per day, oldest first. Days with no movement are kept at zero,
    otherwise the chart would lie about quiet periods."""
    since = datetime.utcnow().date() - timedelta(days=days - 1)

    query = (db.session.query(
        db.func.date(WarehouseMovement.date_created),
        WarehouseMovement.direction,
        db.func.sum(WarehouseMovement.weight_kg))
        .filter(WarehouseMovement.date_created >= since))
    if store_id:
        query = query.filter(WarehouseMovement.store_id == store_id)
    rows = query.group_by(db.func.date(WarehouseMovement.date_created),
                          WarehouseMovement.direction).all()

    buckets = {}
    for day, direction, weight in rows:
        key = day.isoformat() if hasattr(day, 'isoformat') else str(day)
        entry = buckets.setdefault(key, {'in': 0.0, 'out': 0.0})
        entry[direction] = float(weight or 0)

    series = []
    for offset in range(days):
        day = (since + timedelta(days=offset)).isoformat()
        entry = buckets.get(day, {'in': 0.0, 'out': 0.0})
        series.append({'date': day, 'in': entry['in'], 'out': entry['out'],
                       'net': entry['in'] - entry['out']})
    return series


def stock_lines(store_id=None):
    """What is held right now, by commodity, variety and grade."""
    query = (db.session.query(
        WarehouseReceipt.crop_id, WarehouseReceipt.variety_id, WarehouseReceipt.grade_id,
        db.func.sum(WarehouseReceipt.net_weight_kg - WarehouseReceipt.released_weight_kg),
        db.func.count(WarehouseReceipt.id))
        .filter(WarehouseReceipt.status.in_(OPEN_RECEIPT_STATUSES)))
    if store_id:
        query = query.filter(WarehouseReceipt.store_id == store_id)
    rows = query.group_by(WarehouseReceipt.crop_id, WarehouseReceipt.variety_id,
                          WarehouseReceipt.grade_id).all()

    lines = []
    for crop_id, variety_id, grade_id, weight, count in rows:
        if not weight or float(weight) <= 0:
            continue
        crop = Crop.query.get(crop_id)
        variety = CropVariety.query.get(variety_id) if variety_id else None
        grade = Grade.query.get(grade_id) if grade_id else None
        lines.append({
            'commodity': crop.name if crop else '—',
            'variety': variety.name if variety else None,
            'grade': grade.grade_value if grade else None,
            'weight_kg': float(weight),
            'receipts': count,
        })
    return sorted(lines, key=lambda line: -line['weight_kg'])


def held_weight(store_id=None):
    query = db.session.query(db.func.coalesce(db.func.sum(
        WarehouseReceipt.net_weight_kg - WarehouseReceipt.released_weight_kg), 0)) \
        .filter(WarehouseReceipt.status.in_(OPEN_RECEIPT_STATUSES))
    if store_id:
        query = query.filter(WarehouseReceipt.store_id == store_id)
    return float(query.scalar() or 0)


def capacity_summary(store_id=None):
    """Capacity of one warehouse, or of the whole network when store_id is None."""
    query = Store.query.filter_by(store_type='warehouse')
    if store_id:
        query = query.filter_by(id=store_id)
    stores = query.all()

    capacity_kg = sum(float(s.capacity_tonnes or 0) * 1000 for s in stores)
    held = held_weight(store_id)
    return {
        'warehouses': len(stores),
        'capacity_kg': capacity_kg or None,
        'held_kg': held,
        'free_kg': (capacity_kg - held) if capacity_kg else None,
        'usage_percent': round(held / capacity_kg * 100, 1) if capacity_kg else None,
    }


def today_totals(store_id=None):
    start = datetime.combine(date.today(), datetime.min.time())
    query = (db.session.query(WarehouseMovement.direction,
                              db.func.coalesce(db.func.sum(WarehouseMovement.weight_kg), 0))
             .filter(WarehouseMovement.date_created >= start))
    if store_id:
        query = query.filter(WarehouseMovement.store_id == store_id)
    rows = dict(query.group_by(WarehouseMovement.direction).all())
    received = float(rows.get('in') or 0)
    released = float(rows.get('out') or 0)
    return {'received_kg': received, 'released_kg': released, 'net_kg': received - released}


def top_depositors(store_id=None, days=90, limit=5):
    since = datetime.utcnow() - timedelta(days=days)
    query = (db.session.query(
        WarehouseReceipt.depositor_name,
        db.func.sum(WarehouseReceipt.net_weight_kg),
        db.func.count(WarehouseReceipt.id))
        .filter(WarehouseReceipt.received_at >= since,
                WarehouseReceipt.status != 'cancelled'))
    if store_id:
        query = query.filter(WarehouseReceipt.store_id == store_id)
    rows = (query.group_by(WarehouseReceipt.depositor_name)
            .order_by(db.func.sum(WarehouseReceipt.net_weight_kg).desc())
            .limit(limit).all())
    return [{'name': name, 'weight_kg': float(weight or 0), 'receipts': count}
            for name, weight, count in rows]