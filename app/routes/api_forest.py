import os
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Forest, User
from app.utils import forest_utils
from werkzeug.utils import secure_filename

import logging

bp = Blueprint('api_forest', __name__, url_prefix='/api/forest')

UPLOAD_FOLDER = 'static/uploads'  # Define your upload folder
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
@jwt_required()
def index():
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id']     
    page = request.args.get('page', 1, type=int)
    
    user = User.query.get(user_id)
    if user.is_admin:
        forests = Forest.query.paginate(page=page, per_page=6)
    else:
        forests = Forest.query.filter_by(created_by=user_id).paginate(page=page, per_page=6)

    forests_list = [{
        "id": forest.id,
        "name": forest.name,
        "tree_type": forest.tree_type,
    } for forest in forests.items]
    
    return jsonify(
        forests=forests_list,
        total_pages=forests.pages,  # Return the total number of pages
        current_page=forests.page,  # Return the current page
    )


@bp.route('/create', methods=['POST'])
@jwt_required()
def create_forest():
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id'] 

    user = User.query.get(user_id)
    print(user_id)
    
    if not user or not user.id_start:
        return jsonify({"msg": "User id_start is not defined"}), 400
    
    name = request.form.get('name')
    tree_type = request.form.get('tree_type')
    file = request.files.get('image')

    if not name or not tree_type:
        return jsonify({"msg": "Name and Tree Type are required"}), 400

    filename = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Create the upload folder if it doesn't exist
        upload_dir = os.path.join(UPLOAD_FOLDER)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

    try:
        # Use the forest_utils.create_forest function
        new_forest = forest_utils.create_forest(
            name=name,
            tree_type=tree_type,
            user=user  # Pass the user object to the utility function
        )
        return jsonify(success=True, forest_id=new_forest.id)
    except Exception as e:
        logging.error(f"Error creating forest: {e}")
        return jsonify({"msg": "Error creating forest"}), 500
    
@bp.route('/bulk-create', methods=['POST'])
@jwt_required()
def bulk_create_forests():
    identity = get_jwt_identity()
    user_id = identity['id']
    user = User.query.get(user_id)
    
    if not user or not user.id_start:
        return jsonify({"msg": "User id_start is not defined"}), 400
    
    if 'file' not in request.files:
        return jsonify({"msg": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"msg": "No file selected"}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({"msg": "File must be a CSV"}), 400
    
    try:
        import csv
        import io
        
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        # Validate headers
        required_headers = {'name', 'tree_type'}
        headers = set(csv_reader.fieldnames or [])
        
        if not required_headers.issubset(headers):
            missing = required_headers - headers
            return jsonify({
                "msg": f"Missing required columns: {', '.join(missing)}"
            }), 400
        
        results = {
            'success': 0,
            'errors': 0,
            'skipped': 0,
            'details': []
        }
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                name = row.get('name', '').strip()
                tree_type = row.get('tree_type', '').strip()
                
                if not name or not tree_type:
                    results['errors'] += 1
                    results['details'].append({
                        'row': row_num,
                        'name': name or 'N/A',
                        'error': 'Name and tree_type are required'
                    })
                    continue
                
                # ✅ VÉRIFICATION DES DOUBLONS - name + tree_type + created_by
                existing_forest = Forest.query.filter_by(
                    name=name,
                    tree_type=tree_type,  # ✅ Ajouté
                    created_by=user_id
                ).first()
                
                if existing_forest:
                    results['skipped'] += 1
                    results['details'].append({
                        'row': row_num,
                        'name': name,
                        'tree_type': tree_type,
                        'forest_id': existing_forest.id,
                        'status': 'skipped',
                        'reason': f'Forest "{name}" with tree type "{tree_type}" already exists'
                    })
                    continue
                
                # Créer la forêt si elle n'existe pas
                new_forest = forest_utils.create_forest(
                    name=name,
                    tree_type=tree_type,
                    user=user
                )
                
                results['success'] += 1
                results['details'].append({
                    'row': row_num,
                    'forest_id': new_forest.id,
                    'name': new_forest.name,
                    'tree_type': new_forest.tree_type,
                    'status': 'created'
                })
                
            except Exception as e:
                results['errors'] += 1
                results['details'].append({
                    'row': row_num,
                    'name': name if 'name' in locals() else 'N/A',
                    'error': str(e)
                })
        
        return jsonify(results), 200
        
    except Exception as e:
        logging.error(f"Error in bulk create: {e}")
        return jsonify({"msg": f"Error processing file: {str(e)}"}), 500

@bp.route('/<forest_id>/update', methods=['POST'])
@jwt_required()
def update_forest_route(forest_id):
    identity = get_jwt_identity()  # Returns {'id': user.id, 'user_type': user.user_type}
    user_id = identity['id'] 
    user = User.query.get(user_id)
    data = request.json
    forest_utils.update_forest(
        forest_id=forest_id,
        name=data['name'],
        tree_type=data['tree_type'],
        user=user,
    )
    return jsonify(success=True)

@bp.route('/<forest_id>/delete', methods=['POST'])
@jwt_required()
def delete_forest(forest_id):
    forest = Forest.query.get_or_404(forest_id)
    forest_utils.delete_forest(forest.id)
    return jsonify(success=True)
