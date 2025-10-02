from flask import Blueprint
from app.models import Point
from app.utils.forest_watch_utils import query_forest_watch_async
from app import db
import asyncio

bp = Blueprint('map', __name__)

# Dataset configuration
DATASET_CONFIG = {
    'general': {
        'datasets': [
            'gfw_radd_alerts',
            'umd_tree_cover_loss',
            'jrc_global_forest_cover',
            'wri_tropical_tree_cover_extent',
            'wri_tropical_tree_cover',
            'landmark_indigenous_and_community_lands',
            'gfw_soil_carbon',
            'wur_radd_alerts',
            'tsc_tree_cover_loss_drivers',
            'gfw_soil_carbon_stocks',
        ],
        'pixels': {
            'jrc_global_forest_cover': [
                {'select': 'SUM(area__ha)', 'where': 'is__jrc_global_forest_cover > 0'},
            ],
            'gfw_soil_carbon': [
                {'select': 'wdpa_protected_areas__iucn_cat, COUNT(*) as count', 'group_by': 'wdpa_protected_areas__iucn_cat'},
            ],
            'umd_tree_cover_loss': [
                {'select': 'SUM(area__ha)'},
            ],
            'landmark_indigenous_and_community_lands': [
                {'select': 'name'},
            ],
            'wur_radd_alerts': [
                {'select': 'SUM(area__ha)'},
            ],
            'wri_tropical_tree_cover_extent': [
                {'select': 'wri_tropical_tree_cover_extent__decile, COUNT(*) as pixel_count', 'group_by': 'wri_tropical_tree_cover_extent__decile'},
                {'select': 'AVG(wri_tropical_tree_cover_extent__decile) as overall_avg'},
            ],
            'wri_tropical_tree_cover': [
                {'select': 'AVG(wri_tropical_tree_cover__percent) as avg_cover, SUM(area__ha)'},
            ],
            'tsc_tree_cover_loss_drivers': [
                {'select': 'tsc_tree_cover_loss_drivers__driver', 'group_by': 'tsc_tree_cover_loss_drivers__driver'},
            ],
            'gfw_soil_carbon_stocks': [
                {'select': 'SUM(area__ha)'},
            ],
            'gfw_radd_alerts': [
                {'select': 'SUM(area__ha)'},
            ],
            'wri_tropical_tree_cover_percent': [
                {'select': 'SUM(area__ha)'},
            ],
        }
    },
    'carbon': {
        'datasets': [
            'gfw_forest_carbon_gross_emissions',
            'gfw_forest_carbon_gross_removals',
            'gfw_forest_carbon_net_flux',
            'gfw_full_extent_aboveground_carbon_potential_sequestration',
        ],
        'pixels': {
            'gfw_forest_carbon_gross_emissions': [
                {'select': 'SUM(gfw_forest_carbon_gross_emissions__Mg_CO2e)'},
            ],
            'gfw_forest_carbon_gross_removals': [
                {'select': 'SUM(gfw_forest_carbon_gross_removals__Mg_CO2e)'},
            ],
            'gfw_forest_carbon_net_flux': [
                {'select': 'SUM(gfw_forest_carbon_net_flux__Mg_CO2e)'},
            ],
            'gfw_full_extent_aboveground_carbon_potential_sequestration': [
                {'select': 'SUM(gfw_reforestable_extent_belowground_carbon_potential_sequestration__Mg_C)'},
                {'select': 'SUM(gfw_reforestable_extent_aboveground_carbon_potential_sequestration__Mg_C)'},
            ],
        }
    }
}

def get_coordinates(owner_type, owner_id):
    """Retrieve coordinates for a given owner_type and owner_id."""
    if owner_type and owner_id:
        points = Point.query.filter_by(owner_type=owner_type, owner_id=owner_id).options(db.load_only(Point.longitude, Point.latitude)).all()
        return [(point.longitude, point.latitude) for point in points]
    return []

def extract_geometry(input_data, is_geojson=False):
    """Extract Polygon geometry from owner_type/owner_id or GeoJSON data."""
    if is_geojson:
        if not input_data or not isinstance(input_data, dict):
            return None, {"error": "Invalid or missing GeoJSON geometry"}, 400

        if input_data.get("type") == "FeatureCollection":
            features = input_data.get("features", [])
            polygon_feature = next((f for f in features if f["geometry"]["type"] == "Polygon"), None)
            if not polygon_feature:
                return None, {"error": "No valid Polygon found in FeatureCollection"}, 400
            geometry = polygon_feature["geometry"]
        elif input_data.get("type") == "Feature":
            geometry = input_data.get("geometry")
        elif input_data.get("type") == "Polygon":
            geometry = input_data
        else:
            return None, {"error": "Unsupported GeoJSON geometry type"}, 400

        if geometry.get("type") != "Polygon" or not geometry.get("coordinates"):
            return None, {"error": "Invalid or missing geometry in GeoJSON"}, 400
    else:
        coordinates = get_coordinates(*input_data)
        if not coordinates:
            return None, {"error": "No points found for the specified owner"}, 400
        geometry = {"type": "Polygon", "coordinates": [coordinates]}

    return geometry, None

async def process_datasets(datasets, dataset_pixels, geometry):
    """Process datasets with their pixel definitions and execute async queries."""
    tasks = []
    for dataset in datasets:
        pixels = dataset_pixels.get(dataset, [])
        if not pixels:
            continue

        for pixel in pixels:
            select_expr = pixel.get("select")
            where_expr = pixel.get("where")
            group_by_expr = pixel.get("group_by")
            having_expr = pixel.get("having")
            order_by_expr = pixel.get("order_by")
            limit_expr = pixel.get("limit")

            sql_parts = [f"SELECT {select_expr} FROM results"]
            if where_expr:
                sql_parts.append(f"WHERE {where_expr}")
            if group_by_expr:
                sql_parts.append(f"GROUP BY {group_by_expr}")
            if having_expr:
                sql_parts.append(f"HAVING {having_expr}")
            if order_by_expr:
                sql_parts.append(f"ORDER BY {order_by_expr}")
            if limit_expr:
                sql_parts.append(f"LIMIT {limit_expr}")
            sql_query = " ".join(sql_parts)

            tasks.append(query_forest_watch_async(dataset, geometry, sql_query))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

def format_results(datasets, dataset_pixels, results, geometry):
    """Format query results into a structured response."""
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
                is_grouped = False
            else:
                data = result.get("data", [])
                is_grouped = pixel.get("group_by") is not None
                data_fields = data if is_grouped else (data[0] if len(data) == 1 else data)

            pixel_label = pixel.get("select")
            if pixel.get("group_by"):
                pixel_label += f" (grouped by {pixel['group_by']})"

            dataset_results.append({
                'dataset': dataset.replace('gfw_', '').replace('umd_', '').replace('_', ' ').strip(),
                'pixel': pixel_label,
                'data_fields': data_fields,
                'is_grouped_result': is_grouped,
                'coordinates': geometry["coordinates"],
                'sql_query': sql_query if 'sql_query' in locals() else None
            })

    return {"dataset_results": dataset_results}, 200

async def query_forest_watch(input_data, is_geojson=False, dataset_type='general'):
    """Query forest watch datasets for owner_type/owner_id or GeoJSON geometry."""
    datasets = DATASET_CONFIG[dataset_type]['datasets']
    dataset_pixels = DATASET_CONFIG[dataset_type]['pixels']

    geometry, error_response = extract_geometry(input_data, is_geojson)
    if error_response:
        return error_response

    results = await process_datasets(datasets, dataset_pixels, geometry)
    return format_results(datasets, dataset_pixels, results, geometry)

# Example usage for different scenarios
async def gfw_async(owner_type, owner_id):
    """Legacy wrapper for general forest watch queries with owner_type and owner_id."""
    return await query_forest_watch((owner_type, owner_id), is_geojson=False, dataset_type='general')

async def gfw_async_carbon(owner_type, owner_id):
    """Legacy wrapper for carbon-related queries with owner_type and owner_id."""
    return await query_forest_watch((owner_type, owner_id), is_geojson=False, dataset_type='carbon')

async def gfw_async_from_geojson(geojson_geometry):
    """Legacy wrapper for general forest watch queries with GeoJSON geometry."""
    return await query_forest_watch(geojson_geometry, is_geojson=True, dataset_type='general')

async def gfw_async_carbon_from_geojson(geojson_data):
    """Legacy wrapper for carbon-related queries with GeoJSON geometry."""
    return await query_forest_watch(geojson_data, is_geojson=True, dataset_type='carbon')