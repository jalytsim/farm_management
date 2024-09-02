from datetime import datetime
from flask_login import current_user
from app import db
from app.models import Point, Forest, Farm, District, Tree
from sqlalchemy.exc import IntegrityError


def create_point(longitude, latitude, owner_type, district_id=None, forest_id=None, farmer_id=None, tree_id=None, user=None):
    # Validate the owner_type and owner_id
    print(longitude, latitude, owner_type, district_id, forest_id, farmer_id)

    if owner_type == 'forest':
        owner = db.session.query(Forest).filter_by(id=forest_id).first()
        if not owner:
            raise ValueError(f'Forest ID {forest_id} does not exist.')
    elif owner_type == 'farmer':
        owner = db.session.query(Farm).filter_by(farm_id=farmer_id).first()
        if not owner:
            raise ValueError(f'Farmer ID {farmer_id} does not exist.')
    elif owner_type == 'tree':
        owner = db.session.query(Tree).filter_by(id=tree_id).first()
        if not owner:
            raise ValueError(f'Tree ID {tree_id} does not exist.')
    else:
        raise ValueError(f'Invalid owner type: {owner_type}')

    # Determine the user creating the point
    user_id = user.id if user else current_user.id

    # Check if the point already exists
    existing_point = db.session.query(Point).filter_by(
        longitude=longitude,
        latitude=latitude,
        owner_type=owner_type,
        owner_id=forest_id if owner_type == 'forest' else (farmer_id if owner_type == 'farmer' else tree_id),
        district_id=district_id
    ).first()

    if existing_point:
        raise ValueError(f'Point at longitude {longitude} and latitude {latitude} already exists.')

    # Create the point
    point = Point(
        longitude=longitude,
        latitude=latitude,
        owner_type=owner_type,
        owner_id=forest_id if owner_type == 'forest' else (farmer_id if owner_type == 'farmer' else tree_id),
        district_id=district_id,
        created_by=user_id,
        modified_by=user_id,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )

    try:
        db.session.add(point)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f'Error creating point: {str(e)}')

    return point

def delete_point(point_id):
    point = Point.query.get(point_id)
    if point:
        db.session.delete(point)
        db.session.commit()

def get_all_points():
    return Point.query.all()

def get_point_by_id(point_id):
    return Point.query.get(point_id)

def update_point(point_id, longitude, latitude, owner_type, district_id, forest_id=None, farmer_id=None, tree_id=None, user=None):
    # Retrieve the point by ID
    point = Point.query.get(point_id)
    user_id = user.id if user else current_user.id
    if not point:
        raise ValueError(f'Point ID {point_id} does not exist.')

    # Validate the owner_type and owner_id
    if owner_type == 'forest':
        owner = db.session.query(Forest).filter_by(id=forest_id).first()
        if not owner:
            raise ValueError(f'Forest ID {forest_id} does not exist.')
    elif owner_type == 'farmer':
        owner = db.session.query(Farm).filter_by(farm_id=farmer_id).first()
        if not owner:
            raise ValueError(f'Farmer ID {farmer_id} does not exist.')
    elif owner_type == 'tree':
        owner = db.session.query(Tree).filter_by(id=tree_id).first()
        if not owner:
            raise ValueError(f'Tree ID {tree_id} does not exist.')
    else:
        raise ValueError(f'Invalid owner type: {owner_type}')

    # Update the point fields
    point.longitude = longitude
    point.latitude = latitude
    point.owner_type = owner_type
    point.owner_id = forest_id if owner_type == 'forest' else (farmer_id if owner_type == 'farmer' else tree_id)
    point.district_id = district_id
    point.modified_by = user_id
    point.date_updated = datetime.utcnow()

    # Commit the changes to the database
    db.session.commit()

def get_point_details(point_id):
    point = db.session.query(Point).filter(Point.id == point_id).first()
    if not point:
        return None

    district = db.session.query(District).filter(District.id == point.district_id).first()
    owner_name = None
    if point.owner_type == 'forest':
        owner = db.session.query(Forest).filter(Forest.id == point.owner_id).first()
        owner_name = owner.name if owner else None
    elif point.owner_type == 'farmer':
        owner = db.session.query(Farm).filter(Farm.farm_id == point.owner_id).first()
        owner_name = owner.name if owner else None
    elif point.owner_type == 'tree':
        owner = db.session.query(Tree).filter(Tree.id == point.owner_id).first()
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
        if point.owner_type == 'forest':
            owner = db.session.query(Forest).filter(Forest.id == point.owner_id).first()
            owner_name = owner.name if owner else None
        elif point.owner_type == 'farmer':
            owner = db.session.query(Farm).filter(Farm.farm_id == point.owner_id).first()
            owner_name = owner.name if owner else None
        elif point.owner_type == 'tree':
            owner = db.session.query(Tree).filter(Tree.id == point.owner_id).first()
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

def get_points_by_owner(owner_id, owner_type):
    return db.session.query(Point).filter(Point.owner_id == owner_id, Point.owner_type == owner_type).all()

def get_points_by_forest_id(forest_id):
    return db.session.query(Point).filter(Point.owner_id == forest_id, Point.owner_type == 'forest').all()

def get_points_by_farm_id(farm_id):
    return db.session.query(Point).filter(Point.owner_id == farm_id, Point.owner_type == 'farmer').all()

def get_points_by_tree_id(tree_id):
    return db.session.query(Point).filter(Point.owner_id == tree_id, Point.owner_type == 'tree').all()

def point_exists(longitude, latitude, district_id, owner_type, owner_id):
    query = db.session.query(Point).filter(
        Point.longitude == longitude,
        Point.latitude == latitude,
        Point.district_id == district_id,
        Point.owner_type == owner_type
    )
    if owner_type == 'forest':
        query = query.filter(Point.owner_id == owner_id)
    elif owner_type == 'farmer':
        query = query.filter(Point.owner_id == owner_id)
    elif owner_type == 'tree':
        query = query.filter(Point.owner_id == owner_id)
    
    return db.session.query(query.exists()).scalar()

def calculate_area(vertices):
    n = len(vertices)
    area = 0.0

    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]

    area = abs(area) / 2.0
    return area
