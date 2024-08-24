from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import login_required, current_user
from app.models import Point, Forest, Farm, District, User
from app.utils.farm_utils import get_farm_id
from app.utils.point_utils import create_point, delete_point, update_point, get_point_by_id, get_all_points
from app import db

bp = Blueprint('api_points', __name__, url_prefix='/api/points')

@bp.route('/', methods=['GET'])
@jwt_required()
def list_points():
    user_id = get_jwt_identity()  # Retrieve the user ID from the JWT token
    page = request.args.get('page', 1, type=int)
    
    user = User.query.get(user_id)
    if user.is_admin:
        points = Point.query.paginate(page=page, per_page=6)
    else:
        points = Point.query.filter_by(created_by=current_user.id).paginate(page=page, per_page=6)

    points_json = [
        {
            'id': point.id,
            'longitude': point.longitude,
            'latitude': point.latitude,
            'owner_type': point.owner_type,
            'forest_id': point.forest_id,
            'farmer_id': point.farmer_id,
            'district_id': point.district_id,
            'created_by': point.created_by,
            'date_created': point.date_created,
            'date_updated': point.date_updated
        } for point in points.items
    ]
    return jsonify({
        'points': points_json,
        'total_pages': points.pages,
        'current_page': points.page
    })

@bp.route('/<int:point_id>', methods=['GET'])
@jwt_required()
def view_point(point_id):
    point = get_point_by_id(point_id)
    if not point:
        return jsonify({'error': 'Point not found.'}), 404
    point_json = {
        'id': point.id,
        'longitude': point.longitude,
        'latitude': point.latitude,
        'owner_type': point.owner_type,
        'forest_id': point.forest_id,
        'farmer_id': point.farmer_id,
        'district_id': point.district_id,
        'created_by': point.created_by,
        'date_created': point.date_created,
        'date_updated': point.date_updated
    }
    return jsonify(point_json)

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_point_route():

    user_id = get_jwt_identity()
    print(user_id)
    user = User.query.get(user_id)
    data = request.json
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    owner_id = data.get('owner_id')
    owner_type = data.get('owner_type')
    district_id = 5
    
    farm = db.session.query(Farm).filter_by(farm_id=owner_id).first()
    print(farm.farm_id)
    if owner_type == 'tree' :
        tree_id = owner_id
        farmer_id = None
        forest_id = None

    else :    
        if not farm :
            owner_type = 'forest'
            forest_id = owner_id
            farmer_id = None
            tree_id = None
        else :
            owner_type = 'farmer'
            farmer_id = owner_id
            forest_id = None
            tree_id = None
            district_id = farm.district_id
        
    # azo izay ny forest id ny owner type ary ny farm_id

    if not longitude or not latitude or not owner_type:
        return jsonify({'error': 'Longitude, latitude, and owner type are required.'}), 400
    
    try:
        create_point(longitude, latitude, owner_type, district_id, forest_id, farmer_id, tree_id, user)
        return jsonify({'message': 'Point created successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error creating point: {str(e)}'}), 500

@bp.route('/<int:point_id>', methods=['PUT'])
def update_point_route(point_id):
    data = request.json
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    owner_type = data.get('owner_type')
    forest_id = data.get('forest_id')
    farmer_id = data.get('farmer_id')
    district_id = data.get('district_id')

    if not longitude or not latitude or not owner_type:
        return jsonify({'error': 'Longitude, latitude, and owner type are required.'}), 400

    if owner_type == 'forest':
        if forest_id:
            forest = Forest.query.get(forest_id)
            if not forest:
                return jsonify({'error': 'Invalid Forest ID.'}), 400
        else:
            return jsonify({'error': 'Forest ID is required for owner type "forest".'}), 400
        farmer_id = None
    elif owner_type == 'farmer':
        if farmer_id:
            farmer = Farm.query.filter_by(farm_id=farmer_id).first()
            if not farmer:
                return jsonify({'error': 'Invalid Farmer ID.'}), 400
        else:
            return jsonify({'error': 'Farmer ID is required for owner type "farmer".'}), 400
        forest_id = None
    else:
        return jsonify({'error': 'Invalid owner type.'}), 400

    try:
        update_point(point_id, longitude, latitude, owner_type, district_id, forest_id, farmer_id)
        return jsonify({'message': 'Point updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating point: {str(e)}'}), 500

@bp.route('/<int:point_id>', methods=['DELETE'])
def delete_point_route(point_id):
    try:
        delete_point(point_id)
        return jsonify({'message': 'Point deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting point: {str(e)}'}), 500

@bp.route('/getbyownerid/<owner_type>/<owner_id>', methods=['GET'])
@jwt_required()
def get_points_owner_id(owner_type, owner_id):
    user_id = get_jwt_identity()  # Retrieve the user ID from the JWT token

    if owner_type == 'farmer':
        points = Point.query.filter_by(owner_type=owner_type, farmer_id=owner_id).all()
    elif owner_type == 'forest':
        points = Point.query.filter_by(owner_type=owner_type, forest_id=owner_id).all()
    else:
        points = Point.query.filter_by(owner_type=owner_type, tree_id=owner_id).all()

    points_json = [
        {
            'id': point.id,
            'longitude': point.longitude,
            'latitude': point.latitude,
            'owner_type': point.owner_type,
            'forest_id': point.forest_id,
            'farmer_id': point.farmer_id,
            'district_id': point.district_id,
            'created_by': point.created_by,
            'date_created': point.date_created,
            'date_updated': point.date_updated
        } for point in points
    ]
    return jsonify({
        'points': points_json,
    })


@bp.route('/getallbyownertype/<owner_type>', methods=['GET'])
@jwt_required()
def get_all_points_owner_type(owner_type):
    user_id = get_jwt_identity()  # Retrieve the user ID from the JWT token

    # Grouping points by the owner_type, which could be forest_id, farmer_id, or tree_id
    if owner_type == 'forest':
        points = Point.query.filter_by(owner_type=owner_type).group_by(Point.forest_id).all()
    elif owner_type == 'farmer':
        points = Point.query.filter_by(owner_type=owner_type).group_by(Point.farmer_id).all()
    elif owner_type == 'tree':
        points = Point.query.filter_by(owner_type=owner_type).group_by(Point.tree_id).all()
    else:
        return jsonify({'error': 'Invalid owner type'}), 400

    # Organizing the points into polygons by the specified owner_type
    grouped_polygons = {}
    for point in points:
        group_id = getattr(point, f"{owner_type}_id")
        if group_id not in grouped_polygons:
            grouped_polygons[group_id] = {
                'owner_type': owner_type,
                'points': []
            }
        grouped_polygons[group_id]['points'].append({
            'id': point.id,
            'longitude': point.longitude,
            'latitude': point.latitude,
            'forest_id': point.forest_id,
            'farmer_id': point.farmer_id,
            'tree_id': point.tree_id,
            'district_id': point.district_id,
            'created_by': point.created_by,
            'date_created': point.date_created,
            'date_updated': point.date_updated
        })

    # Transforming grouped_polygons into a list of polygons
    polygons_list = [{'owner_type': owner_type, 'points': points['points']} for _, points in grouped_polygons.items()]

    return jsonify({
        'polygons': polygons_list,
    })