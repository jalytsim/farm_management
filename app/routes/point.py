from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required

from app.utils.point_utils import create_point, delete_point, get_points_by_farm_id, get_points_by_forest_id, update_point

bp = Blueprint('point', __name__)
@bp.route('/point/create', methods=['POST'])
@login_required
def handle_create_point():
    longitude = request.form['longitude']
    latitude = request.form['latitude']
    district_id = request.form['district_id']
    owner_type = request.form['owner_type']
    owner_id = request.form['owner_id']
    create_point(longitude, latitude, district_id, owner_type, owner_id)
    return redirect(url_for('point.index'))

@bp.route('/point/update/<int:id>', methods=['POST'])
@login_required
def handle_update_point(id):
    longitude = request.form['longitude']
    latitude = request.form['latitude']
    district_id = request.form['district_id']
    owner_type = request.form['owner_type']
    owner_id = request.form['owner_id']
    update_point(id, longitude, latitude, district_id, owner_type, owner_id)
    return redirect(url_for('point.index'))

@bp.route('/point/delete/<int:id>', methods=['POST'])
@login_required
def handle_delete_point(id):
    delete_point(id)
    return redirect(url_for('point.index'))

@bp.route('/points/forest/<int:forest_id>')
def points_by_forest(forest_id):
    points = get_points_by_forest_id(forest_id)
    return points

@bp.route('/points/farm/<int:farm_id>')
def points_by_farm(farm_id):
    points = get_points_by_farm_id(farm_id)
    return points