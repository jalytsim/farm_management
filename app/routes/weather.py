from datetime import datetime
import json
from flask import Blueprint, app, jsonify
from flask_cors import cross_origin
from app.utils.weather_utils import create_weather

bp = Blueprint('weather', __name__)

# Données dynamiques pour chaque région
data = {
    "Butambal": {
        "imageUrl": "https://via.placeholder.com/600x400?text=Butambal",
        "farmName": "Ferme de Butambal",
        "temperature": "25.0",
        "humidity": "60.0",
        "solarRadiation": "200.0",
        "windSpeed": "2.0",
        "pressure": "101300",
        "ET0": "5.67",  # Exemple de résultat
        "ETc": "6.80",   # Exemple de résultat
        "latitude": "0.123",
        "longitude": "0.456"
    },
    "Lwengo": {
        "imageUrl": "https://via.placeholder.com/600x400?text=Lwengo",
        "farmName": "Ferme de Lwengo",
        "temperature": "22.5",
        "humidity": "65.0",
        "solarRadiation": "180.0",
        "windSpeed": "1.5",
        "pressure": "100800",
        "ET0": "4.23",  # Exemple de résultat
        "ETc": "5.15",   # Exemple de résultat
        "latitude": "1.123",
        "longitude": "1.456"
    },
    "Mukono": {
        "imageUrl": "https://via.placeholder.com/600x400?text=Mukono",
        "farmName": "Ferme de Mukono",
        "temperature": "24.0",
        "humidity": "55.0",
        "solarRadiation": "210.0",
        "windSpeed": "2.5",
        "pressure": "101500",
        "ET0": "6.12",  # Exemple de résultat
        "ETc": "7.25",   # Exemple de résultat
        "latitude": "2.123",
        "longitude": "2.456"
    }
}

@bp.route('/weather', methods=['GET'])
@cross_origin()  # Permet à toutes les origines de faire des requêtes à cette route
def weather():
    return jsonify(data)

@bp.route('/upload-weather-data', methods=['GET'])
@cross_origin()
def uploadWeather():
    json_file_path = f'D:\\project\Brian\\farm_management\\Weather_data.json'
    insert_weather_data_from_json(json_file_path)
    return jsonify({"status": "success"}), 200



def insert_weather_data_from_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    latitude = data['meta']['lat']
    longitude = data['meta']['lng']
    
    for hour in data['hours']:
        # Extract data for each parameter
        weather_data = {
            'latitude': latitude,
            'longitude': longitude,
            'air_temperature': hour.get('airTemperature', {}).get('noaa',None),
            'air_temperature_80m': hour.get('airTemperature80m', {}).get('noaa',None),
            'air_temperature_100m': hour.get('airTemperature100m', {}).get('noaa',None),
            'air_temperature_1000hpa': hour.get('airTemperature1000hpa', {}).get('noaa',None),
            'air_temperature_800hpa': hour.get('airTemperature800hpa', {}).get('noaa',None),
            'air_temperature_500hpa': hour.get('airTemperature500hpa', {}).get('noaa',None),
            'air_temperature_200hpa': hour.get('airTemperature200hpa', {}).get('noaa',None),
            'pressure': hour.get('pressure', {}).get('noaa',None),
            'cloud_cover': hour.get('cloudCover', {}).get('noaa',None),
            'current_direction': hour.get('currentDirection', {}).get('noaa',None),
            'current_speed': hour.get('currentSpeed', {}).get('noaa',None),
            'gust': hour.get('gust', {}).get('noaa',None),
            'humidity': hour.get('humidity', {}).get('noaa',None),
            'ice_cover': hour.get('iceCover', {}).get('noaa',None),
            'precipitation': hour.get('precipitation', {}).get('noaa',None),
            'snow_depth': hour.get('snowDepth', {}).get('noaa',None),
            'sea_level': hour.get('seaLevel', {}).get('noaa',None),
            'swell_direction': hour.get('swellDirection', {}).get('noaa',None),
            'swell_height': hour.get('swellHeight', {}).get('noaa',None),
            'swell_period': hour.get('swellPeriod', {}).get('noaa',None),
            'secondary_swell_period': hour.get('secondarySwellPeriod', {}).get('noaa',None),
            'secondary_swell_direction': hour.get('secondarySwellDirection', {}).get('noaa',None),
            'secondary_swell_height': hour.get('secondarySwellHeight', {}).get('noaa',None),
            'visibility': hour.get('visibility', {}).get('noaa',None),
            'water_temperature': hour.get('waterTemperature', {}).get('noaa',None),
            'wave_direction': hour.get('waveDirection', {}).get('noaa',None),
            'wave_height': hour.get('waveHeight', {}).get('noaa',None),
            'wave_period': hour.get('wavePeriod', {}).get('noaa',None),
            'wind_wave_direction': hour.get('windWaveDirection', {}).get('noaa',None),
            'wind_wave_height': hour.get('windWaveHeight', {}).get('noaa',None),
            'wind_wave_period': hour.get('windWavePeriod', {}).get('noaa',None),
            'wind_direction': hour.get('windDirection', {}).get('noaa',None),
            'wind_direction_20m': hour.get('windDirection20m', {}).get('noaa',None),
            'wind_direction_30m': hour.get('windDirection30m', {}).get('noaa',None),
            'wind_direction_40m': hour.get('windDirection40m', {}).get('noaa',None),
            'wind_direction_50m': hour.get('windDirection50m', {}).get('noaa',None),
            'wind_direction_80m': hour.get('windDirection80m', {}).get('noaa',None),
            'wind_direction_100m': hour.get('windDirection100m', {}).get('noaa',None),
            'wind_direction_1000hpa': hour.get('windDirection1000hpa', {}).get('noaa',None),
            'wind_direction_800hpa': hour.get('windDirection800hpa', {}).get('noaa',None),
            'wind_direction_500hpa': hour.get('windDirection500hpa', {}).get('noaa',None),
            'wind_direction_200hpa': hour.get('windDirection200hpa', {}).get('noaa',None),
            'wind_speed': hour.get('windSpeed', {}).get('noaa',None),
            'wind_speed_20m': hour.get('windSpeed20m', {}).get('noaa',None),
            'wind_speed_30m': hour.get('windSpeed30m', {}).get('noaa',None),
            'wind_speed_40m': hour.get('windSpeed40m', {}).get('noaa',None),
            'wind_speed_50m': hour.get('windSpeed50m', {}).get('noaa',None),
            'wind_speed_80m': hour.get('windSpeed80m', {}).get('noaa',None),
            'wind_speed_100m': hour.get('windSpeed100m', {}).get('noaa',None),
            'wind_speed_1000hpa': hour.get('windSpeed1000hpa', {}).get('noaa',None),
            'wind_speed_800hpa': hour.get('windSpeed800hpa', {}).get('noaa',None),
            'wind_speed_500hpa': hour.get('windSpeed500hpa', {}).get('noaa',None),
            'wind_speed_200hpa': hour.get('windSpeed200hpa', {}).get('noaa',None),
            'date_created': datetime.utcnow(),
            'date_updated': datetime.utcnow(),
        }

        # Create the weather record
        create_weather(weather_data)
# Example usage
