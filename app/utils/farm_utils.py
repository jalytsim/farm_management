from datetime import datetime
from flask_login import current_user
from app import db
from app.models import Farm, FarmData, District, FarmerGroup


def get_farm_properties(farm_id):
    print(farm_id)
    try:
        data = db.session.query(
            Farm.id.label('farm_id'),
            Farm.farmergroup_id,
            Farm.geolocation,
            Farm.district_id,
            FarmData.crop_id,
            FarmData.tilled_land_size,
            FarmData.season,
            FarmData.quality,
            FarmData.quantity.label('produce_weight'),
            FarmData.harvest_date,
            FarmData.timestamp,
            FarmData.channel_partner,
            FarmData.destination_country,
            FarmData.customer_name,
            District.name.label('district_name'),
            District.region.label('district_region')
        ).join(FarmData, Farm.id == FarmData.farm_id) \
         .join(District, Farm.district_id == District.id) \
         .filter(Farm.id == farm_id).all()

        return data

    except Exception as e:
        print(f"Error fetching farm properties: {e}")
        return None


def get_farm_id(farm_id):
    try:
        data = db.session.query(Farm.farm_id).filter(Farm.id == farm_id).all()
        return data
    except Exception as e:
        print(f"Error fetching farm properties: {e}")
        return None


def get_all_farms():
    return db.session.query(Farm).join(District).join(FarmerGroup).add_columns(
        Farm.id, Farm.name, Farm.geolocation, Farm.district_id, Farm.farmergroup_id,
        District.name.label('district_name'), FarmerGroup.name.label('farmergroup_name')
    ).all()


def create_farm(farm_id, name, subcounty, farmergroup_id, district_id, geolocation, phonenumber1=None, phonenumber2=None):
    farm = Farm(
        farm_id=farm_id,
        name=name,
        subcounty=subcounty,
        farmergroup_id=farmergroup_id,
        district_id=district_id,
        geolocation=geolocation,
        phonenumber=phonenumber1,
        phonenumber2=phonenumber2,
        created_by=current_user.id,
        modified_by=current_user.id,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )
    db.session.add(farm)
    db.session.commit()
    return farm


def update_farm(farm_id, name, subcounty, farmergroup_id, district_id, geolocation, phonenumber1, phonenumber2=None):
    farm = db.session.query(Farm).get(farm_id)
    if farm:
        farm.name = name
        farm.subcounty = subcounty
        farm.farmergroup_id = farmergroup_id
        farm.district_id = district_id
        farm.geolocation = geolocation
        farm.phonenumber = phonenumber1
        farm.phonenumber2 = phonenumber2 if phonenumber2 else None
        farm.modified_by = current_user.id
        farm.date_updated = datetime.utcnow()
        db.session.commit()
    else:
        raise ValueError(f"Farm ID {farm_id} does not exist.")


def delete_farm(farm_id):
    farm = db.session.query(Farm).get(farm_id)
    if farm:
        db.session.delete(farm)
        db.session.commit()
    else:
        raise ValueError(f"Farm ID {farm_id} does not exist.")
