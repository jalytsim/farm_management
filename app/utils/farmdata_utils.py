from datetime import datetime
from flask_login import current_user
from app import db
from app.models import FarmData


def create_farmdata(data):
    farmdata = FarmData(
        **data,
        created_by=current_user.id,
        modified_by=current_user.id,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )
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
