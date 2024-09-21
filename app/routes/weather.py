from datetime import datetime
import json
from flask import Blueprint, app, jsonify, request
from flask_cors import cross_origin
from app.utils.solar_utils import get_solar_data
from app.utils.weather_utils import calculate_penman_etc, calculate_penman_et0, create_weather, get_daily_average_temperature, get_hourly_weather_data, get_weather_data, get_weekly_weather_data, insert_weather_data_from_json

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
@cross_origin()  # Allow all origins to make requests to this route
def uploadWeather():
    lat = request.args.get('lat', default='0.292225', type=str)
    lon = request.args.get('lon', default='32.576809', type=str)
    time = request.args.get('datestring', default='2024-08-06T10:00:43.649Z', type=str)

    # Time processing
    if time:
        try:
            # Convert ISO 8601 string to a datetime object
            timestamp = datetime.fromisoformat(time.replace('Z', '+00:00'))
            # Convert datetime object to a string in the desired format
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            return jsonify({"status": "error", "message": f"Invalid time format: {str(e)}"}), 400
    else:
        return jsonify({"status": "error", "message": "Time parameter is missing or empty"}), 400

    # Pass the formatted timestamp to your function and handle exceptions
    try:
        hourly_data, columns = get_hourly_weather_data(formatted_timestamp, lat, lon)
        
        # Create a dynamic dictionary based on the column names and corresponding data
        data = [
            {columns[i]: str(record[i]) if isinstance(record[i], datetime) else record[i]
             for i in range(len(record))}
            for record in hourly_data
        ]
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to fetch data: {str(e)}"}), 500

    return jsonify({"status": "success", "data": data}), 200

@bp.route('/WeatherWeekly', methods=['GET'])
@cross_origin()  # Allow all origins to make requests to this route
def getWeeklyWeather():
    lat = request.args.get('lat', default='0.536279', type=str)
    lon = request.args.get('lon', default='32.589248', type=str)
    time = request.args.get('datestring', default='2024-08-07T10:00:43.649Z', type=str)

    # Time processing
    if time:
        try:
            # Convert ISO 8601 string to a datetime object
            timestamp = datetime.fromisoformat(time.replace('Z', '+00:00'))
            # Convert datetime object to a string in the desired format
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            return jsonify({"status": "error", "message": f"Invalid time format: {str(e)}"}), 400
    else:
        return jsonify({"status": "error", "message": "Time parameter is missing or empty"}), 400

    # Fetch weekly data based on the timestamp
    try:
        weekly_data = get_weekly_weather_data(formatted_timestamp, lat, lon)
        
        # Process the weekly_data to include min, max, and average values
        data = [
            {
                "date": record["date"],  # Assuming "date" is the key for the date in the dictionary
                "min_temperature": record["min_temperature"],
                "max_temperature": record["max_temperature"],
                "average_temperature": record["average_temperature"],
                "min_pressure": record["min_pressure"],
                "max_pressure": record["max_pressure"],
                "average_pressure": record["average_pressure"],
                "min_wind_speed": record["min_wind_speed"],
                "max_wind_speed": record["max_wind_speed"],
                "average_wind_speed": record["average_wind_speed"],
                "min_humidity": record["min_humidity"],
                "max_humidity": record["max_humidity"],
                "average_humidity": record["average_humidity"],
                "total_precipitation": record["total_precipitation"]  # Total precipitation for the day
            }
            for record in weekly_data
        ]
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to fetch data: {str(e)}"}), 500

    return jsonify({"status": "success", "data": data}), 200



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
            # Convert the ISO 8601 string to a datetime object
            timestamp = datetime.fromisoformat(time.replace('Z', '+00:00'))
            # Convert the datetime object to a string in the desired format
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            return jsonify({"status": "error", "message": f"Invalid time format: {str(e)}"}), 400
    else:
        return jsonify({"status": "error", "message": "Time parameter is missing or empty"}), 400
    
    # Retrieve weather and solar data
    weather_result = get_weather_data(latitude, longitude, formatted_timestamp)
    print("weather data = ", weather_result)

    solar_result = get_solar_data(latitude, longitude, formatted_timestamp)
    print("solar data =", solar_result)

    if not weather_result or not solar_result:
        return jsonify({"status": "error", "message": "Data not found"}), 404

    # Calculate ET₀ and ETc
    RH = weather_result['humidity']
    min_humidity = weather_result['min_humidity']
    max_humidity = weather_result['max_humidity']

    precipitation = weather_result['precipitation']
    min_precipitation = weather_result['min_precipitation']
    max_precipitation = weather_result['max_precipitation']

    Rs = solar_result['downward_short_wave_radiation_flux']
    u2 = weather_result['wind_speed']
    min_wind_speed = weather_result['min_wind_speed']
    max_wind_speed = weather_result['max_wind_speed']

    P = weather_result['pressure'] / 1000  # Convert Pa to kPa
    min_pressure = weather_result['min_pressure'] / 1000
    max_pressure = weather_result['max_pressure'] / 1000

    # Example Kc value (you might want to get this from somewhere or adjust as needed)
    Kc = 1.2
    T_moy = get_daily_average_temperature(formatted_timestamp, latitude, longitude)  # Assuming average temperature is used for ETc calculation
    min_temperature = weather_result['min_temperature']
    max_temperature = weather_result['max_temperature']

    ETc = calculate_penman_etc(T_moy, RH, Rs, u2, P, 'maize')
    ET0 = calculate_penman_et0(T_moy, RH, Rs, u2, P)

    # Prepare the response
    response = {
        "imageUrl": imageUrl,
        "farmName": farmName,
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": formatted_timestamp,
        "average_temperature": T_moy,
        "min_temperature": min_temperature,
        "max_temperature": max_temperature,
        "humidity": RH,
        "min_humidity": min_humidity,
        "max_humidity": max_humidity,
        "solarRadiation": Rs,
        "windSpeed": u2,
        "min_wind_speed": min_wind_speed,
        "max_wind_speed": max_wind_speed,
        "pressure": P * 1000,  # Convert kPa back to Pa
        "min_pressure": min_pressure * 1000,  # Convert kPa to Pa
        "max_pressure": max_pressure * 1000,  # Convert kPa to Pa
        "ET0": ET0,
        "ETc": ETc,
        "precipitation": precipitation,
        "min_precipitation": min_precipitation,
        "max_precipitation": max_precipitation
    }

    return jsonify({"status": "success", "data": response}), 200



@bp.route('/dailyweather', methods=['GET'])
@cross_origin()
def get_daily_weather():
    latitude = request.args.get('latitude', default=None)
    longitude = request.args.get('longitude', default=None)
    time = request.args.get('time', default=None)
    print(f"Received parameters:latitude={latitude}, longitude={longitude}, time={time}")
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
    print("weather data = ",weather_result)

    solar_result = get_solar_data(latitude, longitude, formatted_timestamp)
    print("solar data =",solar_result)

    if not weather_result or not solar_result:
        return jsonify({"status": "error", "message": "Data not found"}), 404

    # Calculate ET₀ and ETc


    RH = weather_result['humidity']
    precipitation = weather_result['precipitation']
    Rs = solar_result['downward_short_wave_radiation_flux']
    u2 = weather_result['wind_speed']
    P = weather_result['pressure'] / 1000  # Convert Pa to kPa


    # Example Kc value (you might want to get this from somewhere or adjust as needed)
    Kc = 1.2
    T_moy = get_daily_average_temperature(formatted_timestamp, latitude, longitude)  # Assuming average temperature is used for ETc calculation
    ETc = calculate_blaney_criddle_etc(T_moy, Kc)
    ET0 = calculate_penman_et0(T_moy, RH, Rs, u2, P)

    # Prepare the response
    response = {
        # "imageUrl": imageUrl,
        # "farmName": farmName,
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": formatted_timestamp,
        "temperature": T_moy,
        "humidity": RH,
        "solarRadiation": Rs,
        "windSpeed": u2,
        "pressure": P * 1000,  # Convert kPa back to Pa
        "ET0": ET0,
        "ETc": ETc,
        "precipitation": precipitation, 
    }

    return jsonify({"status": "success", "data": response}), 200