from datetime import datetime
from flask_login import current_user
from app import db
from app.models import Farm, FarmData, District, FarmerGroup


def get_farm_properties(farm_id):
    print(farm_id)
    try:
        data = db.session.query(
            Farm.farm_id,
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
        ).join(FarmData, Farm.farm_id == FarmData.farm_id) \
         .join(District, Farm.district_id == District.id) \
         .filter(Farm.farm_id == farm_id).all()

        print(data)
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

def create_farm(user=None, name=None, subcounty=None, farmergroup_id=None, district_id=None, geolocation=None, phonenumber1=None, phonenumber2=None):
    # Check if a user object is provided; otherwise, use the current user's ID from context or global state
    if user:
        user_id = user.id
        user_id_start = user.id_start
    else:
        # Assuming that 'current_user' is a global or context-based object that provides the current user's ID
        from flask_jwt_extended import get_jwt_identity
        from app.models import User

        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found.")
        user_id_start = user.id_start
    
    print('tafiditra utils.create_farm  ')
    print(user_id_start)

    if not user_id_start:
        raise ValueError("User's id_start is not set.")

    # Construct the base of the farm_id
    base_farm_id = f"{user_id_start}FA"

    # Query the database for the latest farm_id with the same base
    last_farm = Farm.query.filter(Farm.farm_id.like(f"{base_farm_id}%")).order_by(Farm.farm_id.desc()).first()
    print(last_farm)

    if last_farm:
        # Extract the last numeric part of the farm_id and increment it
        last_number = int(last_farm.farm_id.replace(base_farm_id, ""))
        new_number = last_number + 1
        print(new_number)
    else:
        # Start with 1 if no previous farm_id exists
        new_number = 1
    # Ensure the number is 4 digits long
    farm_id = f"{base_farm_id}{str(new_number).zfill(4)}"
    print(farm_id)

    # Create the new farm
    farm = Farm(
        farm_id=farm_id,
        name=name,
        subcounty=subcounty,
        farmergroup_id=farmergroup_id,
        district_id=district_id,
        geolocation=geolocation,
        phonenumber=phonenumber1,
        phonenumber2=phonenumber2,
        created_by=user_id,  # Use the resolved user_id
        modified_by=user_id,  # Use the resolved user_id
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
    print(farm)
    if farm:
        db.session.delete(farm)
        db.session.commit()
    else:
        raise ValueError(f"Farm ID {farm_id} does not exist.")
