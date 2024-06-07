import json
import random
import plotly.express as px
import pandas as pd
from flask import current_app as app
from sqlalchemy import func

from app.utils.point_utils import get_points_by_forest_id
from ..models import db, FarmData, Farm, District, SoilData
import plotly.graph_objects as go

def load_geojson(file_path):
    try:
        with open(file_path, encoding='utf-8') as geojson_file:
            return json.load(geojson_file)
    except Exception as e:
        print(f"Error loading GeoJSON file: {e}")
        return None

def generate_choropleth_map(data_variable='actual_yield', start_date=None, end_date=None, crop=None):
    geojson_file_path = app.config['GEOJSON_FILE_PATH']
    uganda_geojson = load_geojson(geojson_file_path)
    
    if not uganda_geojson:
        return None

    try:
        query = db.session.query(
            District.name.label('District'),
            func.sum(getattr(FarmData, data_variable)).label(f'Total{data_variable}')
        ).join(Farm, FarmData.farm_id == Farm.id).join(District, Farm.district_id == District.id)
        
        if start_date and end_date:
            query = query.filter(FarmData.planting_date.between(start_date, end_date))
        if crop:
            query = query.filter(FarmData.crop_id == crop)
        
        query = query.group_by(District.name).all()
        
        data = [{'Subcounty': district, f'Total{data_variable}': total} for district, total in query]

        df = pd.DataFrame(data)
        color_scale = 'Greens' if data_variable == 'tilled_land_size' else (
            'hot' if data_variable == 'expected_yield' else 'Blues')

        merged_data = pd.merge(df, pd.json_normalize(
            uganda_geojson['features']), left_on='Subcounty', right_on='properties.shapeName')

        fig = px.choropleth_mapbox(
            merged_data,
            geojson=uganda_geojson,
            locations='Subcounty',
            featureidkey="properties.shapeName",
            color=f'Total{data_variable}',
            color_continuous_scale=color_scale,
            mapbox_style="white-bg",
            center={"lat": 1.27, "lon": 32.29},
            zoom=6,
            title=f"Map of Uganda - {data_variable}",
            labels={f'Total{data_variable}': f'Total {data_variable}'},
            hover_data={f'Total{data_variable}': True, 'Subcounty': False},
            hover_name='Subcounty',
        )
        fig.update_layout(height=550, margin={"r": 0, "t": 40, "l": 0, "b": 0})
        return fig.to_html(full_html=False)

    except Exception as e:
        print(f"Error querying data: {e}")
        return None

def generate_choropleth_map_soil():
    geojson_file_path = app.config['GEOJSON_FILE_PATH']
    uganda_geojson = load_geojson(geojson_file_path)

    if not uganda_geojson:
        return None

    try:
        query = db.session.query(
            District.name.label('Subcounty'),
            func.avg(SoilData.nitrogen).label('AvgNitrogen'),
            func.avg(SoilData.phosphorus).label('AvgPhosphorus'),
            func.avg(SoilData.potassium).label('AvgPotassium'),
            func.avg(SoilData.ph).label('AvgPH'),
            func.avg(SoilData.temperature).label('AvgTemperature'),
            func.avg(SoilData.humidity).label('AvgHumidity'),
            func.avg(SoilData.conductivity).label('AvgConductivity'),
            func.avg(SoilData.signal_level).label('AvgSignalLevel')
        ).join(District, SoilData.district_id == District.id).group_by(District.name).all()

        data = [{'Subcounty': subcounty, 'AvgNitrogen': avg_nitrogen, 'AvgPhosphorus': avg_phosphorus,
                 'AvgPotassium': avg_potassium, 'AvgPH': avg_ph, 'AvgTemperature': avg_temp,
                 'AvgHumidity': avg_humidity, 'AvgConductivity': avg_conductivity, 'AvgSignalLevel': avg_signal}
                for subcounty, avg_nitrogen, avg_phosphorus, avg_potassium, avg_ph, avg_temp,
                    avg_humidity, avg_conductivity, avg_signal in query]

        df = pd.DataFrame(data)
        merged_data = pd.merge(df, pd.json_normalize(
            uganda_geojson['features']), left_on='Subcounty', right_on='properties.shapeName')

        fig = px.choropleth_mapbox(
            merged_data,
            geojson=uganda_geojson,
            locations='Subcounty',
            featureidkey="properties.shapeName",
            color='AvgPH',
            color_continuous_scale='Greens',
            mapbox_style="white-bg",
            center={"lat": 1.27, "lon": 32.29},
            zoom=6.3,
            title="Map of Uganda - PH Average",
            labels={'AvgNitrogen': 'Nitrogen Content'},
            hover_data={'Subcounty': False, 'AvgNitrogen': True, 'AvgPhosphorus': True, 'AvgPotassium': True,
                        'AvgPH': True, 'AvgTemperature': True, 'AvgHumidity': True, 'AvgConductivity': True, 'AvgSignalLevel': True},
            hover_name='Subcounty',
        )
        fig.update_layout(height=650, margin={"r": 0, "t": 40, "l": 0, "b": 0})
        return fig.to_html(full_html=False)

    except Exception as e:
        print(f"Error querying data: {e}")
        return None

def generate_choropleth_map_combined(highlight_region=None):
    geojson_file_path = app.config['GEOJSON_FILE_PATH']
    uganda_geojson = load_geojson(geojson_file_path)

    if not uganda_geojson:
        return None

    try:
        query = db.session.query(
            District.name.label('District'),
            func.avg(FarmData.actual_yield).label('TotalActualYield'),
            func.avg(FarmData.tilled_land_size).label('TotalTilledLandSize'),
            func.avg(FarmData.expected_yield).label('TotalExpectedYield')
        ).join(Farm, FarmData.farm_id == Farm.id).join(District, Farm.district_id == District.id)

        if highlight_region:
            query = query.filter(District.name == highlight_region)

        query = query.group_by(District.name).all()

        data = [{'Subcounty': subcounty, 'TotalActualYield': total_actual_yield, 'TotalTilledLandSize': total_tilled_land_size,
                 'TotalExpectedYield': total_expected_yield}
                for subcounty, total_actual_yield, total_tilled_land_size, total_expected_yield in query]

        df = pd.DataFrame(data)
        df['Average'] = df[['TotalActualYield',
                            'TotalTilledLandSize', 'TotalExpectedYield']].mean(axis=1)

        merged_data = pd.merge(df, pd.json_normalize(
            uganda_geojson['features']), how='right', left_on='Subcounty', right_on='properties.shapeName')

        fig = px.choropleth_mapbox(
            merged_data,
            geojson=uganda_geojson,
            locations='Subcounty',
            featureidkey="properties.shapeName",
            color='Average',
            color_continuous_scale='Blues',
            mapbox_style="white-bg",
            center={"lat": 1.27, "lon": 32.29},
            zoom=6.3 if not highlight_region else 9.3,
            title="Map of Uganda - Average Yield",
            labels={'Average': 'Average'},
            hover_data={'Subcounty': False, 'TotalActualYield': True,
                        'TotalTilledLandSize': True, 'TotalExpectedYield': True},
            hover_name='Subcounty',
        )
        fig.update_layout(height=650, margin={"r": 0, "t": 40, "l": 0, "b": 0})
        return fig.to_html(full_html=False)

    except Exception as e:
        print(f"Error querying data: {e}")
        return None


def create_mapbox_html(geojson_file, points):
    # Load GeoJSON file
    polygons = []
    for point in points:
        lat = point["lat"]
        lon = point["lon"]
        num_sides = random.randint(3, 10)
        polygon = create_polygon(lat, lon, num_sides=num_sides, radius=0.1)
        polygons.append(polygon)

    features = createGeoJSONFeature(polygons)
    collection = createGeojsonFeatureCollection(features)

    try:
        with open(geojson_file, 'w') as f:
            json.dump(collection, f)

        with open(geojson_file) as f:
            geojson_data = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading or writing GeoJSON file: {e}")
        return None

    # Create Plotly figure
    fig = go.Figure()

    # Add markers with custom hover text
    fig.add_trace(go.Scattermapbox(
        mode="markers",
        lon=[point["lon"] for point in points],
        lat=[point["lat"] for point in points],
        # Dynamic hover text
        text=[f"{point['name']}: {point['info']}" for point in points],
        marker={'size': 10, 'color': "red"},
        hoverinfo='text'
    ))

    # Add MultiPolygon to the figure with dynamic hover text
    for feature2 in geojson_data['features']:
        subcounty_name = feature2['properties'].get('Subcounty', 'Unknown')
        other_property = feature2['properties'].get(
            'OtherProperty', 'No additional info')  # Replace with actual property key
        for multipolygon in feature2['geometry']['coordinates']:
            for polygon in multipolygon:
                fig.add_trace(go.Scattermapbox(
                    fill="toself",
                    lon=[coord[0] for coord in polygon],
                    lat=[coord[1] for coord in polygon],
                    text=f'{subcounty_name}: {other_property}',
                    marker={'size': 5, 'color': "green"},
                    line=dict(width=2),
                    hoverinfo='text'
                ))

    # Determine the map center
    if len(points) == 1:
        center_coords = {"lat": points[0]["lat"], "lon": points[0]["lon"]}
    else:
        center_coords = {"lat": 1.27, "lon": 32.29}

    # Update the layout
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=center_coords,  # Center the map
            zoom=7
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    # Return the HTML of the figure
    return fig.to_html(full_html=False)

def create_mapbox_html_static(geojson_file):
    # Load GeoJSON file
    try:
        with open(geojson_file) as f:
            geojson_data = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading or writing GeoJSON file: {e}")
        return None

    # Create Plotly figure
    fig = go.Figure()

    # Add MultiPolygon to the figure with dynamic hover text
    for feature2 in geojson_data['features']:
        subcounty_name = feature2['properties'].get('Subcounty', 'Unknown')
        other_property = feature2['properties'].get(
            'OtherProperty', 'No additional info')  # Replace with actual property key
        for multipolygon in feature2['geometry']['coordinates']:
            for polygon in multipolygon:
                fig.add_trace(go.Scattermapbox(
                    fill="toself",
                    lon=[coord[0] for coord in polygon],
                    lat=[coord[1] for coord in polygon],
                    text=f'{subcounty_name}: {other_property}', 
                    marker={'size': 5, 'color': "green"},
                    line=dict(width=2),
                    hoverinfo='text'
                ))

    center_coords = {"lat": 1.27, "lon": 32.29}

    # Update the layout
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=center_coords,  # Center the map
            zoom=7
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    # Return the HTML of the figure
    return fig.to_html(full_html=False)

def create_polygon_from_db(forest_id):
    """
    Create a polygon from points in the database for a given forest_id.

    :param forest_id: ID of the forest
    :param db_config: Dictionary with database configuration (host, user, password, database)
    :return: List of tuples representing the polygon coordinates
    """
    points = get_points_by_forest_id(forest_id)

    if not points:
        raise ValueError(f"No points found for forest_id {forest_id}")

    # Assuming points are in the format [(lat1, lon1), (lat2, lon2), ...]
    # We need to transform it to [(lon1, lat1), (lon2, lat2), ...] for polygon creation
    print(points)
    polygon_coords = [(lat, lon) for lat, lon in points]

    # Close the polygon by appending the first point at the end
    if polygon_coords:
        polygon_coords.append(polygon_coords[0])
    print("Poly coords: ")
    return polygon_coords


def createGeoJSONFeature(polygons):
    multi_polygon_feature = {
        "type": "Feature",
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [[polygon] for polygon in polygons]
        },
        "properties": {}
    }

    return multi_polygon_feature


def createGeojsonFeatureCollection(multi_polygon_feature):
    geojson_data = {
        "type": "FeatureCollection",
        "features": [multi_polygon_feature]
    }

    return geojson_data

def save_polygon_to_geojson(data, filename='polygon.geojson'): 
    # Structure the points into the correct GeoJSON format

    # Write the GeoJSON data to a file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"GeoJSON data has been saved to {filename}")
   

def create_polygon(lat, lon, num_sides=6, radius=0.01):
    from math import sin, cos, pi
    coords = []
    for i in range(num_sides):
        angle = i * (2 * pi / num_sides)
        dx = radius * cos(angle)
        dy = radius * sin(angle)
        coords.append((lon + dx, lat + dy))
    coords.append(coords[0])  # close the polygon
    return coords
 
    
    
    
    
    