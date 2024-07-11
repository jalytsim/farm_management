from flask import Blueprint, json, jsonify, render_template, render_template_string, request, send_file
from flask_login import login_required
from app.models import Farm, Forest, Point
from app.utils.farm_utils import get_farm_id, get_farmProperties
from app.utils.forest_watch_utils import query_forest_watch
from app.utils.map_utils import calculate_area, convert_to_cartesian, create_mapbox_html, create_polygon_from_db, createGeoJSONFeature, createGeojsonFeatureCollection, generate_choropleth_map, generate_choropleth_map_combined, generate_choropleth_map_soil, save_polygon_to_geojson
from flask import Blueprint, render_template
from app import db
from app.utils.point_utils import get_all_points
import json
import datetime
from shapely.geometry import mapping, Polygon as ShapelyPolygon
from geojson import Polygon, MultiPolygon, Feature, FeatureCollection
from sqlalchemy.orm import load_only
from tempfile import NamedTemporaryFile
import plotly.graph_objects as go

bp = Blueprint('map', __name__)

@bp.route('/map')
@login_required
def map():
    # Generate the choropleth map HTML code
    choropleth_map = generate_choropleth_map()
    return render_template('index.html', choropleth_map=choropleth_map)

@bp.route('/dynamicsearch')
@login_required
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

@bp.route('/map/all_points')
@login_required
def display_all_points():
    geojson_file = 'multipolygon.json'
    points = get_all_points()

    choropleth_map = create_mapbox_html(geojson_file, points)

    return render_template('index.html', choropleth_map=choropleth_map)


@bp.route('/forests/<int:forest_id>/geojson', methods=['GET'])
def get_forest_geojson(forest_id):
    points = Point.query.filter_by(owner_type='forest', forest_id=forest_id).options(db.load_only(Point.longitude, Point.latitude)).all()
    forest = Forest.query.filter_by(id=forest_id).first()
    print(forest)
    if not points:
        return jsonify({"error": "No points found for the specified forest_id"}), 404
    
    # Create GeoJSON data from points
    geojson_data = create_geojson(points, forest)
    
    # Create the Mapbox HTML using the GeoJSON data
    mapbox_html = create_mapbox_html_static(geojson_data)
    
    # Render the HTML directly in the response
    return render_template('index.html', choropleth_map=mapbox_html)


@bp.route('/farm/<string:farm_id>/report', methods=['GET'])
def farmerReport(farm_id):

    farm_properties = get_farmProperties(farm_id) 
    
    if farm_properties is None:
        return jsonify({"error": "No data found for the specified farm"}), 404
    
    print(farm_properties)
    farm_info = {
        'farm_id': farm_properties[0][0] if farm_properties else 'N/A',
        'name': farm_properties[0][12] if farm_properties else 'N/A',
        'subcounty': farm_properties[0][14] if farm_properties else 'N/A',
        'district_name': farm_properties[0][15] if farm_properties else 'N/A',
        'district_region': farm_properties[0][15] if farm_properties else 'N/A',
        'geolocation': farm_properties[0][2] if farm_properties else 'N/A',
        'phonenumber': farm_properties[0][5] if farm_properties else 'N/A',
        'phonenumber2': farm_properties[0][7] if farm_properties else 'N/A',
        'date_created': farm_properties[0][9] if farm_properties else 'N/A',
        'date_updated': farm_properties[0][10] if farm_properties else 'N/A',
        'crops': [
            {
                'crop_id': fp[1],
                'tilled_land_size': fp[4],
                'season': fp[5],
                'quality': fp[6],
                'produce_weight': fp[8],
                'harvest_date': fp[9],
                'timestamp': fp[10],
                'channel_partner': fp[13],
                'destination_country': fp[11],
                'customer_name': fp[12]
            } for fp in farm_properties
        ]
    }
    
    data, status_code = gfw(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code
    object_type = 'farm'
    
    return render_template('gfw/view.html', dataset_results=data['dataset_results'], farm=farm_info, object_type=object_type)


@bp.route('/forests/<int:forest_id>/report', methods=['GET'])
def forestReport(forest_id):
    data, status_code = gfw(owner_type='forest', owner_id=str(forest_id))
    if status_code != 200:
        return jsonify(data), status_code
    
    return render_template('gfw/view.html', dataset_results=data['dataset_results'])


@bp.route('/farm/<int:farmer_id>/geojson', methods=['GET'])
def get_farm_geojson(farmer_id):
    farm = Farm.query.filter_by(id=farmer_id).first()
    print(farm.farm_id)
    
    points = Point.query.filter_by(owner_type='farmer', farmer_id=farm.farm_id).options(db.load_only(Point.longitude, Point.latitude)).all()
    
    if not points:
        return jsonify({"error": "No points found for the specified farm_id"  }), 404
    
    # Create GeoJSON data from points
    geojson_data = create_geojson(points, farm)
    
    # Create the Mapbox HTML using the GeoJSON data
    mapbox_html = create_mapbox_html_static(geojson_data)
    
    # Render the HTML directly in the response
    return render_template('index.html', choropleth_map=mapbox_html)

def create_geojson(points, model_instance):
    coordinates = [(point.longitude, point.latitude) for point in points]
    shapely_polygon = ShapelyPolygon(coordinates)
    geojson_polygon = mapping(shapely_polygon)
    properties = {column.name: getattr(model_instance, column.name) for column in model_instance.__table__.columns}
    properties['name'] = model_instance.name
    feature = Feature(geometry=geojson_polygon, properties=properties)
    feature_collection = FeatureCollection([feature])
    return feature_collection

@bp.route('/forests/all/geojson', methods=['GET'])
def get_all_forests_geojson():
    forests = Forest.query.all()
    features = []

    for forest in forests:
        points = Point.query.filter_by(owner_type='forest', forest_id=forest.id).options(db.load_only(Point.longitude, Point.latitude)).all()
        if points:
            geojson_data = create_geojson(points, forest)
            features.extend(geojson_data['features'])

    if not features:
        return jsonify({"error": "No points found for any forest"}), 404

    feature_collection = FeatureCollection(features)
    mapbox_html = create_mapbox_html_static(feature_collection)

    return render_template('index.html', choropleth_map=mapbox_html)

@bp.route('/farm/all/geojson', methods=['GET'])
def get_all_farm_geojson():
    farmers = Farm.query.all()
    features = []

    for farmer in farmers:
        
        points = Point.query.filter_by(owner_type='farmer', farmer_id=farmer.farm_id).options(db.load_only(Point.longitude, Point.latitude)).all()
        if points:
            geojson_data = create_geojson(points, farmer)
            features.extend(geojson_data['features'])

    if not features:
        return jsonify({"error": "No points found for any farm"}), 404

    feature_collection = FeatureCollection(features)
    mapbox_html = create_mapbox_html_static(feature_collection)

    return render_template('index.html', choropleth_map=mapbox_html)

def create_mapbox_html_static(geojson_data):
    """Generate a Mapbox plotly figure with static GeoJSON data and display area in hovertext."""
    fig = go.Figure()
    for feature in geojson_data['features']:
        properties = feature.get('properties', {})
        # Extracting coordinates
        if feature['geometry']['type'] == 'Polygon':
            polygons = [feature['geometry']['coordinates']]
        else:
            polygons = feature['geometry']['coordinates']
        for polygon in polygons:
            for ring in polygon:
                # Convert the vertices from geo-coordinates to Cartesian coordinates
                cartesian_vertices = convert_to_cartesian(ring)
                # Calculate the area of the polygon
                polygon_area = calculate_area(cartesian_vertices)
                # Convert the area to square kilometers
                area_km2 = polygon_area / 1000000
                # Add area information to properties
                properties['Area (sq km)'] = f"{area_km2:.2f} km²"
                # Create hover text
                hover_text = '<br>'.join(f"{key}: {value}" for key, value in properties.items())
                fig.add_trace(go.Scattermapbox(
                    fill="toself",
                    lon=[coord[0] for coord in ring],
                    lat=[coord[1] for coord in ring],
                    text=hover_text,
                    marker={'size': 5, 'color': "red"},
                    line=dict(width=2),
                    hoverinfo='text'
                ))
    center_coords = {"lat": 1.27, "lon": 32.29}
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=center_coords,
            zoom=7
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig.to_html(full_html=False)


def get_coordinates(owner_type, owner_id):
    if owner_type == 'forest':
        points = Point.query.filter_by(owner_type=owner_type, forest_id=owner_id).options(db.load_only(Point.longitude, Point.latitude)).all()
    elif owner_type == 'farmer':
        points = Point.query.filter_by(owner_type=owner_type, farmer_id=owner_id).options(db.load_only(Point.longitude, Point.latitude)).all()
    else:
        return []

    coordinates = [(point.longitude, point.latitude) for point in points]
    return coordinates

def create_geojson(points, owner):
    coordinates = [(point.longitude, point.latitude) for point in points]
    shapely_polygon = ShapelyPolygon(coordinates)
    geojson_polygon = mapping(shapely_polygon)
    properties = {column.name: getattr(owner, column.name) for column in owner.__table__.columns}
    feature = Feature(geometry=geojson_polygon, properties=properties)
    return FeatureCollection([feature])

def gfw(owner_type, owner_id):
    datasets = [
        'umd_tree_cover_loss',
        'gfw_forest_carbon_gross_emissions',
        'gfw_forest_carbon_gross_removals',
        'gfw_forest_carbon_net_flux',
        'gfw_forest_flux_aboveground_carbon_stock_in_emissions_year',
        'gfw_forest_flux_belowground_carbon_stock_in_emissions_year',
        'gfw_forest_flux_deadwood_carbon_stock_in_emissions_year',
    ]

    dataset_results = []
    for dataset in datasets:
        # Get the dataset from the URL parameters or use a default value
        datasetss = request.args.get('dataset', dataset)

        # Get coordinates from the database
        coordinates = get_coordinates(owner_type, owner_id)
        if not coordinates:
            return {"error": "No points found for the specified owner"}, 404

        geometry = {
            "type": "Polygon",
            "coordinates": [coordinates]
        }

        # Query data from the dataset
        sql_query = "SELECT COUNT(*) FROM results"
        dataset_data = query_forest_watch(datasetss, geometry, sql_query)

        # Extract fields dynamically, ensuring to handle cases where 'data' key might be missing
        data_fields = dataset_data.get("data", [{}])[0] if dataset_data else {}

        dataset_results.append({
            'dataset': datasetss,
            'data_fields': data_fields,
            'coordinates': geometry["coordinates"]
        })

    return {"dataset_results": dataset_results}, 200
