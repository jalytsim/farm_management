import json
import plotly.express as px
import pandas as pd
from flask import current_app as app
from sqlalchemy import func
from ..models import db, FarmData, Farm, District, SoilData

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
