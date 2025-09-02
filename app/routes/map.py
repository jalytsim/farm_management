from flask import Blueprint
from app.models import Point
from app.utils.forest_watch_utils import  query_forest_watch_async
from flask import Blueprint
from app import db
from shapely.geometry import mapping, Polygon as ShapelyPolygon
from geojson import Feature, FeatureCollection
import asyncio

bp = Blueprint('map', __name__)

# def create_geojson(points, model_instance):
#     coordinates = [(point.longitude, point.latitude) for point in points]
#     shapely_polygon = ShapelyPolygon(coordinates)
#     geojson_polygon = mapping(shapely_polygon)
#     properties = {column.name: getattr(model_instance, column.name) for column in model_instance.__table__.columns}
#     properties['name'] = model_instance.name
#     feature = Feature(geometry=geojson_polygon, properties=properties)
#     feature_collection = FeatureCollection([feature])
#     return feature_collection


def get_coordinates(owner_type, owner_id):
    print(owner_type,"###############", owner_id)
    if owner_type:
        points = Point.query.filter_by(owner_type=owner_type, owner_id=owner_id).options(db.load_only(Point.longitude, Point.latitude)).all()
    else:
        return []
    coordinates = [(point.longitude, point.latitude) for point in points]
    return coordinates

# def create_geojson(points, owner):
#     coordinates = [(point.longitude, point.latitude) for point in points]
#     shapely_polygon = ShapelyPolygon(coordinates)
#     geojson_polygon = mapping(shapely_polygon)
#     properties = {column.name: getattr(owner, column.name) for column in owner.__table__.columns}
#     feature = Feature(geometry=geojson_polygon, properties=properties)
#     return FeatureCollection([feature])
async def gfw_async(owner_type, owner_id):
    datasets = [
        'gfw_radd_alerts',
        'umd_tree_cover_loss',
        'jrc_global_forest_cover',
        'wri_tropical_tree_cover_extent',
        'wri_tropical_tree_cover_percent',
        'landmark_indigenous_and_community_lands',
        'gfw_soil_carbon',
        'wur_radd_alerts',
        'tsc_tree_cover_loss_drivers',
    ]
    
    # Define pixels for each dataset
    dataset_pixels = {
        'jrc_global_forest_cover': [
            'wri_tropical_tree_cover_extent__decile',
            'is__jrc_global_forest_cover',
        ],
        'gfw_soil_carbon': [
            'wdpa_protected_areas__iucn_cat',
        ],
        'umd_tree_cover_loss': [
            'SUM(area__ha)',
        ],
        'landmark_indigenous_and_community_lands': [
            'name',
        ],
        'gfw_radd_alerts': [
            'SUM(area__ha)',
        ],
        'wri_tropical_tree_cover_extent': [
            'SUM(area__ha)',
        ],
        'wri_tropical_tree_cover_percent': [
            'SUM(area__ha)',
        ],
        'tsc_tree_cover_loss_drivers':[
            'tsc_tree_cover_loss_drivers__driver',
         ],
    }
    
    # Get coordinates
    coordinates = get_coordinates(owner_type, owner_id)
    if not coordinates:
        return {"error": "No points found for the specified owner"}, 400
    
    geometry = {
        "type": "Polygon",
        "coordinates": [coordinates]
    }
    
    tasks = []
    for dataset in datasets:
        # Get the pixels for the current dataset
        pixels = dataset_pixels.get(dataset, [])
        if not pixels:
            continue  # Skip datasets without defined pixels
        
        for pixel in pixels:
            # Construct the SQL query for each pixel
            sql_query = f"SELECT {pixel} FROM results"
            
            # Schedule the async request
            tasks.append(query_forest_watch_async(dataset, geometry, sql_query))
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Collect and structure results
    dataset_results = []
    task_index = 0
    for dataset in datasets:
        pixels = dataset_pixels.get(dataset, [])
        if not pixels:
            continue
        
        for pixel in pixels:
            result = results[task_index]
            task_index += 1
            
            if isinstance(result, Exception):
                # Handle any exceptions that occurred during requests
                data_fields = {"error": str(result)}
            else:
                # Extract fields from the response
                data = result.get("data", [])
                if len(data) == 1:
                    data_fields = data[0]  # Single record
                else:
                    data_fields = data      # Multiple records
            
            dataset_results.append({
                'dataset': dataset.replace('gfw_', '').replace('umd_', '').replace('_', ' '),
                'pixel': pixel,
                'data_fields': data_fields,
                'coordinates': geometry["coordinates"]
            })
    
    return {"dataset_results": dataset_results}, 200

async def gfw_async_carbon(owner_type, owner_id):
    datasets = [
        'gfw_forest_carbon_gross_emissions',
        'gfw_forest_carbon_gross_removals',
        'gfw_forest_carbon_net_flux',
        'gfw_full_extent_aboveground_carbon_potential_sequestration',
    ]
    
    # Define pixels for each dataset
    dataset_pixels = {
        'gfw_forest_carbon_gross_emissions': [
            'SUM(gfw_forest_carbon_gross_emissions__Mg_CO2e)',
        ],
        'gfw_forest_carbon_gross_removals': [
            'SUM(gfw_forest_carbon_gross_removals__Mg_CO2e)',
        ],
        'gfw_forest_carbon_net_flux': [
            'SUM(gfw_forest_carbon_net_flux__Mg_CO2e)',
        ],
        'gfw_full_extent_aboveground_carbon_potential_sequestration': [
            'SUM(gfw_reforestable_extent_belowground_carbon_potential_sequestration__Mg_C)',
            'SUM(gfw_reforestable_extent_aboveground_carbon_potential_sequestration__Mg_C)',
        ],
        
    }
    
    # Get coordinates
    coordinates = get_coordinates(owner_type, owner_id)
    if not coordinates:
        return {"error": "No points found for the specified owner"}, 400
    
    geometry = {
        "type": "Polygon",
        "coordinates": [coordinates]
    }
    
    tasks = []
    for dataset in datasets:
        # Get the pixels for the current dataset
        pixels = dataset_pixels.get(dataset, [])
        if not pixels:
            continue  # Skip datasets without defined pixels
        
        for pixel in pixels:
            # Construct the SQL query for each pixel
            sql_query = f"SELECT {pixel} FROM results"
            
            # Schedule the async request
            tasks.append(query_forest_watch_async(dataset, geometry, sql_query))
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Collect and structure results
    dataset_results = []
    task_index = 0
    for dataset in datasets:
        pixels = dataset_pixels.get(dataset, [])
        if not pixels:
            continue
        
        for pixel in pixels:
            result = results[task_index]
            task_index += 1
            
            if isinstance(result, Exception):
                # Handle any exceptions that occurred during requests
                data_fields = {"error": str(result)}
            else:
                # Extract fields from the response
                data = result.get("data", [])
                if len(data) == 1:
                    data_fields = data[0]  # Single record
                else:
                    data_fields = data      # Multiple records
            
            dataset_results.append({
                'dataset': dataset.replace('gfw_', '').replace('umd_', '').replace('_', ' '),
                'pixel': pixel,
                'data_fields': data_fields,
                'coordinates': geometry["coordinates"]
            })
    
    return {"dataset_results": dataset_results}, 200


import asyncio

async def gfw_async_from_geojson(geojson_geometry):
    datasets = [
        'gfw_radd_alerts',
        'umd_tree_cover_loss',
        'jrc_global_forest_cover',
        'wri_tropical_tree_cover_extent',
        'wri_tropical_tree_cover_percent',
        'landmark_indigenous_and_community_lands',
        'gfw_soil_carbon',
        'wur_radd_alerts',
        'tsc_tree_cover_loss_drivers',
        'gfw_soil_carbon_stocks',
    ]

    dataset_pixels = {
        'jrc_global_forest_cover': [
            'is__jrc_global_forest_cover',
            
        ],
        'gfw_soil_carbon': [
            'wdpa_protected_areas__iucn_cat',
        ],
        'umd_tree_cover_loss': [
            'SUM(area__ha)',
        ],
        'landmark_indigenous_and_community_lands': [
            'name',
        ],
        'gfw_radd_alerts': [
            'SUM(area__ha)',
        ],
        'wri_tropical_tree_cover_extent': [
            'SUM(area__ha)',
        ],
        'wri_tropical_tree_cover_percent': [
            'SUM(area__ha)',
        ],
        'tsc_tree_cover_loss_drivers':[
            'tsc_tree_cover_loss_drivers__driver',
         ],
         'gfw_soil_carbon_stocks': [
            'SUM(area__ha)',
        ],
    }

    # Valider que la géométrie est au bon format
    if not geojson_geometry or not isinstance(geojson_geometry, dict):
        return {"error": "Invalid or missing GeoJSON geometry"}, 400

    # Extraire le polygon
    if geojson_geometry.get("type") == "FeatureCollection":
        features = geojson_geometry.get("features", [])
        polygon_feature = next((f for f in features if f["geometry"]["type"] == "Polygon"), None)
        if not polygon_feature:
            return {"error": "No valid Polygon found in FeatureCollection"}, 400
        geometry = polygon_feature["geometry"]
    elif geojson_geometry.get("type") == "Polygon":
        geometry = geojson_geometry
    else:
        return {"error": "Unsupported GeoJSON geometry type"}, 400

    tasks = []
    for dataset in datasets:
        pixels = dataset_pixels.get(dataset, [])
        if not pixels:
            continue

        for pixel in pixels:
            sql_query = f"SELECT {pixel} FROM results"
            tasks.append(query_forest_watch_async(dataset, geometry, sql_query))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    dataset_results = []
    task_index = 0
    for dataset in datasets:
        pixels = dataset_pixels.get(dataset, [])
        if not pixels:
            continue

        for pixel in pixels:
            result = results[task_index]
            task_index += 1

            if isinstance(result, Exception):
                data_fields = {"error": str(result)}
            else:
                data = result.get("data", [])
                data_fields = data[0] if len(data) == 1 else data

            dataset_results.append({
                'dataset': dataset.replace('gfw_', '').replace('umd_', '').replace('_', ' '),
                'pixel': pixel,
                'data_fields': data_fields,
                'coordinates': geometry["coordinates"]
            })

    return {"dataset_results": dataset_results}, 200

async def gfw_async_carbon_from_geojson(geojson_data):
    print("tonga atoa minny utils")
    print(geojson_data)

    datasets = [
        'gfw_forest_carbon_gross_emissions',
        'gfw_forest_carbon_gross_removals',
        'gfw_forest_carbon_net_flux',
        'gfw_full_extent_aboveground_carbon_potential_sequestration',
    ]

    dataset_pixels = {
        'gfw_forest_carbon_gross_emissions': [
            'SUM(gfw_forest_carbon_gross_emissions__Mg_CO2e)',
        ],
        'gfw_forest_carbon_gross_removals': [
            'SUM(gfw_forest_carbon_gross_removals__Mg_CO2e)',
        ],
        'gfw_forest_carbon_net_flux': [
            'SUM(gfw_forest_carbon_net_flux__Mg_CO2e)',
        ],
        'gfw_full_extent_aboveground_carbon_potential_sequestration': [
            'SUM(gfw_reforestable_extent_belowground_carbon_potential_sequestration__Mg_C)',
            'SUM(gfw_reforestable_extent_aboveground_carbon_potential_sequestration__Mg_C)',
        ],
    }

    # Extraction géométrie
    if geojson_data.get("type") == "FeatureCollection":
        features = geojson_data.get("features", [])
        if not features or "geometry" not in features[0]:
            return {"error": "Invalid or missing geometry in GeoJSON"}, 400
        geometry = features[0]["geometry"]
    elif geojson_data.get("type") == "Feature":
        geometry = geojson_data.get("geometry")
    else:
        geometry = geojson_data  # Peut déjà être une géométrie directe

    if not geometry or geometry.get("type") != "Polygon" or not geometry.get("coordinates"):
        return {"error": "Invalid or missing geometry in GeoJSON"}, 400

    # Lancer les requêtes asynchrones
    tasks = []
    for dataset in datasets:
        pixels = dataset_pixels.get(dataset, [])
        for pixel in pixels:
            sql_query = f"SELECT {pixel} FROM results"
            tasks.append(query_forest_watch_async(dataset, geometry, sql_query))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    dataset_results = []
    task_index = 0
    for dataset in datasets:
        pixels = dataset_pixels.get(dataset, [])
        for pixel in pixels:
            result = results[task_index]
            task_index += 1

            if isinstance(result, Exception):
                data_fields = {"error": str(result)}
            else:
                data = result.get("data", [])
                data_fields = data[0] if len(data) == 1 else data

            dataset_results.append({
                'dataset': dataset.replace('gfw_', '').replace('umd_', '').replace('_', ' ').strip(),
                'pixel': pixel,
                'data_fields': data_fields,
                'coordinates': geometry.get("coordinates", [])
            })

    print("ato amin'ny utils", dataset_results)

    return {"dataset_results": dataset_results}, 200
