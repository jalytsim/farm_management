import re
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app import db
from werkzeug.security import generate_password_hash

bp = Blueprint('api_user', __name__, url_prefix='/api/users')


# ─── GET all users (ou filtrer par username / email) ────────────────────────
@bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    username = request.args.get('username')
    email    = request.args.get('email')

    if username:
        user = User.query.filter_by(username=username).first()
    elif email:
        user = User.query.filter_by(email=email).first()
    else:
        users = User.query.all()
        return jsonify([{
            'id':              u.id,
            'username':        u.username,
            'email':           u.email,
            'phonenumber':     u.phonenumber,
            'company_name':    u.company_name,
            'user_type':       u.user_type,
            'is_admin':        u.is_admin,
            'has_access_wbii': u.has_access_wbii,   # ✅ retourné au frontend
            'date_created':    u.date_created,
            'date_updated':    u.date_updated,
        } for u in users])

    if user:
        return jsonify({
            'id':              user.id,
            'username':        user.username,
            'email':           user.email,
            'phonenumber':     user.phonenumber,
            'company_name':    user.company_name,
            'user_type':       user.user_type,
            'is_admin':        user.is_admin,
            'has_access_wbii': user.has_access_wbii,   # ✅
            'date_created':    user.date_created,
            'date_updated':    user.date_updated,
        })
    return jsonify({'message': 'User not found'}), 404


# ─── GET user by ID ──────────────────────────────────────────────────────────
@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id':              user.id,
        'username':        user.username,
        'email':           user.email,
        'phonenumber':     user.phonenumber,
        'company_name':    user.company_name,
        'user_type':       user.user_type,
        'is_admin':        user.is_admin,
        'has_access_wbii': user.has_access_wbii,   # ✅
        'date_created':    user.date_created,
        'date_updated':    user.date_updated,
    })


# ─── CREATE user ─────────────────────────────────────────────────────────────
@bp.route('/create', methods=['POST'])
def create_user():
    data         = request.json
    username     = data.get('username')
    email        = data.get('email')
    password     = data.get('password')
    phonenumber  = data.get('phonenumber')
    company_name = data.get('company_name')
    user_type    = data.get('user_type')
    is_admin     = data.get('is_admin', False)
    id_start     = re.sub(r'[^A-Za-z]', 'A', username)[:4].upper()

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'message': 'Username or email already exists'}), 400

    new_user = User(
        username=username,
        email=email,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        phonenumber=phonenumber,
        company_name=company_name,
        user_type=user_type,
        is_admin=is_admin,
        id_start=id_start,
        # has_access_wbii vaut False par défaut (voir modèle)
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201


# ─── EDIT user (une seule définition) ────────────────────────────────────────
@bp.route('/<int:id>/edit', methods=['PUT'])
@jwt_required()
def edit_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.json

    user.username     = data.get('username',     user.username)
    user.email        = data.get('email',        user.email)
    user.phonenumber  = data.get('phonenumber',  user.phonenumber)
    user.company_name = data.get('company_name', user.company_name)
    user.user_type    = data.get('user_type',    user.user_type)
    user.is_admin     = data.get('is_admin',     user.is_admin)
    user.has_access_wbii = data.get('has_access_wbii', user.has_access_wbii)  # ✅

    # Ne changer le mot de passe que s'il est fourni et non vide
    if data.get('password'):
        user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    db.session.commit()
    return jsonify({'message': 'User updated successfully'})


# ─── DELETE user ─────────────────────────────────────────────────────────────
@bp.route('/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})


# ─── PATCH accès WBII uniquement (route dédiée, admin seulement) ─────────────
@bp.route('/<int:user_id>/update-access', methods=['PATCH'])
@jwt_required()
def update_wbii_access(user_id):
    identity  = get_jwt_identity()
    requester = User.query.get(identity['id'])

    if not requester or not requester.is_admin:
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403

    target_user = User.query.get_or_404(user_id)
    data        = request.get_json()

    if 'has_access_wbii' not in data:
        return jsonify({'status': 'error', 'message': 'Missing has_access_wbii field'}), 400

    target_user.has_access_wbii = bool(data['has_access_wbii'])
    db.session.commit()

    return jsonify({
        'status':          'success',
        'user_id':         user_id,
        'has_access_wbii': target_user.has_access_wbii,
    })