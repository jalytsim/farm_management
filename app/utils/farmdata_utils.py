# app/utils/farmdata_utils.py
from app import db
from app.models import FarmData

def get_all_farmdata():
    return FarmData.query.all()

def create_farmdata(data):
    new_farmdata = FarmData(**data)
    db.session.add(new_farmdata)
    db.session.commit()
    return new_farmdata

def get_farmdata_by_id(farmdata_id):
    return FarmData.query.get_or_404(farmdata_id)

def update_farmdata(farmdata, data):
    for key, value in data.items():
        setattr(farmdata, key, value)
    db.session.commit()
    return farmdata

def delete_farmdata(farmdata):
    db.session.delete(farmdata)
    db.session.commit()
