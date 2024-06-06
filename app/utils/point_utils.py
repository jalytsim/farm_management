from app.models import Farm, District, Forest, Point
from ..models import db, FarmData, Farm, District, SoilData

def create_point(longitude, latitude, district_id, owner_type, owner_id):
    new_point = Point(
        longitude=longitude, 
        latitude=latitude, 
        district_id=district_id, 
        owner_type=owner_type, 
        owner_id=owner_id
    )
    db.session.add(new_point)
    db.session.commit()

def update_point(id, longitude, latitude, district_id, owner_type, owner_id):
    point = db.session.query(Point).get(id)
    if point:
        point.longitude = longitude
        point.latitude = latitude
        point.district_id = district_id
        point.owner_type = owner_type
        point.owner_id = owner_id
        db.session.commit()

def delete_point(id):
    point = db.session.query(Point).get(id)
    if point:
        db.session.delete(point)
        db.session.commit()
        
def get_pointDetails(point_id):
    point = db.session.query(Point).filter(Point.id == point_id).first()
    if not point:
        return None

    district = db.session.query(District).filter(District.id == point.district_id).first()
    owner_name = None
    if point.owner_type == 'forest' and point.forest_id:
        owner = db.session.query(Forest).filter(Forest.id == point.forest_id).first()
        owner_name = owner.name if owner else None
    elif point.owner_type == 'farmer' and point.farmer_id:
        owner = db.session.query(Farm).filter(Farm.id == point.farmer_id).first()
        owner_name = owner.name if owner else None

    return {
        'point_id': point.id,
        'longitude': point.longitude,
        'latitude': point.latitude,
        'district_id': point.district_id,
        'owner_type': point.owner_type,
        'owner_name': owner_name,
        'district_name': district.name if district else None,
        'district_region': district.region if district else None
    }


def get_all_points_other():
    points = db.session.query(Point).all()
    all_points_details = []

    for point in points:
        district = db.session.query(District).filter(District.id == point.district_id).first()
        owner_name = None
        if point.owner_type == 'forest' and point.forest_id:
            owner = db.session.query(Forest).filter(Forest.id == point.forest_id).first()
            owner_name = owner.name if owner else None
        elif point.owner_type == 'farmer' and point.farmer_id:
            owner = db.session.query(Farm).filter(Farm.id == point.farmer_id).first()
            owner_name = owner.name if owner else None

        point_details = {
            'point_id': point.id,
            'longitude': point.longitude,
            'latitude': point.latitude,
            'district_id': point.district_id,
            'owner_type': point.owner_type,
            'owner_name': owner_name,
            'district_name': district.name if district else None,
            'district_region': district.region if district else None
        }

        all_points_details.append(point_details)

    return all_points_details



def get_all_points():
    return db.session.query(Point).all()

def get_points_by_forest_id(forest_id):
    return db.session.query(Point).filter(Point.forest_id == forest_id).all()

def get_points_by_farm_id(farm_id):
    return db.session.query(Point).filter(Point.farmer_id == farm_id).all()

def point_exists(longitude, latitude, district_id, owner_type, owner_id):
    query = db.session.query(Point).filter(
        Point.longitude == longitude,
        Point.latitude == latitude,
        Point.district_id == district_id,
        Point.owner_type == owner_type
    )
    if owner_type == 'forest':
        query = query.filter(Point.forest_id == owner_id)
    elif owner_type == 'farmer':
        query = query.filter(Point.farmer_id == owner_id)
    
    return db.session.query(query.exists()).scalar()

