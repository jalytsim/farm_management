from app.models import Farm, FarmData, District, FarmerGroup
from app import db

def get_farmProperties(farm_id):
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


def get_all_farms():
    return db.session.query(Farm).join(District).join(FarmerGroup).add_columns(
        Farm.id, Farm.name, Farm.geolocation, Farm.district_id, Farm.farmergroup_id,
        District.name.label('district_name'), FarmerGroup.name.label('farmergroup_name')
    ).all()


def create_farm(farm_id, name, subcounty, farmergroup_id, district_id, geolocation):
    farm = Farm(farm_id=farm_id, name=name, subcounty=subcounty, farmergroup_id=farmergroup_id, district_id=district_id, geolocation=geolocation)
    db.session.add(farm)
    db.session.commit()
    return farm

def update_farm(farm, farm_id, name, subcounty, farmergroup_id, district_id, geolocation):
    farm.farm_id = farm_id
    farm.name = name
    farm.subcounty = subcounty
    farm.farmergroup_id = farmergroup_id
    farm.district_id = district_id
    farm.geolocation = geolocation
    db.session.commit()

def delete_farm(farm):
    db.session.delete(farm)
    db.session.commit()