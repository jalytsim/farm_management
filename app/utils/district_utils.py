from datetime import datetime
from flask_login import current_user
from app import db
from app.models import District


def create_district(name, region):
    new_district = District(
        name=name,
        region=region,
        created_by=current_user.id,
        modified_by=current_user.id,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )
    db.session.add(new_district)
    db.session.commit()
    return new_district


def get_all_districts():
    return District.query.all()


def get_district_by_id(district_id):
    return District.query.get_or_404(district_id)


def update_district(district_id, name, region):
    district = get_district_by_id(district_id)
    if not district:
        raise ValueError(f"District ID {district_id} does not exist.")
    
    district.name = name
    district.region = region
    district.modified_by = current_user.id
    district.date_updated = datetime.utcnow()
    db.session.commit()
    return district


def delete_district(district_id):
    district = get_district_by_id(district_id)
    if district:
        db.session.delete(district)
        db.session.commit()
    else:
        raise ValueError(f"District ID {district_id} does not exist.")
