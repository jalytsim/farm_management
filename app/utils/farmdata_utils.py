from datetime import datetime
from flask_login import current_user
from app import db
from app.models import FarmData


def create_farmdata(data, user=None):
    user_id = user.id if user else current_user.id

    # Champs obligatoires
    required = ['farm_id', 'crop_id']
    missing = [f for f in required if f not in data or str(data[f]).strip() == '']
    if missing:
        raise ValueError(f"Missing required farmdata field(s): {', '.join(missing)}")

    # Conversions protégées
    def to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    # Construction du dictionnaire à insérer
    farmdata = FarmData(
        farm_id=data['farm_id'],
        crop_id=to_int(data['crop_id']),
        land_type=data.get('land_type') or 'unspecified',
        tilled_land_size=to_float(data.get('tilled_land_size')),
        planting_date=data.get('planting_date') or None,
        season=to_int(data.get('season'), 1),
        quality=data.get('quality') or 'standard',
        quantity=to_int(data.get('quantity')),
        harvest_date=data.get('harvest_date') or None,
        expected_yield=to_float(data.get('expected_yield')),
        actual_yield=to_float(data.get('actual_yield')),
        timestamp=datetime.utcnow(),
        channel_partner=data.get('channel_partner') or 'unspecified',
        destination_country=data.get('destination_country') or 'unspecified',
        customer_name=data.get('customer_name') or 'unspecified',
        number_of_tree=to_int(data.get('number_of_tree')),
        hs_code=data.get('hs_code') or None,
        created_by=user_id,
        modified_by=user_id,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )

    db.session.add(farmdata)
    db.session.commit()
    return farmdata


def get_farmdata_by_id(id):
    return FarmData.query.get_or_404(id)


def update_farmdata(farmdata, data, user=None):
    """
    Update FarmData, setting missing optional fields to defaults and handling safe conversions.
    """
    if not farmdata:
        raise ValueError("FarmData object is required.")

    def to_float(value, default=0.0):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def to_int(value, default=0):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    defaults = {
        'land_type': 'unspecified',
        'tilled_land_size': 0.0,
        'planting_date': None,
        'season': 1,
        'quality': 'standard',
        'quantity': 0,
        'harvest_date': None,
        'expected_yield': 0.0,
        'actual_yield': 0.0,
        'channel_partner': 'unspecified',
        'destination_country': 'unspecified',
        'customer_name': 'unspecified',
        'number_of_tree': 0,
        'hs_code': None
    }

    # Fill defaults for missing fields
    for key, default_value in defaults.items():
        if key not in data or str(data[key]).strip() == '':
            data[key] = default_value

    # Convert specific fields safely
    data['tilled_land_size'] = to_float(data.get('tilled_land_size'))
    data['season'] = to_int(data.get('season'), 1)
    data['quantity'] = to_int(data.get('quantity'))
    data['expected_yield'] = to_float(data.get('expected_yield'))
    data['actual_yield'] = to_float(data.get('actual_yield'))
    data['number_of_tree'] = to_int(data.get('number_of_tree'), 0)

    # Ne pas écraser les champs sensibles ou générés automatiquement
    protected_fields = ['id', 'timestamp', 'date_created', 'created_by']
    for key, value in data.items():
        if key not in protected_fields and hasattr(farmdata, key):
            setattr(farmdata, key, value)

    farmdata.modified_by = user.id if user else current_user.id
    farmdata.date_updated = datetime.utcnow()
    db.session.commit()
    return farmdata



def delete_farmdata(farmdata_id):
    farmdata = FarmData.query.get(farmdata_id)
    if farmdata:
        db.session.delete(farmdata)
        db.session.commit()
    else:
        raise ValueError(f"FarmData ID {farmdata_id} does not exist.")
