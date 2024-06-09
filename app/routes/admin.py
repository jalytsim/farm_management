from flask import Blueprint, jsonify, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import User
from app import db
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @login_required
    def wrap(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@admin_bp.route('/admin')
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)


@admin_bp.route('/admin/create_user', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phonenumber = request.form.get('phonenumber')
        user_type = request.form.get('user_type')
        is_admin = 'is_admin' in request.form

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('admin.create_user'))

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            phonenumber=phonenumber,
            user_type=user_type,
            is_admin=is_admin
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/create_user.html')

@admin_bp.route('/admin/user/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(id=user.id, username=user.username, email=user.email, phonenumber=user.phonenumber, user_type=user.user_type, is_admin=user.is_admin)

@admin_bp.route('/admin/user', methods=['POST'])
@admin_required
def update_user():
    data = request.form
    user_id = data.get('user_id')
    user = User.query.get_or_404(user_id)
    user.username = data.get('username')
    user.email = data.get('email')
    user.phonenumber = data.get('phone')
    user.user_type = data.get('user_type')
    user.is_admin = data.get('is_admin') == 'on'
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/user/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify(success=True)
