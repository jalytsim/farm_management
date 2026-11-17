import gzip
import json

from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import current_user
from sqlalchemy import func
from app.models import Point, User
from app.utils.point_utils import create_point, delete_point, delete_point_by_owner, update_point, get_point_by_id
from app import db
from app.utils import map_cache

bp = Blueprint('api_points', __name__, url_prefix='/api/points')

@bp.route('/', methods=['GET'])
@jwt_required()
def list_points():
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id'] 
      # Retrieve the user ID from the JWT token
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
            'owner_id': point.owner_id,
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
    return jsonify({
        'id': point.id,
        'longitude': point.longitude,
        'latitude': point.latitude,
        'owner_type': point.owner_type,
        'owner_id': point.owner_id,
        'district_id': point.district_id,
        'created_by': point.created_by,
        'date_created': point.date_created,
        'date_updated': point.date_updated
    })

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_new_point():
    data = request.json
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    owner_type = data.get('owner_type')
    district_id = data.get('district_id')
    owner_id = data.get('owner_id')
    forest_id, farmer_id, tree_id = None, None, None
    if owner_type == 'forest':
        forest_id = owner_id
    elif owner_type == 'farmer':
        farmer_id = owner_id
    elif owner_type == 'tree':
        tree_id = owner_id
    else:
        return jsonify({'error': f'Invalid owner type: {owner_type}'}), 400

    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id']   # Retrieve the user ID from the JWT token
    user = User.query.get(user_id)

    try:
        create_point(
            longitude=longitude,
            latitude=latitude,
            owner_type=owner_type,
            district_id=district_id,
            forest_id=forest_id,
            farmer_id=farmer_id,
            tree_id=tree_id,
            user=user
        )
        return jsonify({'message': 'Point created successfully.'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:point_id>', methods=['DELETE'])
@jwt_required()
def delete_point_route(point_id):
    try:
        delete_point(point_id)
        return jsonify({'message': 'Point deleted successfully.'}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@bp.route('/owner/<string:owner_id>', methods=['DELETE'])
@jwt_required()
def delete_point_by_owner_route(owner_id):
    try:
        message = delete_point_by_owner(owner_id)  # Call the function to delete points by owner_id
        return jsonify({'message': message}), 204 if "Deleted" in message else 404  # Return 204 if deleted, 404 if no points found
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:point_id>', methods=['PUT'])
@jwt_required()
def update_point_route(point_id):
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id']   # Retrieve the user ID from the JWT token
    user = User.query.get(user_id)
    data = request.json
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    owner_type = data.get('owner_type')
    owner_id = data.get('owner_id')
    district_id = data.get('district_id')
    forest_id, farmer_id, tree_id = None, None, None
    if owner_type == 'forest':
        forest_id = owner_id
    elif owner_type == 'farmer':
        farmer_id = owner_id
    elif owner_type == 'tree':
        tree_id = owner_id
    else:
        return jsonify({'error': f'Invalid owner type: {owner_type}'}), 400

    try:
        update_point(
            point_id=point_id,
            longitude=longitude,
            latitude=latitude,
            owner_type=owner_type,
            district_id=district_id,
            forest_id=forest_id,
            farmer_id=farmer_id,
            tree_id=tree_id,
            user=user
        )
        return jsonify({'message': 'Point updated successfully.'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

def _gzip_json_response(blob):
    """blob = JSON déjà compressé gzip ; décompressé seulement si le client ne gère pas gzip."""
    if 'gzip' in request.headers.get('Accept-Encoding', '').lower():
        resp = make_response(blob)
        resp.headers['Content-Encoding'] = 'gzip'
    else:
        resp = make_response(gzip.decompress(blob))
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Cache-Control'] = 'private, no-cache'
    resp.headers['Vary'] = 'Accept-Encoding'
    return resp


@bp.route('/map/<owner_type>/centroids', methods=['GET'])
@jwt_required()
def map_centroids(owner_type):
    """Un point + une surface par ferme/forêt : {count, total_area_m2, ids, coords, areas}."""
    if owner_type not in ('farmer', 'forest', 'tree'):
        return jsonify({'error': 'invalid owner_type'}), 400
    user = User.query.get(get_jwt_identity()['id'])
    return _gzip_json_response(map_cache.centroids_gz(db, owner_type, user))


@bp.route('/map/<owner_type>/polygons', methods=['GET'])
@jwt_required()
def map_polygons(owner_type):
    """Contours GeoJSON des entités visibles : ?bbox=ouest,sud,est,nord."""
    if owner_type not in ('farmer', 'forest', 'tree'):
        return jsonify({'error': 'invalid owner_type'}), 400
    try:
        west, south, east, north = (float(v) for v in request.args.get('bbox', '').split(','))
    except ValueError:
        return jsonify({'error': 'bbox=west,south,east,north required'}), 400
    user = User.query.get(get_jwt_identity()['id'])
    geojson, n = map_cache.polygons_in_bbox(db, owner_type, user, west, south, east, north)
    if geojson is None:
        return jsonify({'too_many': True, 'count': n, 'limit': map_cache.MAX_BBOX_ENTITIES})
    geojson['count'] = n
    return _gzip_json_response(gzip.compress(json.dumps(geojson, separators=(',', ':')).encode(), 5))


@bp.route('/getallbyownertype/<owner_type>', methods=['GET'])
@jwt_required()
def get_all_points_owner_type(owner_type):
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id']   # Retrieve the user ID from the JWT token
    user = User.query.get(user_id)
    if user.is_admin:
        points = db.session.query(Point).filter_by(owner_type=owner_type).all()
    else:
        points = Point.query.filter_by(created_by=user.id, owner_type=owner_type).all()
    # Fetch all points for the given owner_type
    # Group points by owner_id
    grouped_polygons = {}
    for point in points:
        group_id = point.owner_id
        if group_id not in grouped_polygons:
            grouped_polygons[group_id] = {
                'owner_id': group_id,
                'owner_type': owner_type,
                'points': []
            }
        grouped_polygons[group_id]['points'].append({
            'longitude': point.longitude,
            'latitude': point.latitude,
            'id': point.id,
            'district_id': point.district_id,
            'created_by': point.created_by,
            'date_created': point.date_created,
            'date_updated': point.date_updated
        })

    # Transform grouped_polygons into a list of polygons
    polygons_list = [{'owner_id': points['owner_id'], 'owner_type': points['owner_type'], 'points': points['points']} for _, points in grouped_polygons.items()]

    return jsonify({
        'polygons': polygons_list,
    })
@bp.route('/getbyownerid/<owner_type>/<owner_id>', methods=['GET'])
@jwt_required()
def get_points_owner_id(owner_type, owner_id):
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id']   # Retrieve the user ID from the JWT token

    points = Point.query.filter_by(owner_type=owner_type, owner_id=owner_id).all()
    points_json = [
        {
            'id': point.id,
            'longitude': point.longitude,
            'latitude': point.latitude,
            'owner_type': point.owner_type,
            'owner_id': point.owner_id,
            'district_id': point.district_id,
            'created_by': point.created_by,
            'date_created': point.date_created,
            'date_updated': point.date_updated
        } for point in points
    ]
    return jsonify({
        'points': points_json,
    })

# New endpoint to check if points exist for a given owner_id
@bp.route('/exists/<owner_type>/<owner_id>', methods=['GET'])
@jwt_required()
def check_points_exists(owner_type, owner_id):
    # Validate owner_type
    if owner_type not in ['forest', 'farmer', 'tree']:
        return jsonify({'error': 'Invalid owner type.'}), 400

    # Query to check if points exist for the given owner_type and owner_id
    points = Point.query.filter_by(owner_type=owner_type, owner_id=owner_id).first()
    exists = points is not None

    return jsonify({'exists': exists})
