import csv
from flask import Blueprint, abort, flash, json, jsonify, make_response, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from app.models import Crop, Farm, FarmData, Forest, Point
from app.routes.farm import farmer_or_admin_required
from app.routes.forest import forest_or_admin_required
from app.utils.forest_watch_utils import query_forest_watch
from app.utils.map_utils import calculate_area, create_mapbox_html,generate_choropleth_map, generate_choropleth_map_combined, generate_choropleth_map_soil
from flask import Blueprint, render_template
from app import db
from app.utils.point_utils import get_all_points
import json
from shapely.geometry import mapping, Polygon as ShapelyPolygon
from geojson import Polygon, Feature, FeatureCollection
from tempfile import NamedTemporaryFile
import plotly.graph_objects as go
import plotly.graph_objects as go
from shapely.geometry import Polygon
from pyproj import Transformer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
@forest_or_admin_required 
def get_forest_geojson(forest_id):
    points = Point.query.filter_by(owner_type='forest', forest_id=forest_id).options(db.load_only(Point.longitude, Point.latitude)).all()
    forest = Forest.query.filter_by(id=forest_id).first()
    print(forest)
    if not points:
        flash("error: No points found for the specified forest_id"), 404
        return redirect(url_for('forest.index'))
    # Create GeoJSON data from points
    geojson_data = create_geojson(points, forest)
    # Create the Mapbox HTML using the GeoJSON data
    mapbox_html = create_mapbox_html_static(geojson_data)
    # Render the HTML directly in the response
    return render_template('index.html', choropleth_map=mapbox_html)


@bp.route('/farm/<string:farm_id>/report', methods=['GET'])
@farmer_or_admin_required
def farmerReport(farm_id):
    # Fetch the farm details
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if farm is None:
        abort(404, description="Farm not found")
    # Fetch related data for the farm
    farmer_group = farm.farmer_group
    district = farm.district
    farm_data = FarmData.query.filter_by(farm_id=farm_id).all()
    # Extract farm info
    farm_info = {
        'farm_id': farm.farm_id,
        'name': farm.name,
        'subcounty': farm.subcounty,
        'district_name': farm.district.name if farm.district else 'N/A',
        'district_region': farm.district.region if farm.district else 'N/A',
        'geolocation': farm.geolocation,
        'phonenumber': farm.phonenumber,
        'phonenumber2': farm.phonenumber2,
        'date_created': farm.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_updated': farm.date_updated.strftime('%Y-%m-%d %H:%M:%S'),
        'crops': [
            {
                'crop': Crop.query.get_or_404(data.crop_id).name,
                'land_type': data.land_type,
                'tilled_land_size': data.tilled_land_size,
                'planting_date': data.planting_date.strftime('%Y-%m-%d') if data.planting_date else 'N/A',
                'season': data.season,
                'quality': data.quality,
                'quantity': data.quantity,
                'harvest_date': data.harvest_date.strftime('%Y-%m-%d') if data.harvest_date else 'N/A',
                'expected_yield': data.expected_yield,
                'actual_yield': data.actual_yield,
                'timestamp': data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'channel_partner': data.channel_partner,
                'destination_country': data.destination_country,
                'customer_name': data.customer_name
            } for data in farm_data
        ]
    }
    # Fetch GFW data for the farm
    data, status_code = gfw(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code
    object_type = 'farm'
    return render_template('gfw/view.html', dataset_results=data['dataset_results'], farm=farm_info, object_type=object_type)


@bp.route('/forests/<int:forest_id>/report', methods=['GET'])
@forest_or_admin_required 
def forestReport(forest_id):
    data, status_code = gfw(owner_type='forest', owner_id=str(forest_id))
    if status_code != 200:
        return jsonify(data), status_code
    forest = Forest.query.filter_by(id=forest_id).first()
    print(forest.name)
    object_type = 'forest'
    return render_template('gfw/view.html', dataset_results=data['dataset_results'], forest=forest,  object_type = object_type)


@bp.route('/farm/<int:farmer_id>/geojson', methods=['GET'])
@farmer_or_admin_required
def get_farm_geojson(farmer_id):
    farm = Farm.query.filter_by(id=farmer_id).first()
    print(farm.farm_id)
    points = Point.query.filter_by(owner_type='farmer', farmer_id=farm.farm_id).options(db.load_only(Point.longitude, Point.latitude)).all()
    if not points:
        flash("error: No points found for the specified farm_id"  ), 404
        return redirect(url_for('farm.index'))
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
@forest_or_admin_required   
def get_all_forests_geojson():
    if current_user.is_admin:
        forests = Forest.query.all()
    else:
        forests = Forest.query.filter_by(created_by=current_user.id)
    features = []
    for forest in forests:
        points = Point.query.filter_by(owner_type='forest', forest_id=forest.id).options(db.load_only(Point.longitude, Point.latitude)).all()
        if points:
            geojson_data = create_geojson(points, forest)
            features.extend(geojson_data['features'])
    if not features:
        flash("error: No points found for any forest"), 404
        return redirect(url_for('forest.index'))
    feature_collection = FeatureCollection(features)
    mapbox_html = create_mapbox_html_static(feature_collection)
    return render_template('index.html', choropleth_map=mapbox_html)

@bp.route('/farm/all/geojson', methods=['GET'])
@farmer_or_admin_required
def get_all_farm_geojson():
    if current_user.is_admin:
        farms = Farm.query.all()
    else:
        farms = Farm.query.filter_by(created_by=current_user.id)
    features = []
    for farmer in farms:
        points = Point.query.filter_by(owner_type='farmer', farmer_id=farmer.farm_id).options(db.load_only(Point.longitude, Point.latitude)).all()
        if points:
            geojson_data = create_geojson(points, farmer)
            features.extend(geojson_data['features'])
    if not features:
        flash("error: No points found for any farm"), 404
        return redirect(url_for('farm.index'))
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
                # Calculate the area of the polygon
                area_km2 = calculate_area(ring)
                properties['Area (sq km)'] = f"{area_km2:.4f} km²"
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
        'gfw_radd_alerts',
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
        sql_query = "SELECT SUM(area__ha) FROM results"
        dataset_data = query_forest_watch(datasetss, geometry, sql_query)
        # Extract fields dynamically, ensuring to handle cases where 'data' key might be missing
        data_fields = dataset_data.get("data", [{}])[0] if dataset_data else {}
        dataset_results.append({
            'dataset': datasetss,
            'data_fields': data_fields,
            'coordinates': geometry["coordinates"]
        })
    return {"dataset_results": dataset_results}, 200



@bp.route('/forest/<int:forest_id>/report/download', methods=['GET'])
@login_required
def download_forest_report(forest_id):
    # Fetch the forest details
    forest = Forest.query.filter_by(id=forest_id).first()
    if forest is None:
        abort(404, description="Forest not found")
    
    # Fetch related data for the forest
    forest_data = Point.query.filter_by(owner_type='forest', forest_id=forest_id).all()
    
    # Extract forest info
    forest_info = {
        'forest_id': forest.id,
        'name': forest.name,
        'geolocation': [
            {
                'longitude': point.longitude,
                'latitude': point.latitude
            } for point in forest_data
        ],
        'additional_info': 'Additional information if needed'
    }
    
    # Fetch GFW data for the forest
    data, status_code = gfw(owner_type='forest', owner_id=str(forest_id))
    if status_code != 200:
        return jsonify(data), status_code
    
    # Create PDF
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=forest_{forest_id}_report.pdf'
    
    c = canvas.Canvas(response.stream, pagesize=letter)
    width, height = letter
    
    c.drawString(100, height - 100, f"Forest Report: {forest.name}")
    
    c.drawString(100, height - 120, f"Forest ID: {forest_info['forest_id']}")
    c.drawString(100, height - 140, f"Name: {forest_info['name']}")
    c.drawString(100, height - 160, "Geolocation:")
    y = height - 180
    for geo in forest_info['geolocation']:
        c.drawString(120, y, f"Longitude: {geo['longitude']}, Latitude: {geo['latitude']}")
        y -= 20
    
    c.drawString(100, y, f"Additional Info: {forest_info['additional_info']}")
    
    y -= 40
    c.drawString(100, y, "GFW Data:")
    y -= 20
    for result in data['dataset_results']:
        c.drawString(120, y, f"Dataset: {result['dataset']}")
        y -= 20
        c.drawString(140, y, f"Area (ha): {result['data_fields'].get('area__ha', 'N/A')}")
        y -= 20
    
    c.save()
    
    return response

@bp.route('/farm/<string:farm_id>/report/download', methods=['GET'])
@login_required
def download_farm_report(farm_id):
    # Fetch the farm details
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if farm is None:
        abort(404, description="Farm not found")
    # Fetch related data for the farm
    farm_data = FarmData.query.filter_by(farm_id=farm_id).all()
    
    # Extract farm info
    farm_info = {
        'farm_id': farm.farm_id,
        'name': farm.name,
        'subcounty': farm.subcounty,
        'district_name': farm.district.name if farm.district else 'N/A',
        'district_region': farm.district.region if farm.district else 'N/A',
        'geolocation': farm.geolocation,
        'phonenumber': farm.phonenumber,
        'phonenumber2': farm.phonenumber2,
        'date_created': farm.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_updated': farm.date_updated.strftime('%Y-%m-%d %H:%M:%S'),
        'crops': [
            {
                'crop': Crop.query.get_or_404(data.crop_id).name,
                'land_type': data.land_type,
                'tilled_land_size': data.tilled_land_size,
                'planting_date': data.planting_date.strftime('%Y-%m-%d') if data.planting_date else 'N/A',
                'season': data.season,
                'quality': data.quality,
                'quantity': data.quantity,
                'harvest_date': data.harvest_date.strftime('%Y-%m-%d') if data.harvest_date else 'N/A',
                'expected_yield': data.expected_yield,
                'actual_yield': data.actual_yield,
                'timestamp': data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'channel_partner': data.channel_partner,
                'destination_country': data.destination_country,
                'customer_name': data.customer_name
            } for data in farm_data
        ]
    }
    
    # Fetch GFW data for the farm
    data, status_code = gfw(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code
    
    # Create PDF
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=farm_{farm_id}_report.pdf'
    
    c = canvas.Canvas(response.stream, pagesize=letter)
    width, height = letter
    
    c.drawString(100, height - 100, f"Farm Report: {farm.name}")
    
    c.drawString(100, height - 120, f"Farm ID: {farm_info['farm_id']}")
    c.drawString(100, height - 140, f"Name: {farm_info['name']}")
    c.drawString(100, height - 160, f"Subcounty: {farm_info['subcounty']}")
    c.drawString(100, height - 180, f"District Name: {farm_info['district_name']}")
    c.drawString(100, height - 200, f"District Region: {farm_info['district_region']}")
    c.drawString(100, height - 220, f"Geolocation: {farm_info['geolocation']}")
    c.drawString(100, height - 240, f"Phone Number: {farm_info['phonenumber']}")
    c.drawString(100, height - 260, f"Phone Number 2: {farm_info['phonenumber2']}")
    c.drawString(100, height - 280, f"Date Created: {farm_info['date_created']}")
    c.drawString(100, height - 300, f"Date Updated: {farm_info['date_updated']}")
    
    y = height - 320
    c.drawString(100, y, "Crops:")
    for crop in farm_info['crops']:
        y -= 20
        c.drawString(120, y, f"Crop: {crop['crop']}")
        y -= 20
        c.drawString(140, y, f"Land Type: {crop['land_type']}")
        y -= 20
        c.drawString(140, y, f"Tilled Land Size: {crop['tilled_land_size']}")
        y -= 20
        c.drawString(140, y, f"Planting Date: {crop['planting_date']}")
        y -= 20
        c.drawString(140, y, f"Season: {crop['season']}")
        y -= 20
        c.drawString(140, y, f"Quality: {crop['quality']}")
        y -= 20
        c.drawString(140, y, f"Quantity: {crop['quantity']}")
        y -= 20
        c.drawString(140, y, f"Harvest Date: {crop['harvest_date']}")
        y -= 20
        c.drawString(140, y, f"Expected Yield: {crop['expected_yield']}")
        y -= 20
        c.drawString(140, y, f"Actual Yield: {crop['actual_yield']}")
        y -= 20
        c.drawString(140, y, f"Timestamp: {crop['timestamp']}")
        y -= 20
        c.drawString(140, y, f"Channel Partner: {crop['channel_partner']}")
        y -= 20
        c.drawString(140, y, f"Destination Country: {crop['destination_country']}")
        y -= 20
        c.drawString(140, y, f"Customer Name: {crop['customer_name']}")
        y -= 20
    
    c.showPage()
    
    c.drawString(100, height - 100, "GFW Data:")
    y = height - 120
    for result in data['dataset_results']:
        y -= 20
        c.drawString(100, y, f"Dataset: {result['dataset']}")
        y -= 20
        c.drawString(120, y, f"Area (ha): {result['data_fields'].get('area__ha', 'N/A')}")
        y -= 20
    
    c.save()
    
    return response
def calculate_area(polygon_coords):
    # Convert the coordinates to (longitude, latitude) for Shapely
    coordinates = [(coord[0], coord[1]) for coord in polygon_coords]
    # Create a Shapely polygon
    polygon = Polygon(coordinates)
    # Use pyproj to transform the coordinates for accurate area calculation
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
    projected_coords = [transformer.transform(lon, lat) for lon, lat in coordinates]
    # Create a Shapely polygon with projected coordinates
    projected_polygon = Polygon(projected_coords)
    # Calculate area in square meters and convert to square kilometers
    area_km2 = projected_polygon.area / 1_000_000
    return area_km2

def calculate_area_m2(polygon_coords, utm_zone=36):
    """
    Calculate the area of a polygon in square meters using UTM projection.
    Args:
        polygon_coords (list): List of coordinates of the polygon in (longitude, latitude).
        utm_zone (int): UTM zone number (default is 36 for UTM 36N).

    Returns:
        float: Area of the polygon in square meters.
    """
    # Convert the coordinates to (longitude, latitude) for Shapely
    coordinates = [(coord[0], coord[1]) for coord in polygon_coords]
    # Define UTM CRS for the specified zone (36 for UTM 36N)
    utm_crs = f"epsg:326{utm_zone}"
    # Create a Shapely polygon
    polygon = Polygon(coordinates)
    # Use pyproj to transform the coordinates for accurate area calculation
    transformer = Transformer.from_crs("epsg:4326", utm_crs, always_xy=True)
    projected_coords = [transformer.transform(lon, lat) for lon, lat in coordinates]
    # Create a Shapely polygon with projected coordinates
    projected_polygon = Polygon(projected_coords)
    # Calculate area in square meters
    area_m2 = projected_polygon.area
    return area_m2

def calculate_area_accurate(polygon_coords, utm_zone=36):
    """
    Calculate the area of a polygon in square meters using UTM projection with corrected accuracy.

    Args:
        polygon_coords (list): List of coordinates of the polygon in (longitude, latitude).
        utm_zone (int): UTM zone number (default is 36 for UTM 36N).

    Returns:
        float: Area of the polygon in square meters.
    """
    # Convert the coordinates to (longitude, latitude) for Shapely
    coordinates = [(coord[0], coord[1]) for coord in polygon_coords]
    # Define UTM CRS for the specified zone (36 for UTM 36N)
    utm_crs = f"epsg:326{utm_zone}"
    # Create a Shapely polygon
    polygon = Polygon(coordinates)
    # Use pyproj to transform the coordinates for accurate area calculation
    transformer = Transformer.from_crs("epsg:4326", utm_crs, always_xy=True)
    projected_coords = [transformer.transform(lon, lat) for lon, lat in coordinates]
    # Create a Shapely polygon with projected coordinates
    projected_polygon = Polygon(projected_coords)
    # Calculate area in square meters
    area_m2 = projected_polygon.area
    return area_m2




def create_mapbox_html_static_token(geojson_data):
    """Generate a Mapbox plotly figure with static GeoJSON data and display area in hovertext."""
    fig = go.Figure()
    mapbox_access_token = "acess token"
    mapbox_style = ""
    for feature in geojson_data['features']:
        properties = feature.get('properties', {})        
        # Extracting coordinates
        if feature['geometry']['type'] == 'Polygon':
            polygons = [feature['geometry']['coordinates']]
        else:
            polygons = feature['geometry']['coordinates']
        
        for polygon in polygons:
            for ring in polygon:
                # Calculate the area of the polygon
                area_km2 = calculate_area(ring)
                properties['Area (sq km)'] = f"{area_km2:.4f} km²"
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
            accesstoken=mapbox_access_token,  # Your Mapbox access token
            style=mapbox_style,  # Your custom Mapbox style
            center=center_coords,
            zoom=7
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    
    return fig.to_html(full_html=False)
