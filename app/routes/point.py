from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required

from app.models import District, Point
from app.utils.point_utils import create_point, delete_point, get_points_by_farm_id, get_points_by_forest_id, update_point

bp = Blueprint('point', __name__)

@bp.route('/point/create', methods=['GET', 'POST'])
@login_required
def handle_create_point():
    if request.method == 'POST':
        longitude = request.form['longitude']
        latitude = request.form['latitude']
        district_id = request.form.get('district_id', None)
        owner_type = request.form['owner_type']
        forest_id = request.form.get('forest_id', None)
        farmer_id = request.form.get('farmer_id', None)
        
        create_point(longitude, latitude, owner_type, district_id, forest_id, farmer_id)
        return redirect(url_for('forest.index'))
    
    districts = District.query.all()  # Get all districts for the dropdown
    return render_template('create_point.html', districts=districts, owner_types=['forest', 'farmer'])

@bp.route('/point/update/<int:id>', methods=['GET', 'POST'])
@login_required
def handle_update_point(id):
    if request.method == 'POST':
        longitude = request.form['longitude']
        latitude = request.form['latitude']
        district_id = request.form['district_id']
        owner_type = request.form['owner_type']
        forest_id = request.form.get('forest_id', None)
        farmer_id = request.form.get('farmer_id', None)
        if not district_id or district_id == 'None':
            district_id = None
        update_point(id, longitude, latitude, district_id, owner_type, forest_id, farmer_id)
        return redirect(url_for('forest.index'))
    
    point = Point.query.get(id)
    districts = District.query.all()
    return render_template('update_point.html', point=point, districts=districts, owner_types=['forest', 'farmer'])
@bp.route('/point/delete/<int:id>', methods=['POST'])
@login_required
def handle_delete_point(id):
    delete_point(id)
    return redirect(url_for('forest.index'))

@bp.route('/points/forest/<int:forest_id>')
def points_by_forest(forest_id):
    points = get_points_by_forest_id(forest_id)
    return points

@bp.route('/points/farm/<int:farm_id>')
def points_by_farm(farm_id):
    points = get_points_by_farm_id(farm_id)
    return points

@bp.route('/points/list')
@login_required
def list_points():
    points = Point.query.all()
    return render_template('view.html', points=points)

@bp.route('/points/view')
@login_required
def view_points():
    points = Point.query.all()
    return render_template('list.html', points=points)
