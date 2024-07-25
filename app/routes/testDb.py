import os
from flask import Blueprint, jsonify, render_template, request
from app.utils.forest_watch_utils import create_sql_query, get_pixel_meaning, query_forest_watch
from ..models import db, Farm, Forest, Point

from shapely.geometry import mapping, Polygon as ShapelyPolygon
from geojson import Feature, FeatureCollection

test = Blueprint('test', __name__)

@test.route('/test')
def test_db():
    datasets = [
        'umd_tree_cover_loss',
        'gfw_forest_carbon_gross_emissions',
        'gfw_forest_carbon_gross_removals',
        'gfw_forest_carbon_net_flux',
        'gfw_forest_flux_aboveground_carbon_stock_in_emissions_year',
        'gfw_forest_flux_belowground_carbon_stock_in_emissions_year',
        'gfw_forest_flux_deadwood_carbon_stock_in_emissions_year',
    ]

    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [32.588851, 0.54519],
                [32.588883, 0.545424],
                [32.58914, 0.545861],
                [32.590049, 0.545409],
                [32.590066, 0.545245],
                [32.590386, 0.545663],
                [32.590741, 0.545458],
                [32.590601, 0.545196],
                [32.591077, 0.54479],
                [32.591221, 0.544532],
                [32.591223, 0.544332],
                [32.591454, 0.54422],
                [32.59116, 0.543855],
                [32.591492, 0.543857],
                [32.591973, 0.543428],
                [32.591661, 0.542925],
                [32.591228, 0.542902],
                [32.590995, 0.542433],
                [32.588851, 0.54519]
            ]
        ]
    }

    dataset_results = []

    for dataset in datasets:
        # Get the dataset from the URL parameters or use a default value
        datasetss = request.args.get('dataset', dataset)

        sql_query = "SELECT SUM(area__ha) FROM results"

        # Query data from the dataset
        dataset_data = query_forest_watch(datasetss, geometry, sql_query)
        print(dataset)
        print(sql_query)
        print(dataset_data)


        # Extract fields dynamically, ensuring to handle cases where 'data' key might be missing
        data_fields = dataset_data.get("data", [{}])[0] if dataset_data else {}

        dataset_results.append({
            'dataset': datasetss,
            'data_fields': data_fields,
            'coordinates': geometry["coordinates"]
        })

    return render_template('gfw/view.html', dataset_results=dataset_results)



@test.route('/testjson')
def test_gfw():
    datasets = [
        'umd_tree_cover_loss',
        'gfw_forest_carbon_gross_removals',
        'gfw_forest_carbon_net_flux',
        'gfw_forest_flux_aboveground_carbon_stock_in_emissions_year',
        'gfw_forest_flux_belowground_carbon_stock_in_emissions_year',
        'gfw_forest_flux_deadwood_carbon_stock_in_emissions_year',
    ]

    all_data = []
    for dataset in datasets:
        # Get the dataset from the URL parameters or use a default value
        datasetss = request.args.get('dataset', dataset)
        
        # Get owner type and ID (this should be passed as arguments in the URL)
        owner_type = request.args.get('owner_type', 'farmer')  # default to 'farmer'
        owner_id = request.args.get('owner_id')

        if not owner_id:
            return jsonify({"error": "Owner ID is required"}), 400

        # Get coordinates from the database
        coordinates = get_coordinates(owner_type, owner_id)
        if not coordinates:
            return jsonify({"error": "No points found for the specified owner"}), 404
        
        geometry = {
            "type": "Polygon",
            "coordinates": [coordinates]
        }

        # Query data from the dataset
        sql_query = "SELECT COUNT(*) FROM results"
        dataset_data = query_forest_watch(datasetss, geometry, sql_query)
        
        # Extract fields dynamically, ensuring to handle cases where 'data' key might be missing
        data_fields = dataset_data.get("data", [{}])[0] if dataset_data else {}
        
        all_data.append({
            'dataset': datasetss,
            'data_fields': data_fields,
            'coordinates': geometry["coordinates"]
        })

    return render_template('gfw/view.html', all_data=all_data)

def get_coordinates(owner_type, owner_id):
    points = Point.query.filter_by(owner_type=owner_type, owner_id=owner_id).options(db.load_only(Point.longitude, Point.latitude)).all()
    coordinates = [(point.longitude, point.latitude) for point in points]
    return coordinates

def create_geojson(points, owner):
    coordinates = [(point.longitude, point.latitude) for point in points]
    shapely_polygon = ShapelyPolygon(coordinates)
    geojson_polygon = mapping(shapely_polygon)
    properties = {column.name: getattr(owner, column.name) for column in owner.__table__.columns}
    feature = Feature(geometry=geojson_polygon, properties=properties)
    return FeatureCollection([feature])