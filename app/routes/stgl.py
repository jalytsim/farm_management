from datetime import date, datetime
import arrow
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import requests

from app.utils.solar_utils import insert_solar_data
from app.utils.weather_utils import insert_weather_data

bp = Blueprint('stgl', __name__)


@bp.route('/stgl', methods=['GET'])
@cross_origin()  # Permet à toutes les origines de faire des requêtes à cette route
def stgl():

    
    return jsonify({'status': 'success'}) 


@bp.route('/getWeather', methods=['GET'])
@cross_origin()  # Permet à toutes les origines de faire des requêtes à cette route
def get_weather():
    lat = request.args.get('lat', default='0.536279', type=str)
    lon = request.args.get('lon', default='32.589248', type=str)
    # Get first hour of today
    start = arrow.now().floor('day')
    # Get last hour of today
    end = arrow.now().ceil('day')
    # List of all parameters
    params_list = [
        'airTemperature', 'airTemperature80m', 'airTemperature100m', 'airTemperature1000hpa', 'airTemperature800hpa', 
        'airTemperature500hpa', 'airTemperature200hpa', 'pressure', 'cloudCover', 'currentDirection', 'currentSpeed', 
        'gust', 'humidity', 'iceCover', 'precipitation', 'snowDepth', 'seaLevel', 'swellDirection', 'swellHeight', 
        'swellPeriod', 'secondarySwellPeriod', 'secondarySwellDirection', 'secondarySwellHeight', 'visibility', 
        'waterTemperature', 'waveDirection', 'waveHeight', 'wavePeriod', 'windWaveDirection', 'windWaveHeight', 
        'windWavePeriod', 'windDirection', 'windDirection20m', 'windDirection30m', 'windDirection40m', 'windDirection50m', 
        'windDirection80m', 'windDirection100m', 'windDirection1000hpa', 'windDirection800hpa', 'windDirection500hpa', 
        'windDirection200hpa', 'windSpeed', 'windSpeed20m', 'windSpeed30m', 'windSpeed40m', 'windSpeed50m', 'windSpeed80m', 
        'windSpeed100m', 'windSpeed1000hpa', 'windSpeed800hpa', 'windSpeed500hpa', 'windSpeed200hpa'
    ]
    response = requests.get(
        'https://api.stormglass.io/v2/weather/point',
        params={
            'lat': lat,
            'lng': lon,
            'params': ','.join(params_list),
            # 'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
            # 'end': end.to('UTC').timestamp()  # Convert to UTC timestamp
        },
        headers={
            'Authorization': 'a6b685ea-5014-11ef-8a8f-0242ac130004-a6b68676-5014-11ef-8a8f-0242ac130004'
        }
    )

    # Get JSON data from the response
    json_data = response.json()
    print(json_data)

    # Insert data into the database
    insert_weather_data(json_data)

    return jsonify({'status': 'success', 'response': json_data}) 


@bp.route('/getSolar', methods=['GET'])
@cross_origin()  # Permet à toutes les origines de faire des requêtes à cette route
def get_solar():    
    lat = request.args.get('lat', default='0.536279', type=str)
    lon = request.args.get('lon', default='32.589248', type=str)
    # Get first hour of today
    start = arrow.now().floor('day')

    # Get last hour of today
    end = arrow.now().ceil('day')

    # List of all parameters
    params_list = [
        'uvIndex', 'downwardShortWaveRadiationFlux'
    ]

    response = requests.get(
        'https://api.stormglass.io/v2/solar/point',
        params={
            'lat': lat,
            'lng': lon,
            'params': ','.join(params_list),
            # 'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
            # 'end': end.to('UTC').timestamp()  # Convert to UTC timestamp
        },
        headers={
            'Authorization': '6c63097c-fd08-11ee-a75c-0242ac130002-6c630a3a-fd08-11ee-a75c-0242ac130002'
        }
    )

    # Get JSON data from the response
    json_data = response.json()
    print(json_data)

    # Insert data into the database
    insert_solar_data(json_data)

    return jsonify({'status': 'success', 'response': json_data})

# url = url_for('weather.get_solar', lat='0.292225', lon='32.576809')