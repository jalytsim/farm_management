from app import db
from app.models import District

def create_district(name, region):
    new_district = District(name=name, region=region)
    db.session.add(new_district)
    db.session.commit()
    return new_district

def get_all_districts():
    return District.query.all()

def get_district_by_id(district_id):
    return District.query.get_or_404(district_id)

def update_district(district_id, name, region):
    district = get_district_by_id(district_id)
    district.name = name
    district.region = region
    db.session.commit()
    return district

def delete_district(district_id):
    district = get_district_by_id(district_id)
    db.session.delete(district)
    db.session.commit()
