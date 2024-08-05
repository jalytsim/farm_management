from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from app.models import Weather

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



@bp.route('/upload-weather-data', methods=['POST'])
@cross_origin()
def upload_weather_data():
    try:
        # Load JSON data from the request
        data = request.get_json()

        # Extract latitude and longitude from the meta data
        latitude = data['meta']['lat']
        longitude = data['meta']['lng']

        # Loop through the hourly weather data
        for hour in data['hours']:
            # Extract data for each parameter
            weather = Weather(
                latitude=latitude,
                longitude=longitude,
                air_temperature=hour.get('airTemperature', {}).get('noaa'),
                air_temperature_80m=hour.get('airTemperature80m', {}).get('noaa'),
                air_temperature_100m=hour.get('airTemperature100m', {}).get('noaa'),
                air_temperature_1000hpa=hour.get('airTemperature1000hpa', {}).get('noaa'),
                air_temperature_800hpa=hour.get('airTemperature800hpa', {}).get('noaa'),
                air_temperature_500hpa=hour.get('airTemperature500hpa', {}).get('noaa'),
                air_temperature_200hpa=hour.get('airTemperature200hpa', {}).get('noaa'),
                pressure=hour.get('pressure', {}).get('noaa'),
                cloud_cover=hour.get('cloudCover', {}).get('noaa'),
                current_direction=hour.get('currentDirection', {}).get('noaa'),
                current_speed=hour.get('currentSpeed', {}).get('noaa'),
                gust=hour.get('gust', {}).get('noaa'),
                humidity=hour.get('humidity', {}).get('noaa'),
                ice_cover=hour.get('iceCover', {}).get('noaa'),
                precipitation=hour.get('precipitation', {}).get('noaa'),
                snow_depth=hour.get('snowDepth', {}).get('noaa'),
                sea_level=hour.get('seaLevel', {}).get('noaa'),
                swell_direction=hour.get('swellDirection', {}).get('noaa'),
                swell_height=hour.get('swellHeight', {}).get('noaa'),
                swell_period=hour.get('swellPeriod', {}).get('noaa'),
                secondary_swell_direction=hour.get('secondarySwellDirection', {}).get('noaa'),
                secondary_swell_height=hour.get('secondarySwellHeight', {}).get('noaa'),
                visibility=hour.get('visibility', {}).get('noaa'),
                water_temperature=hour.get('waterTemperature', {}).get('noaa'),
                wave_direction=hour.get('waveDirection', {}).get('noaa'),
                wave_height=hour.get('waveHeight', {}).get('noaa'),
                wave_period=hour.get('wavePeriod', {}).get('noaa'),
                wind_wave_direction=hour.get('windWaveDirection', {}).get('noaa'),
                wind_wave_height=hour.get('windWaveHeight', {}).get('noaa'),
                wind_wave_period=hour.get('windWavePeriod', {}).get('noaa'),
                wind_direction=hour.get('windDirection', {}).get('noaa'),
                wind_direction_20m=hour.get('windDirection20m', {}).get('noaa'),
                wind_direction_30m=hour.get('windDirection30m', {}).get('noaa'),
                wind_direction_40m=hour.get('windDirection40m', {}).get('noaa'),
                wind_direction_50m=hour.get('windDirection50m', {}).get('noaa'),
                wind_direction_80m=hour.get('windDirection80m', {}).get('noaa'),
                wind_direction_100m=hour.get('windDirection100m', {}).get('noaa'),
                wind_direction_1000hpa=hour.get('windDirection1000hpa', {}).get('noaa'),
                wind_direction_800hpa=hour.get('windDirection800hpa', {}).get('noaa'),
                wind_direction_500hpa=hour.get('windDirection500hpa', {}).get('noaa'),
                wind_direction_200hpa=hour.get('windDirection200hpa', {}).get('noaa'),
                wind_speed=hour.get('windSpeed', {}).get('noaa'),
                wind_speed_20m=hour.get('windSpeed20m', {}).get('noaa'),
                wind_speed_30m=hour.get('windSpeed30m', {}).get('noaa'),
                wind_speed_40m=hour.get('windSpeed40m', {}).get('noaa'),
                wind_speed_50m=hour.get('windSpeed50m', {}).get('noaa'),
                wind_speed_80m=hour.get('windSpeed80m', {}).get('noaa'),
                wind_speed_100m=hour.get('windSpeed100m', {}).get('noaa'),
                wind_speed_1000hpa=hour.get('windSpeed1000hpa', {}).get('noaa'),
                wind_speed_800hpa=hour.get('windSpeed800hpa', {}).get('noaa'),
                wind_speed_500hpa=hour.get('windSpeed500hpa', {}).get('noaa'),
                wind_speed_200hpa=hour.get('windSpeed200hpa', {}).get('noaa'),
                date_created=datetime.utcnow(),
                date_updated=datetime.utcnow()
            )

            db.session.add(weather)

        # Commit all the new records to the database
        db.session.commit()

        return jsonify({"message": "Weather data uploaded successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500