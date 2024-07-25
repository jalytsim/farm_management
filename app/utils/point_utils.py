from datetime import datetime
from flask_login import current_user
from app import db
from app.models import Point, Forest, Farm, District, Tree

def create_point(longitude, latitude, owner_type, district_id, forest_id=None, farmer_id=None, tree_id=None, ):
    if owner_type == 'forest' and forest_id:
        forest = db.session.query(Forest).filter_by(id=forest_id).first()
        if not forest:
            raise ValueError(f'Forest ID {forest_id} does not exist.')
    elif owner_type == 'farmer' and farmer_id:
        farmer = db.session.query(Farm).filter_by(farm_id=farmer_id).first()
        if not farmer:
            raise ValueError(f'Farmer ID {farmer_id} does not exist.')
    elif owner_type == 'tree' and tree_id:
        tree = db.session.query(Tree).filter_by(id=tree_id).first()
        if not tree:
            raise ValueError(f'Tree ID {tree_id} does not exist.')

    point = Point(
        longitude=longitude,
        latitude=latitude,
        owner_type=owner_type,
        forest_id=forest_id,
        farmer_id=farmer_id,
        tree_id=tree_id,
        district_id=district_id,
        created_by=current_user.id,
        modified_by=current_user.id,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )
    db.session.add(point)
    db.session.commit()

def delete_point(point_id):
    point = Point.query.get(point_id)
    if point:
        db.session.delete(point)
        db.session.commit()

def get_all_points():
    return Point.query.all()

def get_point_by_id(point_id):
    return Point.query.get(point_id)

def update_point(point_id, longitude, latitude, owner_type, district_id, forest_id=None, farmer_id=None, tree_id=None):
    point = Point.query.get(point_id)
    if not point:
        raise ValueError(f'Point ID {point_id} does not exist.')

    if owner_type == 'forest' and forest_id:
        forest = db.session.query(Forest).filter_by(id=forest_id).first()
        if not forest:
            raise ValueError(f'Forest ID {forest_id} does not exist.')
    elif owner_type == 'farmer' and farmer_id:
        farmer = db.session.query(Farm).filter_by(farm_id=farmer_id).first()
        if not farmer:
            raise ValueError(f'Farmer ID {farmer_id} does not exist.')
    elif owner_type == 'tree' and tree_id:
        tree = db.session.query(Tree).filter_by(id=tree_id).first()
        if not tree:
            raise ValueError(f'Tree ID {tree_id} does not exist.')

    point.longitude = longitude
    point.latitude = latitude
    point.owner_type = owner_type
    point.forest_id = forest_id
    point.farmer_id = farmer_id
    point.tree_id = tree_id
    point.district_id = district_id
    point.modified_by = current_user.id
    point.date_updated = datetime.utcnow()
    db.session.commit()

def get_point_details(point_id):
    point = db.session.query(Point).filter(Point.id == point_id).first()
    if not point:
        return None

    district = db.session.query(District).filter(District.id == point.district_id).first()
    owner_name = None
    if point.owner_type == 'forest' and point.forest_id:
        owner = db.session.query(Forest).filter(Forest.id == point.forest_id).first()
        owner_name = owner.name if owner else None
    elif point.owner_type == 'farmer' and point.farmer_id:
        owner = db.session.query(Farm).filter(Farm.farm_id == point.farmer_id).first()
        owner_name = owner.name if owner else None
    elif point.owner_type == 'tree' and point.tree_id:
        owner = db.session.query(Tree).filter(Tree.id == point.tree_id).first()
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
            owner = db.session.query(Farm).filter(Farm.farm_id == point.farmer_id).first()
            owner_name = owner.name if owner else None
        elif point.owner_type == 'tree' and point.tree_id:
            owner = db.session.query(Tree).filter(Tree.id == point.tree_id).first()
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

def get_points_by_forest_id(forest_id):
    return db.session.query(Point).filter(Point.forest_id == forest_id).all()

def get_points_by_farm_id(farm_id):
    return db.session.query(Point).filter(Point.farmer_id == farm_id).all()

def get_points_by_tree_id(tree_id):
    return db.session.query(Point).filter(Point.tree_id == tree_id).all()

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
    elif owner_type == 'tree':
        query = query.filter(Point.tree_id == owner_id)
    
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
