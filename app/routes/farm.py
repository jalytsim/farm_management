from flask import Blueprint, render_template, redirect, request, url_for, send_file
from flask_login import login_required
from app.utils.qr_generator import generate_qr_codes
from app.utils.map_utils import generate_choropleth_map

bp = Blueprint('farm', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    # Handle farm dashboard logic
    return render_template('home.html')


@bp.route('/boundaries/<region_name>/<farm_id>')
@login_required
def generate_polygon_map_specific_region(region_name, farm_id):
    # Generate polygon map for a specific region
    choropleth_map = generate_choropleth_map(region_name, farm_id)
    return render_template('index.html', choropleth_map=choropleth_map)

@bp.route('/map/all_points')
@login_required
def display_all_points():
    # Generate map displaying all points
    choropleth_map = generate_choropleth_map()
    return render_template('index.html', choropleth_map=choropleth_map)
