from datetime import datetime
import json
from flask import Blueprint, app, jsonify, request
from flask_cors import cross_origin
from app.utils.solar_utils import get_solar_data
from app.utils.weather_utils import calculate_blaney_criddle_etc, calculate_penman_et0, create_weather, get_weather_data, insert_weather_data_from_json

bp = Blueprint('weather', __name__)

# Données dynamiques pour chaque région
data = {
    "Butambal": {
        "imageUrl": "https://via.placeholder.com/600x400?text=Butambal",
        "farmName": "Ferme de Butambal",
        "latitude": "0.123",
        "longitude": "0.456",
        "timestamp": '2024-08-14T13:00:00+00:00'
    },
    "Lwengo": {
        "imageUrl": "https://via.placeholder.com/600x400?text=Lwengo",
        "farmName": "Ferme de Lwengo",
        "latitude": "1.123",
        "longitude": "1.456",
        "timestamp": '2024-08-14T13:00:00+00:00'
    },
    "Mukono": {
        "imageUrl": "https://via.placeholder.com/600x400?text=Mukono",
        "farmName": "Ferme de Mukono",
        "latitude": "2.123",
        "longitude": "2.456",
        "timestamp": '2024-08-14T13:00:00+00:00'
    }
}


@bp.route('/WeatherInsert', methods=['GET'])
@cross_origin()  # Permet à toutes les origines de faire des requêtes à cette route
def uploadWeather():
    insert_weather_data_from_json(f'C:\\Users\\Backira Babazhelia\\Documents\\nomenaProjetBrian\\farm_management\\Weather_data.json')
    return jsonify({"status": "success"}), 200


@bp.route('/weather', methods=['GET'])
@cross_origin()
def get_weather():
    region_id = request.args.get('region_id')
    crop_id = request.args.get('crop_id')
    latitude = request.args.get('latitude', default=None)
    longitude = request.args.get('longitude', default=None)
    time = request.args.get('time', default=None)
    imageUrl = "http://example.com/images/logo.png"
    farmName = "Farm Name"
    print(f"Received parameters: region_id={region_id}, crop_id={crop_id}, latitude={latitude}, longitude={longitude}, time={time}")
    # Check if 'time' is not empty
    if time:
        try:
            # Convertir la chaîne ISO 8601 en un objet datetime
            timestamp = datetime.fromisoformat(time.replace('Z', '+00:00'))
            # Convertir l'objet datetime en une chaîne de caractères au format souhaité
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            return jsonify({"status": "error", "message": f"Invalid time format: {str(e)}"}), 400
    else:
        return jsonify({"status": "error", "message": "Time parameter is missing or empty"}), 400
    
    # Retrieve weather and solar data
    weather_result = get_weather_data(latitude, longitude, formatted_timestamp)
    solar_result = get_solar_data(latitude, longitude, formatted_timestamp)

    if not weather_result or not solar_result:
        return jsonify({"status": "error", "message": "Data not found"}), 404

    # Calculate ET₀ and ETc
    T = weather_result['air_temperature']
    RH = weather_result['humidity']
    Rs = solar_result['downward_short_wave_radiation_flux']
    u2 = weather_result['wind_speed']
    P = weather_result['pressure'] / 1000  # Convert Pa to kPa

    ET0 = calculate_penman_et0(T, RH, Rs, u2, P)

    # Example Kc value (you might want to get this from somewhere or adjust as needed)
    Kc = 1.2
    T_moy = T  # Assuming average temperature is used for ETc calculation
    ETc = calculate_blaney_criddle_etc(T_moy, Kc)

    # Prepare the response
    response = {
        "imageUrl": imageUrl,
        "farmName": farmName,
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": formatted_timestamp,
        "temperature": T,
        "humidity": RH,
        "solarRadiation": Rs,
        "windSpeed": u2,
        "pressure": P * 1000,  # Convert kPa back to Pa
        "ET0": ET0,
        "ETc": ETc
    }

    return jsonify({"status": "success", "data": response}), 200