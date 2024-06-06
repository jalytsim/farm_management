from flask import Blueprint, render_template, request
from flask_login import login_required
from app.utils.map_utils import generate_choropleth_map, generate_choropleth_map_combined, generate_choropleth_map_soil
from flask import Blueprint, render_template
from app import db

bp = Blueprint('map', __name__)

@bp.route('/map')
@login_required
def map():
    # Generate the choropleth map HTML code
    choropleth_map = generate_choropleth_map()
    return render_template('index.html', choropleth_map=choropleth_map)

@bp.route('/dynamicsearch')
def index_dynamics():
    # Get user-specified parameters from the URL or form
    data_variable = request.args.get('data_variable', 'actual_yield')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    # Get the selected crop ID from the request
    crop = request.args.get('crop', None)

    # Generate the choropleth map HTML code
    choropleth_map = generate_choropleth_map(
        data_variable=data_variable, start_date=start_date, end_date=end_date, crop=crop)

    # Render the template with the choropleth map
    return render_template('dynamic.html', choropleth_map=choropleth_map)

@bp.route('/combined_map')
@login_required
def index_combined():
    # Generate the choropleth map HTML code
    choropleth_map = generate_choropleth_map_combined()

    # Render the template with the choropleth map
    return render_template('index.html', choropleth_map=choropleth_map)

@bp.route('/soil')
@login_required
def index_soil():
    # Generate the choropleth map HTML code
    choropleth_map = generate_choropleth_map_soil()

    # Render the template with the choropleth map
    return render_template('index.html', choropleth_map=choropleth_map)
