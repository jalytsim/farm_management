# routes/crop_routes.py
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.routes.admin import admin_required
from app.routes.farm import farmer_or_admin_required
from app.utils.district_utils import create_district, delete_district, get_all_districts, get_district_by_id, update_district

bp = Blueprint('districts', __name__)

@bp.route('/districts', methods=['GET'])
@login_required
@farmer_or_admin_required
def list_districts():
    districts = get_all_districts()
    return render_template('districts/list.html', districts=districts)

@bp.route('/districts/<int:district_id>', methods=['GET'])
@login_required
@farmer_or_admin_required
def view_district(district_id):
    district = get_district_by_id(district_id)
    return render_template('districts/view.html', district=district)

@bp.route('/districts/create', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def create_district_route():
    if request.method == 'POST':
        name = request.form.get('name')
        region = request.form.get('region')
        create_district(name, region)
        flash('District created successfully.', 'success')
        return redirect(url_for('districts.list_districts'))
    return render_template('districts/create.html')

@bp.route('/districts/edit/<int:district_id>', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def edit_district_route(district_id):
    district = get_district_by_id(district_id)
    if request.method == 'POST':
        name = request.form.get('name')
        region = request.form.get('region')
        update_district(district_id, name, region)
        flash('District updated successfully.', 'success')
        return redirect(url_for('districts.list_districts'))
    return render_template('districts/edit.html', district=district)

@bp.route('/districts/delete/<int:district_id>', methods=['POST'])
@login_required
@farmer_or_admin_required
def delete_district_route(district_id):
    delete_district(district_id)
    flash('District deleted successfully.', 'success')
    return redirect(url_for('districts.list_districts'))

