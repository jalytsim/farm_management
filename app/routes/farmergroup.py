# routes/farmergroup_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, FarmerGroup
from app.routes.farm import farmer_or_admin_required

farmergroup_bp = Blueprint('farmergroup', __name__, url_prefix='/farmergroup')

@farmergroup_bp.route('/farmergroup')
@login_required
@farmer_or_admin_required
def index():
    farmergroups = FarmerGroup.query.all()
    return render_template('farmergroup/index.html', farmergroups=farmergroups)

@farmergroup_bp.route('/create', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def create_farmergroup():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if name:
            new_farmergroup = FarmerGroup(name=name, description=description)
            db.session.add(new_farmergroup)
            db.session.commit()
            flash('Farmer Group created successfully!', 'success')
            return redirect(url_for('farmergroup.index'))
        else:
            flash('Name is required!', 'danger')
    return render_template('farmergroup/create.html')

@farmergroup_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def edit_farmergroup(id):
    farmergroup = FarmerGroup.query.get_or_404(id)
    if request.method == 'POST':
        farmergroup.name = request.form.get('name')
        farmergroup.description = request.form.get('description')
        db.session.commit()
        flash('Farmer Group updated successfully!', 'success')
        return redirect(url_for('farmergroup.index'))
    return render_template('farmergroup/edit.html', farmergroup=farmergroup)

@farmergroup_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@farmer_or_admin_required
def delete_farmergroup(id):
    farmergroup = FarmerGroup.query.get_or_404(id)
    db.session.delete(farmergroup)
    db.session.commit()
    flash('Farmer Group deleted successfully!', 'success')
    return redirect(url_for('farmergroup.index'))
