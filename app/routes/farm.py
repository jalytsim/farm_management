from flask import Blueprint, flash, render_template, redirect, request, url_for, send_file
from flask_login import current_user, login_required
from app.models import District, Farm, FarmerGroup, ProduceCategory
from app.utils import farm_utils
from app.utils.qr_generator import generate_qr_codes
from app.utils.map_utils import generate_choropleth_map

bp = Blueprint('farm', __name__)


def farmer_or_admin_required(f):
    @login_required
    def wrap(*args, **kwargs):
        if current_user.user_type != 'farmer' and not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@bp.route('/farms')
@login_required
@farmer_or_admin_required
def index():
    farms = Farm.query.all()
    districts = District.query.all()
    farmergroups = FarmerGroup.query.all()
    categories = ProduceCategory.query.all()
    return render_template('farm/index.html', farms=farms, districts=districts, farmergroups=farmergroups,categories=categories)
@bp.route('/farm/create', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def create_farm():
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        name = request.form['name']
        district_id = request.form['district_id']
        farmergroup_id = request.form['farmergroup_id']
        longitude = request.form['longitude']
        latitude = request.form['latitude']
        geolocation = f"{latitude},{longitude}"

        farm_utils.create_farm(farm_id, name, district_id, farmergroup_id, district_id, geolocation)
        return redirect(url_for('farm.index'))

    districts = District.query.all()
    farmergroups = FarmerGroup.query.all()
    return render_template('farm/create.html', districts=districts, farmergroups=farmergroups)
@bp.route('/farm/<int:farm_id>/edit', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def edit_farm(farm_id):
    farms = Farm.query.all()
    districts = District.query.all()
    farmergroups = FarmerGroup.query.all()
    categories = ProduceCategory.query.all()
    farm = Farm.query.get_or_404(farm_id)
    if request.method == 'POST':
        farm_id2 = request.form['farm_id']
        name = request.form['name']
        subcounty = request.form['subcounty']
        farmergroup_id = request.form['farmergroup_id']
        district_id = request.form['district_id']
        geolocation = request.form['geolocation']
        farm_utils.update_farm(farm, farm_id2, name, subcounty, farmergroup_id, district_id, geolocation)
        return redirect(url_for('farm.index'))
    return render_template('farm/index.html', farms=farms, districts=districts, farmergroups=farmergroups,categories=categories)

@bp.route('/farm/<int:farm_id>/delete', methods=['POST'])
@login_required
@farmer_or_admin_required
def delete_farm(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    farm_utils.delete_farm(farm)
    return redirect(url_for('farm.index'))
@bp.route('/farm')
@login_required
@farmer_or_admin_required
def dashboard():
    # Handle farm dashboard logic
    return render_template('home.html')


@bp.route('/boundaries/<region_name>/<farm_id>')
@login_required
@farmer_or_admin_required
def generate_polygon_map_specific_region(region_name, farm_id):
    # Generate polygon map for a specific region
    choropleth_map = generate_choropleth_map(region_name, farm_id)
    return render_template('index.html', choropleth_map=choropleth_map)

@bp.route('/map/all_points')
@login_required
@farmer_or_admin_required
def display_all_points():
    # Generate map displaying all points
    choropleth_map = generate_choropleth_map()
    return render_template('index.html', choropleth_map=choropleth_map)
