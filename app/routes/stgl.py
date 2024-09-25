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
    lat = request.args.get('lat', default='0.358261', type=str)
    lon = request.args.get('lon', default='32.654738', type=str)

    # specify date
    # specified_date = arrow.get(2024, 9, 20)
    # start = specified_date.floor('day')

    # Get first hour of today
    start_param = request.args.get('start', type=str)
    end_param = request.args.get('end', type=str)

    # specified_date = arrow.get(2024, 9, 20)
    # start = specified_date.floor('day')
    # Get first hour of today
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
    params={
            'lat': lat,
            'lng': lon,
            'params': ','.join(params_list),
        }
    if start_param:
        params['start'] = arrow.get(start_param).to('UTC').timestamp()
    if end_param:
        params['end'] = arrow.get(end_param).to('UTC').timestamp()
    
    response = requests.get(
        'https://api.stormglass.io/v2/weather/point',
        params=params,
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
@cross_origin()
def get_solar():    
    lat = request.args.get('lat', default='0.358261', type=str)
    lon = request.args.get('lon', default='32.654738', type=str)
    
    start_param = request.args.get('start', type=str)
    end_param = request.args.get('end', type=str)

    # Prepare request parameters
    params = {
        'lat': lat,
        'lng': lon,
        'params': ','.join(['uvIndex', 'downwardShortWaveRadiationFlux'])
    }

    # Add start and end only if provided
    if start_param:
        params['start'] = arrow.get(start_param).to('UTC').timestamp()
    if end_param:
        params['end'] = arrow.get(end_param).to('UTC').timestamp()

    response = requests.get(
        'https://api.stormglass.io/v2/solar/point',
        params=params,
        headers={
            'Authorization': '6c63097c-fd08-11ee-a75c-0242ac130002-6c630a3a-fd08-11ee-a75c-0242ac130002'
        }
    )

    json_data = response.json()
    print(json_data)
    insert_solar_data(json_data)

    return jsonify({'status': 'success', 'response': json_data})
