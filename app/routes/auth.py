from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from ..models import User
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
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
    if current_user.is_authenticated:
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
    if current_user.user_type == 'farmer':
        return render_template('farmer_dashboard.html')
    elif current_user.user_type == 'forest':
        return render_template('forest_dashboard.html')
    else:
        flash('Invalid user type', 'danger')
        return redirect(url_for('auth.logout'))