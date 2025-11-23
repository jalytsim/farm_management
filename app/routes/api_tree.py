# app/routes/api_tree.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func
from app.models import Tree, Point, Forest, User, db
from datetime import datetime

bp = Blueprint('api_tree', __name__, url_prefix='/api/tree')

@bp.route('/', methods=['GET'])
@jwt_required()
def list_trees():
    """Liste tous les arbres avec pagination"""
    identity = get_jwt_identity()
    user_id = identity['id']
    page = request.args.get('page', 1, type=int)
    forest_id = request.args.get('forest_id', type=int)
    
    user = User.query.get(user_id)
    
    # Base query
    query = Tree.query
    
    # Filter by forest if specified
    if forest_id:
        query = query.filter_by(forest_id=forest_id)
    
    # Filter by user if not admin
    if not user.is_admin:
        query = query.filter_by(created_by=user_id)
    
    trees = query.paginate(page=page, per_page=10)
    
    trees_json = []
    for tree in trees.items:
        point = Point.query.get(tree.point_id)
        forest = Forest.query.get(tree.forest_id)
        trees_json.append({
            'id': tree.id,
            'name': tree.name,
            'type': tree.type,
            'height': tree.height,
            'diameter': tree.diameter,
            'date_planted': tree.date_planted.isoformat() if tree.date_planted else None,
            'date_cut': tree.date_cut.isoformat() if tree.date_cut else None,
            'forest_id': tree.forest_id,
            'forest_name': forest.name if forest else None,
            'point_id': tree.point_id,
            'point': {
                'latitude': point.latitude,
                'longitude': point.longitude
            } if point else None,
            'created_by': tree.created_by,
            'date_created': tree.date_created.isoformat() if tree.date_created else None,
            'date_updated': tree.date_updated.isoformat() if tree.date_updated else None
        })
    
    return jsonify({
        'trees': trees_json,
        'total_pages': trees.pages,
        'current_page': trees.page,
        'total_trees': trees.total
    })

@bp.route('/<int:tree_id>', methods=['GET'])
@jwt_required()
def get_tree(tree_id):
    """Récupère un arbre par ID"""
    tree = Tree.query.get_or_404(tree_id)
    point = Point.query.get(tree.point_id)
    forest = Forest.query.get(tree.forest_id)
    
    return jsonify({
        'id': tree.id,
        'name': tree.name,
        'type': tree.type,
        'height': tree.height,
        'diameter': tree.diameter,
        'date_planted': tree.date_planted.isoformat() if tree.date_planted else None,
        'date_cut': tree.date_cut.isoformat() if tree.date_cut else None,
        'forest_id': tree.forest_id,
        'forest_name': forest.name if forest else None,
        'point_id': tree.point_id,
        'point': {
            'latitude': point.latitude,
            'longitude': point.longitude
        } if point else None,
        'created_by': tree.created_by,
        'date_created': tree.date_created.isoformat() if tree.date_created else None
    })

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_tree():
    """Créer un nouvel arbre avec son point géographique"""
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)
    
    data = request.json
    
    # Validation
    required_fields = ['name', 'forest_id', 'latitude', 'longitude', 'height', 'diameter', 'date_planted']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    # Vérifier que la forêt existe
    forest = Forest.query.get(data['forest_id'])
    if not forest:
        return jsonify({'error': 'Forest not found'}), 404
    
    try:
        # 1. Créer le point géographique
        point = Point(
            longitude=float(data['longitude']),
            latitude=float(data['latitude']),
            owner_type='tree',
            owner_id=None,  # Sera mis à jour après
            district_id=data.get('district_id'),
            created_by=user_id,
            modified_by=user_id
        )
        db.session.add(point)
        db.session.flush()  # Pour obtenir l'ID du point
        
        # 2. Créer l'arbre
        tree = Tree(
            name=data['name'],
            type=data.get('type', ''),
            height=float(data['height']),
            diameter=float(data['diameter']),
            date_planted=datetime.fromisoformat(data['date_planted']),
            date_cut=datetime.fromisoformat(data['date_cut']) if data.get('date_cut') else None,
            forest_id=data['forest_id'],
            point_id=point.id,
            created_by=user_id,
            modified_by=user_id
        )
        db.session.add(tree)
        db.session.flush()
        
        # 3. Mettre à jour owner_id du point
        point.owner_id = str(tree.id)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Tree created successfully',
            'tree_id': tree.id,
            'point_id': point.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:tree_id>', methods=['PUT'])
@jwt_required()
def update_tree(tree_id):
    """Mettre à jour un arbre"""
    identity = get_jwt_identity()
    user_id = identity['id']
    
    tree = Tree.query.get_or_404(tree_id)
    data = request.json
    
    try:
        # Mettre à jour les champs de l'arbre
        if 'name' in data:
            tree.name = data['name']
        if 'type' in data:
            tree.type = data['type']
        if 'height' in data:
            tree.height = float(data['height'])
        if 'diameter' in data:
            tree.diameter = float(data['diameter'])
        if 'date_planted' in data:
            tree.date_planted = datetime.fromisoformat(data['date_planted'])
        if 'date_cut' in data:
            tree.date_cut = datetime.fromisoformat(data['date_cut']) if data['date_cut'] else None
        
        tree.modified_by = user_id
        
        # Mettre à jour le point si latitude/longitude changent
        if 'latitude' in data or 'longitude' in data:
            point = Point.query.get(tree.point_id)
            if point:
                if 'latitude' in data:
                    point.latitude = float(data['latitude'])
                if 'longitude' in data:
                    point.longitude = float(data['longitude'])
                point.modified_by = user_id
        
        db.session.commit()
        
        return jsonify({'message': 'Tree updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:tree_id>', methods=['DELETE'])
@jwt_required()
def delete_tree(tree_id):
    """Supprimer un arbre et son point"""
    tree = Tree.query.get_or_404(tree_id)
    point_id = tree.point_id
    
    try:
        # Supprimer l'arbre
        db.session.delete(tree)
        
        # Supprimer le point associé
        if point_id:
            point = Point.query.get(point_id)
            if point:
                db.session.delete(point)
        
        db.session.commit()
        
        return jsonify({'message': 'Tree deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/forest/<int:forest_id>', methods=['GET'])
@jwt_required()
def get_trees_by_forest(forest_id):
    """Récupère tous les arbres d'une forêt"""
    trees = Tree.query.filter_by(forest_id=forest_id).all()
    
    trees_json = []
    for tree in trees:
        point = Point.query.get(tree.point_id)
        trees_json.append({
            'id': tree.id,
            'name': tree.name,
            'type': tree.type,
            'height': tree.height,
            'diameter': tree.diameter,
            'date_planted': tree.date_planted.isoformat() if tree.date_planted else None,
            'date_cut': tree.date_cut.isoformat() if tree.date_cut else None,
            'point': {
                'latitude': point.latitude,
                'longitude': point.longitude
            } if point else None
        })
    
    return jsonify({'trees': trees_json, 'total': len(trees_json)})

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Statistiques des arbres"""
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)
    
    query = Tree.query
    if not user.is_admin:
        query = query.filter_by(created_by=user_id)
    
    total_trees = query.count()
    avg_height = db.session.query(func.avg(Tree.height)).filter(
        Tree.created_by == user_id if not user.is_admin else True
    ).scalar() or 0
    avg_diameter = db.session.query(func.avg(Tree.diameter)).filter(
        Tree.created_by == user_id if not user.is_admin else True
    ).scalar() or 0
    
    trees_by_forest = db.session.query(
        Forest.name,
        func.count(Tree.id)
    ).join(Tree).group_by(Forest.name).all()
    
    return jsonify({
        'total_trees': total_trees,
        'avg_height': round(float(avg_height), 2),
        'avg_diameter': round(float(avg_diameter), 2),
        'trees_by_forest': [{'forest': name, 'count': count} for name, count in trees_by_forest]
    })