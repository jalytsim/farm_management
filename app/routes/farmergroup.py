from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, FarmerGroup
from app.routes.farm import farmer_or_admin_required
from datetime import datetime

bp = Blueprint('farmergroup', __name__)

@bp.route('/farmergroup')
@login_required
@farmer_or_admin_required
def index():
    farmer_groups = FarmerGroup.query.all()
    return render_template('farmergroup/index.html', farmer_groups=farmer_groups)

@bp.route('/farmergroup/create', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def create_fg():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        new_fg = FarmerGroup(name=name, description=description)
        db.session.add(new_fg)
        db.session.commit()

        flash('Farmer Group created successfully', 'success')
        return redirect(url_for('farmergroup.index'))

    return render_template('farmergroup/create.html')

@bp.route('/farmergroup/<int:fg_id>/edit', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def edit_fg(fg_id):
    farmer_group = FarmerGroup.query.get_or_404(fg_id)

    if request.method == 'POST':
        farmer_group.name = request.form['name']
        farmer_group.description = request.form['description']

        db.session.commit()

        flash('Farmer Group updated successfully', 'success')
        return redirect(url_for('farmergroup.index'))

    return render_template('farmergroup/edit.html', farmer_group=farmer_group)

@bp.route('/farmergroup/<int:fg_id>/delete', methods=['POST'])
@login_required
@farmer_or_admin_required
def delete_fg(fg_id):
    farmer_group = FarmerGroup.query.get_or_404(fg_id)

    db.session.delete(farmer_group)
    db.session.commit()

    flash('Farmer Group deleted successfully', 'success')
    return redirect(url_for('farmergroup.index'))
