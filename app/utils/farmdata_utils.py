from datetime import datetime
from flask_login import current_user
from app import db
from app.models import FarmData



def create_farmdata(data, user=None):
    """
    Create a FarmData record. Validates required fields and populates defaults for missing optional fields.

    :param data: dict with keys for FarmData fields.
    :param user: optional User object; if omitted, uses current_user.
    :return: FarmData instance
    :raises: ValueError if any required field is missing or invalid
    """
    # Determine user ID
    user_id = user.id if user else current_user.id

    # Required fields
    required = ['farm_id', 'crop_id', 'planting_date']
    missing = [f for f in required if f not in data or data[f] is None]
    if missing:
        raise ValueError(f"Missing required farmdata field(s): {', '.join(missing)}")

    # Default values for non-nullable fields if not provided
    defaults = {
        'land_type': 'unspecified',
        'tilled_land_size': 0.0,
        'season': 1,
        'quality': 'standard',
        'quantity': 0,
        'harvest_date': data.get('planting_date'),
        'expected_yield': 0.0,
        'actual_yield': 0.0,
        'channel_partner': 'unspecified',
        'destination_country': 'unspecified',
        'customer_name': 'unspecified',
        # optional fields
        'number_of_tree': None,
        'hs_code': None,
    }

    # Merge defaults for missing optional fields
    for key, val in defaults.items():
        data.setdefault(key, val)

    # Always set metadata timestamps and user tracking
    data.update({
        'created_by': user_id,
        'modified_by': user_id,
        'date_created': datetime.utcnow(),
        'date_updated': datetime.utcnow(),
        'timestamp': datetime.utcnow(),
    })

    # Construct and save the FarmData
    farmdata = FarmData(**data)
    db.session.add(farmdata)
    db.session.commit()
    return farmdata


def get_farmdata_by_id(id):
    return FarmData.query.get_or_404(id)


def update_farmdata(farmdata_id, data):
    farmdata = FarmData.query.get(farmdata_id)
    if not farmdata:
        raise ValueError(f"FarmData ID {farmdata_id} does not exist.")
    
    for key, value in data.items():
        setattr(farmdata, key, value)
    farmdata.modified_by = current_user.id
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
