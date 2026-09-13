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
            # ✅ FIX : l'API GFW renvoie systématiquement `data: []` quand la requête
            # utilise GROUP BY sur ce champ contextuel (vérifié en direct sur un
            # polygone réel de la DB : `... GROUP BY wdpa_protected_areas__iucn_cat`
            # → 0 ligne, alors qu'une requête SANS group_by renvoie bien la valeur
            # par pixel). On récupère donc la valeur brute par pixel et on
            # l'agrège nous-mêmes dans pdf_reports.py (compatible avec le format
            # existant : chaque ligne sans 'count' compte pour 1 pixel).
            'gfw_soil_carbon': [
                {'select': 'wdpa_protected_areas__iucn_cat'},
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
                {'select' : 'wri_tropical_tree_cover_extent__decile, longitude, latitude'},
            ],
            'wri_tropical_tree_cover': [
                {'select': 'AVG(wri_tropical_tree_cover__percent) as avg_cover, SUM(area__ha)'},
            ],
            'tsc_tree_cover_loss_drivers': [
                {'select': 'tsc_tree_cover_loss_drivers__driver', 'group_by': 'tsc_tree_cover_loss_drivers__driver'},
                {'select': 'tsc_tree_cover_loss_drivers__driver,longitude, latitude'},
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


# ✅ FIX : types de géométrie acceptés. L'ancien code exigeait STRICTEMENT
# "Polygon" et rejetait tout le reste (notamment "MultiPolygon", que Mapbox
# GL Draw ou certains exports QGIS produisent couramment pour des polygones
# pourtant parfaitement valides) → 400 "No valid Polygon found" même quand
# la géométrie était correcte. L'API Global Forest Watch accepte les deux.
_ACCEPTED_GEOMETRY_TYPES = {'Polygon', 'MultiPolygon'}


def _is_usable_geometry(geometry):
    """True si geometry est un dict GeoJSON exploitable (Polygon/MultiPolygon
    avec des coordonnées présentes). Ne lève jamais d'exception, contrairement
    à l'ancien accès direct f["geometry"]["type"] qui plantait avec KeyError
    dès qu'une feature n'avait pas (ou mal) de champ 'geometry'."""
    if not isinstance(geometry, dict):
        return False
    if geometry.get('type') not in _ACCEPTED_GEOMETRY_TYPES:
        return False
    return bool(geometry.get('coordinates'))


def extract_geometry(input_data, is_geojson=False):
    """
    Extract Polygon/MultiPolygon geometry from owner_type/owner_id or GeoJSON data.
    Always returns a 3-tuple: (geometry, error_response, status_code)
    - On success : (geometry, None, 200)
    - On error   : (None, {"error": "..."}, 4xx)
    """
    if is_geojson:
        if not input_data or not isinstance(input_data, dict):
            return None, {"error": "Invalid or missing GeoJSON geometry"}, 400

        top_type = input_data.get("type")

        if top_type == "FeatureCollection":
            features = input_data.get("features", []) or []
            # ✅ FIX : .get() partout au lieu de f["geometry"]["type"] — une
            # feature sans géométrie (ou géométrie None) est simplement
            # ignorée au lieu de faire planter toute la requête.
            geometry = next(
                (f.get("geometry") for f in features if _is_usable_geometry(f.get("geometry"))),
                None,
            )
            if geometry is None:
                found_types = sorted({
                    (f.get("geometry") or {}).get("type")
                    for f in features if f.get("geometry")
                })
                detail = f" (types trouvés : {', '.join(t for t in found_types if t)})" if found_types else ""
                return None, {"error": f"No valid Polygon/MultiPolygon found in FeatureCollection{detail}"}, 400

        elif top_type == "Feature":
            geometry = input_data.get("geometry")
            if not _is_usable_geometry(geometry):
                found = (geometry or {}).get("type", "missing")
                return None, {"error": f"Unsupported geometry type in Feature: {found}"}, 400

        elif top_type in _ACCEPTED_GEOMETRY_TYPES:
            geometry = input_data
            if not _is_usable_geometry(geometry):
                return None, {"error": "Geometry has no coordinates"}, 400

        else:
            return None, {"error": f"Unsupported GeoJSON type: {top_type}"}, 400

    else:
        coordinates = get_coordinates(*input_data)
        if not coordinates:
            return None, {"error": "No points found for the specified owner"}, 400
        geometry = {"type": "Polygon", "coordinates": [coordinates]}

    # ★ Toujours 3 valeurs — plus jamais de ValueError
    return geometry, None, 200


async def process_datasets(datasets, dataset_pixels, geometry):
    """Process datasets with their pixel definitions and execute async queries."""
    tasks = []
    for dataset in datasets:
        pixels = dataset_pixels.get(dataset, [])
        if not pixels:
            continue

        for pixel in pixels:
            select_expr  = pixel.get("select")
            where_expr   = pixel.get("where")
            group_by_expr= pixel.get("group_by")
            having_expr  = pixel.get("having")
            order_by_expr= pixel.get("order_by")
            limit_expr   = pixel.get("limit")

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
    sql_query = None

    for dataset in datasets:
        pixels = dataset_pixels.get(dataset, [])
        if not pixels:
            continue

        for pixel in pixels:
            result = results[task_index]
            task_index += 1

            if isinstance(result, Exception):
                data_fields = {"error": str(result)}
                is_grouped  = False
            else:
                data       = result.get("data", [])
                is_grouped = pixel.get("group_by") is not None
                data_fields = data if is_grouped else (data[0] if len(data) == 1 else data)

            select_expr = pixel.get("select")
            sql_parts   = [f"SELECT {select_expr} FROM results"]
            if pixel.get("where"):
                sql_parts.append(f"WHERE {pixel['where']}")
            if pixel.get("group_by"):
                sql_parts.append(f"GROUP BY {pixel['group_by']}")
            sql_query = " ".join(sql_parts)

            pixel_label = select_expr
            if pixel.get("group_by"):
                pixel_label += f" (grouped by {pixel['group_by']})"

            dataset_results.append({
                'dataset':           dataset.replace('gfw_', '').replace('umd_', '').replace('_', ' ').strip(),
                'pixel':             pixel_label,
                'data_fields':       data_fields,
                'is_grouped_result': is_grouped,
                'coordinates':       geometry["coordinates"],
                'sql_query':         sql_query,
            })

    return {"dataset_results": dataset_results}, 200


async def query_forest_watch(input_data, is_geojson=False, dataset_type='general'):
    """Query forest watch datasets for owner_type/owner_id or GeoJSON geometry."""
    datasets       = DATASET_CONFIG[dataset_type]['datasets']
    dataset_pixels = DATASET_CONFIG[dataset_type]['pixels']

    # ★ Toujours 3 valeurs maintenant
    geometry, error_response, status_code = extract_geometry(input_data, is_geojson)
    if error_response:
        return error_response, status_code

    results = await process_datasets(datasets, dataset_pixels, geometry)
    return format_results(datasets, dataset_pixels, results, geometry)


# ── Legacy wrappers ───────────────────────────────────────────────────────────

async def gfw_async(owner_type, owner_id):
    """Legacy wrapper — general forest watch queries."""
    return await query_forest_watch((owner_type, owner_id), is_geojson=False, dataset_type='general')

async def gfw_async_carbon(owner_type, owner_id):
    """Legacy wrapper — carbon-related queries."""
    return await query_forest_watch((owner_type, owner_id), is_geojson=False, dataset_type='carbon')

async def gfw_async_from_geojson(geojson_geometry):
    """Legacy wrapper — general forest watch queries with GeoJSON."""
    return await query_forest_watch(geojson_geometry, is_geojson=True, dataset_type='general')

async def gfw_async_carbon_from_geojson(geojson_data):
    """Legacy wrapper — carbon-related queries with GeoJSON."""
    return await query_forest_watch(geojson_data, is_geojson=True, dataset_type='carbon')