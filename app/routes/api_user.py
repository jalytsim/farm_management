import re
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('api_user', __name__, url_prefix='/api/users')

# Fetch all users or a specific user by username or email
@bp.route('/', methods=['GET'])
@jwt_required() 
def get_users():
    username = request.args.get('username')
    email = request.args.get('email')

    if username:
        user = User.query.filter_by(username=username).first()
    elif email:
        user = User.query.filter_by(email=email).first()
    else:
        users = User.query.all()
        return jsonify([{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phonenumber': user.phonenumber,
            'company_name': user.company_name,
            'user_type': user.user_type,
            'is_admin': user.is_admin,
            'date_created': user.date_created,
            'date_updated': user.date_updated
        } for user in users])

    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phonenumber': user.phonenumber,
            'company_name': user.company_name,
            'user_type': user.user_type,
            'is_admin': user.is_admin,
            'date_created': user.date_created,
            'date_updated': user.date_updated
        })
    return jsonify({'message': 'User not found'}), 404

# Create a new user
@bp.route('/create', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phonenumber = data.get('phonenumber')
    company_name = data.get('company_name')
    user_type = data.get('user_type')
    is_admin = data.get('is_admin', False)
    id_start = re.sub(r'[^A-Za-z]', 'A', username)[:4]

    # Ensure id_start is in uppercase
    id_start = id_start.upper()

    # Example result
    print(id_start)

    # Check if the user already exists
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'message': 'Username or email already exists'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256'),

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        phonenumber=phonenumber,
        company_name=company_name,
        user_type=user_type,
        is_admin=is_admin,
        id_start=id_start
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

# Update a user's details
@bp.route('/<int:id>/edit', methods=['PUT'])
@jwt_required()
def edit_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    if 'password' in data:
        user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    user.phonenumber = data.get('phonenumber', user.phonenumber)
    user.company_name = data.get('company_name', user.company_name)
    user.user_type = data.get('user_type', user.user_type)
    user.is_admin = data.get('is_admin', user.is_admin)

    db.session.commit()

    return jsonify({'message': 'User updated successfully'})

# Get a specific user by ID
@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phonenumber': user.phonenumber,
        'company_name': user.company_name,
        'user_type': user.user_type,
        'is_admin': user.is_admin,
        'date_created': user.date_created,
        'date_updated': user.date_updated
    })

# Delete a user by ID
@bp.route('/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'})