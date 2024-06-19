# routes/point_routes.py
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import District, Farm, Forest
from app.routes.admin import admin_required
from app.routes.farm import farmer_or_admin_required
from app import db
from app.utils.point_utils import create_point, delete_point, get_all_points, get_point_by_id, update_point

bp = Blueprint('points', __name__)

@bp.route('/points', methods=['GET'])
@login_required
def list_points():
    points = get_all_points()
    return render_template('points/list.html', points=points)

@bp.route('/points/<int:point_id>', methods=['GET'])
@login_required
def view_point(point_id):
    point = get_point_by_id(point_id)
    return render_template('points/view.html', point=point)

@bp.route('/points/create', methods=['GET', 'POST'])
@login_required
def create_point_route():
    if request.method == 'POST':
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        owner_type = request.form.get('owner_type')
        forest_id = request.form.get('forest_id')
        farmer_id = request.form.get('farmer_id')
        district_id = request.form.get('district_id')
        
        if owner_type == 'forest':
            if forest_id:
                forest_id = int(forest_id)
                # Check if the forest_id exists
                forest = db.session.query(Forest).filter_by(id=forest_id).first()
                if not forest:
                    print('Invalid Forest ID.', 'error')
                    return render_template('points/create.html')
            else:
                forest_id = None
            farmer_id = None
        elif owner_type == 'farmer':
            farmer_id = farmer_id.strip() if farmer_id else None
            forest_id = None

        create_point(longitude, latitude, owner_type, forest_id, farmer_id, district_id)
        flash('Point created successfully.', 'success')
        return redirect(url_for('points.list_points'))
    
    districts = District.query.all()
    forests =Forest.query.all()
    farms = Farm.query.all()
    return render_template('points/create.html', districts = districts, forests = forests, farms=farms)

@bp.route('/points/edit/<int:point_id>', methods=['GET', 'POST'])
@login_required
def edit_point_route(point_id):
    point = get_point_by_id(point_id)
    if not point:
        print('Point not found.', 'error')
        return redirect(url_for('points.list_points'))

    if request.method == 'POST':
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        owner_type = request.form.get('owner_type')
        forest_id = request.form.get('forest_id')
        farmer_id = request.form.get('farmer_id')
        district_id = request.form.get('district_id')

        if owner_type == 'forest':
            if forest_id:
                forest_id = int(forest_id)
                # Check if the forest_id exists
                forest = db.session.query(Forest).filter_by(id=forest_id).first()
                if not forest:
                    print('Invalid Forest ID.', 'error')
                    return render_template('points/edit.html', point=point)
            else:
                forest_id = None
            farmer_id = None
        elif owner_type == 'farmer':
            farmer_id = farmer_id.strip() if farmer_id else None
            forest_id = None

        update_point(point_id, longitude, latitude, owner_type, forest_id, farmer_id, district_id)
        print('Point updated successfully.', 'success')
        return redirect(url_for('points.list_points'))
    districts = District.query.all()
    forests =Forest.query.all()
    farms = Farm.query.all()
    return render_template('points/edit.html', point=point, districts = districts, forests = forests, farms=farms)

@bp.route('/points/delete/<int:point_id>', methods=['POST'])
@login_required
def delete_point_route(point_id):
    delete_point(point_id)
    print('Point deleted successfully.', 'success')
    return redirect(url_for('points.list_points'))
