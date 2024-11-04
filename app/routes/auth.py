from datetime import timedelta
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_cors import cross_origin
from flask_login import login_required, login_user, logout_user, current_user as login_current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, current_user as jwt_current_user
from ..models import User
from app import db

bp = Blueprint('auth', __name__)


@bp.route('/api/login', methods=['POST'])
def api_login():
    email = request.json.get('email')
    password = request.json.get('password')
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        # Inclure user_type dans le token JWT
        access_token = create_access_token(identity={'id': user.id, 'is_admin': user.is_admin, 'user_type': user.user_type}, expires_delta=timedelta(days=7))
        return jsonify(token=access_token), 200
    else:
        return jsonify({"msg": "Login Unsuccessful. Please check email and password"}), 401

@bp.route('/api/signup', methods=['POST'])
def api_signup():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    phonenumber = request.json.get('phonenumber')
    user_type = request.json.get('user_type')

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"msg": "Email address already exists"}), 400

    new_user = User(
        username=username,
        email=email,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        phonenumber=phonenumber,
        user_type=user_type
    )
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=new_user.id)
    return jsonify(token=access_token), 201

@bp.route('/api/dashboard')
@jwt_required()
def api_dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.user_type == 'farmer':
        return render_template('farmer_dashboard.html')
    elif user.user_type == 'forest':
        return render_template('forest_dashboard.html')
    else:
        return jsonify({"msg": "Invalid user type"}), 403

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if login_current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('main/login.html')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if login_current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phonenumber = request.form.get('phonenumber')
        user_type = request.form.get('user_type')
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('auth.signup'))

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            phonenumber=phonenumber,
            user_type=user_type
        )
        
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        
        return redirect(url_for('main.home'))
    
    return render_template('signup.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    if login_current_user.user_type == 'farmer':
        return render_template('farmer_dashboard.html')
    elif login_current_user.user_type == 'forest':
        return render_template('forest_dashboard.html')
    else:
        flash('Invalid user type', 'danger')
        return redirect(url_for('auth.logout'))
