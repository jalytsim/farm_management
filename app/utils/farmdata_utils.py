from app import db
from app.models import FarmData

def create_farmdata(data):
    farmdata = FarmData(**data)
    db.session.add(farmdata)
    db.session.commit()
    return farmdata

def get_farmdata_by_id(id):
    return FarmData.query.get_or_404(id)

def update_farmdata(farmdata, data):
    for key, value in data.items():
        setattr(farmdata, key, value)
    db.session.commit()
    return farmdata

def delete_farmdata(farmdata):
    db.session.delete(farmdata)
    db.session.commit()
