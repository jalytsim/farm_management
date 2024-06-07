from flask import Blueprint, render_template, redirect, request, url_for, send_file
from flask_login import login_required
from app.models import Farm
from app.utils import farm_utils
from app.utils.qr_generator import generate_qr_codes
from app.utils.map_utils import generate_choropleth_map

bp = Blueprint('farm', __name__)


@bp.route('/farms')
@login_required
def index():
    farms = farm_utils.get_all_farms()
    return render_template('farm/index.html', farms=farms)

@bp.route('/farm/create', methods=['GET', 'POST'])
def create_farm():
    if request.method == 'POST':
        name = request.form['name']
        subcounty = request.form['subcounty']
        farmergroup_id = request.form['farmergroup_id']
        district_id = request.form['district_id']
        geolocation = request.form['geolocation']
        farm_utils.create_farm(name, subcounty, farmergroup_id, district_id, geolocation)
        return redirect(url_for('farm.index'))
    return render_template('farm/create.html')

@bp.route('/farm/<int:farm_id>/edit', methods=['GET', 'POST'])
def edit_farm(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    if request.method == 'POST':
        name = request.form['name']
        subcounty = request.form['subcounty']
        farmergroup_id = request.form['farmergroup_id']
        district_id = request.form['district_id']
        geolocation = request.form['geolocation']
        farm_utils.update_farm(farm, name, subcounty, farmergroup_id, district_id, geolocation)
        return redirect(url_for('farm.index'))
    return render_template('farm/index.html', farms=farm)

@bp.route('/farm/<int:farm_id>/delete', methods=['POST'])
def delete_farm(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    farm_utils.delete_farm(farm)
    return redirect(url_for('farm.index'))
@bp.route('/farm')
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
