from sqlalchemy import func
from app.models import Forest, Weather
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from flask_login import current_user
import numpy as np
from flask import current_app as app
import json
from app.models import Weather
from app import db


def calculate_penman_et0(T, RH, Rs, u2, P):
    # Saturation vapor pressure (es) in kPa
    es = 0.6108 * np.exp((17.27 * T) / (T + 237.3))
    
    # Actual vapor pressure (ea) in kPa
    ea = (RH / 100) * es
    
    # Slope of the saturation vapor pressure curve (Δ) in kPa/°C
    delta = (4098 * es) / ((T + 237.3)**2)
    
    # Psychrometric constant (γ) in kPa/°C
    gamma = (0.001013 * P) / (0.622 * 2.45)
    
    # Convert radiation from W/m² to MJ/m²/day
    Rn = Rs * 86.4 * 10**-3  # Net radiation (Rn) in MJ/m²/day
    
    # Soil heat flux density (G) in MJ/m²/day (assumed to be negligible)
    G = 0
    
    # Penman ET₀ calculation in mm/day
    ET0 = ((delta * (Rn - G)) + (gamma * (900 / (T + 273)) * u2 * (es - ea))) / (delta + gamma * (1 + 0.34 * u2))
    
    return ET0

# Exemple de données pour Wakiso, Kyenjojo, Butambala, Mukono
# T = 25.0    # Température en °C
# RH = 60.0   # Humidité relative en %
# Rs = 200.0  # Radiation solaire en W/m² (Downward Short-Wave Radiation Flux)
# u2 = 2.0    # Vitesse du vent en m/s
# P = 101300  # Pression atmosphérique en Pa

# et0 = calculate_penman_et0(T, RH, Rs, u2, P)
# print(f"ET₀ : {et0:.2f} mm/jour")



# Calcul pour ETc
def calculate_blaney_criddle_etc(T_moy, Kc):
    # Calcul du facteur de température (P)
    P = 0.46 * T_moy + 8.13
    
    # Calcul de l'ETc
    ETc = P * Kc
    
    return ETc

# Exemple de données
# T_moy = 25.0  # Température moyenne en °C
# Kc = 1.2      # Coefficient de culture

# et_c = calculate_blaney_criddle_etc(T_moy, Kc)
# print(f"ETc : {et_c:.2f} mm/jour")

# Create a new weather record

def create_weather(latitude, longitude, timestamp, **kwargs):
    new_weather = Weather(
        latitude=latitude,
        longitude=longitude,
        timestamp = timestamp,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow(),
        **kwargs
    )
    db.session.add(new_weather)
    db.session.commit()

def update_weather(id, **kwargs):
    weather = Weather.query.get(id)
    if weather:
        for key, value in kwargs.items():
            if hasattr(weather, key):
                setattr(weather, key, value)
        weather.date_updated = datetime.utcnow()
        db.session.commit()

def delete_weather(id):
    weather = Weather.query.get(id)
    if weather:
        db.session.delete(weather)
        db.session.commit()

def get_all_weather_data():
    return Weather.query.all()


def insert_weather_data_from_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    latitude = data.get('meta', {}).get('lat')
    longitude = data.get('meta', {}).get('lng')
    
    for hour in data.get('hours', []):
        print(f"Processing hour data: {hour}")  # For debugging

        timestamp = datetime.fromisoformat(hour['time'].replace('Z', '+00:00'))

        weather_data = {
            'air_temperature': hour.get('airTemperature', {}).get('noaa'),
            'air_temperature_80m': hour.get('airTemperature80m', {}).get('noaa'),
            'air_temperature_100m': hour.get('airTemperature100m', {}).get('noaa'),
            'air_temperature_1000hpa': hour.get('airTemperature1000hpa', {}).get('noaa'),
            'air_temperature_800hpa': hour.get('airTemperature800hpa', {}).get('noaa'),
            'air_temperature_500hpa': hour.get('airTemperature500hpa', {}).get('noaa'),
            'air_temperature_200hpa': hour.get('airTemperature200hpa', {}).get('noaa'),
            'pressure': hour.get('pressure', {}).get('noaa'),
            'cloud_cover': hour.get('cloudCover', {}).get('noaa'),
            'current_direction': hour.get('currentDirection', {}).get('noaa'),
            'current_speed': hour.get('currentSpeed', {}).get('noaa'),
            'gust': hour.get('gust', {}).get('noaa'),
            'humidity': hour.get('humidity', {}).get('noaa'),
            'ice_cover': hour.get('iceCover', {}).get('noaa'),
            'precipitation': hour.get('precipitation', {}).get('noaa'),
            'snow_depth': hour.get('snowDepth', {}).get('noaa'),
            'sea_level': hour.get('seaLevel', {}).get('noaa'),
            'swell_direction': hour.get('swellDirection', {}).get('noaa'),
            'swell_height': hour.get('swellHeight', {}).get('noaa'),
            'swell_period': hour.get('swellPeriod', {}).get('noaa'),
            'secondary_swell_direction': hour.get('secondarySwellDirection', {}).get('noaa'),
            'secondary_swell_height': hour.get('secondarySwellHeight', {}).get('noaa'),
            'secondary_swell_period': hour.get('secondarySwellPeriod', {}).get('noaa'),
            'visibility': hour.get('visibility', {}).get('noaa'),
            'water_temperature': hour.get('waterTemperature', {}).get('noaa'),
            'wave_direction': hour.get('waveDirection', {}).get('noaa'),
            'wave_height': hour.get('waveHeight', {}).get('noaa'),
            'wave_period': hour.get('wavePeriod', {}).get('noaa'),
            'wind_wave_direction': hour.get('windWaveDirection', {}).get('noaa'),
            'wind_wave_height': hour.get('windWaveHeight', {}).get('noaa'),
            'wind_wave_period': hour.get('windWavePeriod', {}).get('noaa'),
            'wind_direction': hour.get('windDirection', {}).get('noaa'),
            'wind_direction_20m': hour.get('windDirection20m', {}).get('noaa'),
            'wind_direction_30m': hour.get('windDirection30m', {}).get('noaa'),
            'wind_direction_40m': hour.get('windDirection40m', {}).get('noaa'),
            'wind_direction_50m': hour.get('windDirection50m', {}).get('noaa'),
            'wind_direction_80m': hour.get('windDirection80m', {}).get('noaa'),
            'wind_direction_100m': hour.get('windDirection100m', {}).get('noaa'),
            'wind_direction_1000hpa': hour.get('windDirection1000hpa', {}).get('noaa'),
            'wind_direction_800hpa': hour.get('windDirection800hpa', {}).get('noaa'),
            'wind_direction_500hpa': hour.get('windDirection500hpa', {}).get('noaa'),
            'wind_direction_200hpa': hour.get('windDirection200hpa', {}).get('noaa'),
            'wind_speed': hour.get('windSpeed', {}).get('noaa'),
            'wind_speed_20m': hour.get('windSpeed20m', {}).get('noaa'),
            'wind_speed_30m': hour.get('windSpeed30m', {}).get('noaa'),
            'wind_speed_40m': hour.get('windSpeed40m', {}).get('noaa'),
            'wind_speed_50m': hour.get('windSpeed50m', {}).get('noaa'),
            'wind_speed_80m': hour.get('windSpeed80m', {}).get('noaa'),
            'wind_speed_100m': hour.get('windSpeed100m', {}).get('noaa'),
            'wind_speed_1000hpa': hour.get('windSpeed1000hpa', {}).get('noaa'),
            'wind_speed_800hpa': hour.get('windSpeed800hpa', {}).get('noaa'),
            'wind_speed_500hpa': hour.get('windSpeed500hpa', {}).get('noaa'),
            'wind_speed_200hpa': hour.get('windSpeed200hpa', {}).get('noaa'),
        }
        
        print(f"Weather Data: {weather_data}")  # For debugging
        
        create_weather(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
            **weather_data
        )


def insert_weather_data(data):
    latitude = data.get('meta', {}).get('lat')
    longitude = data.get('meta', {}).get('lng')

    for hour in data.get('hours', []):
        timestamp = datetime.fromisoformat(hour['time'].replace('Z', '+00:00'))

        weather_data = {
            'air_temperature': hour.get('airTemperature', {}).get('noaa'),
            'air_temperature_80m': hour.get('airTemperature80m', {}).get('noaa'),
            'air_temperature_100m': hour.get('airTemperature100m', {}).get('noaa'),
            'air_temperature_1000hpa': hour.get('airTemperature1000hpa', {}).get('noaa'),
            'air_temperature_800hpa': hour.get('airTemperature800hpa', {}).get('noaa'),
            'air_temperature_500hpa': hour.get('airTemperature500hpa', {}).get('noaa'),
            'air_temperature_200hpa': hour.get('airTemperature200hpa', {}).get('noaa'),
            'pressure': hour.get('pressure', {}).get('noaa'),
            'cloud_cover': hour.get('cloudCover', {}).get('noaa'),
            'current_direction': hour.get('currentDirection', {}).get('noaa'),
            'current_speed': hour.get('currentSpeed', {}).get('noaa'),
            'gust': hour.get('gust', {}).get('noaa'),
            'humidity': hour.get('humidity', {}).get('noaa'),
            'ice_cover': hour.get('iceCover', {}).get('noaa'),
            'precipitation': hour.get('precipitation', {}).get('noaa'),
            'snow_depth': hour.get('snowDepth', {}).get('noaa'),
            'sea_level': hour.get('seaLevel', {}).get('noaa'),
            'swell_direction': hour.get('swellDirection', {}).get('noaa'),
            'swell_height': hour.get('swellHeight', {}).get('noaa'),
            'swell_period': hour.get('swellPeriod', {}).get('noaa'),
            'secondary_swell_direction': hour.get('secondarySwellDirection', {}).get('noaa'),
            'secondary_swell_height': hour.get('secondarySwellHeight', {}).get('noaa'),
            'secondary_swell_period': hour.get('secondarySwellPeriod', {}).get('noaa'),
            'visibility': hour.get('visibility', {}).get('noaa'),
            'water_temperature': hour.get('waterTemperature', {}).get('noaa'),
            'wave_direction': hour.get('waveDirection', {}).get('noaa'),
            'wave_height': hour.get('waveHeight', {}).get('noaa'),
            'wave_period': hour.get('wavePeriod', {}).get('noaa'),
            'wind_wave_direction': hour.get('windWaveDirection', {}).get('noaa'),
            'wind_wave_height': hour.get('windWaveHeight', {}).get('noaa'),
            'wind_wave_period': hour.get('windWavePeriod', {}).get('noaa'),
            'wind_direction': hour.get('windDirection', {}).get('noaa'),
            'wind_direction_20m': hour.get('windDirection20m', {}).get('noaa'),
            'wind_direction_30m': hour.get('windDirection30m', {}).get('noaa'),
            'wind_direction_40m': hour.get('windDirection40m', {}).get('noaa'),
            'wind_direction_50m': hour.get('windDirection50m', {}).get('noaa'),
            'wind_direction_80m': hour.get('windDirection80m', {}).get('noaa'),
            'wind_direction_100m': hour.get('windDirection100m', {}).get('noaa'),
            'wind_direction_1000hpa': hour.get('windDirection1000hpa', {}).get('noaa'),
            'wind_direction_800hpa': hour.get('windDirection800hpa', {}).get('noaa'),
            'wind_direction_500hpa': hour.get('windDirection500hpa', {}).get('noaa'),
            'wind_direction_200hpa': hour.get('windDirection200hpa', {}).get('noaa'),
            'wind_speed': hour.get('windSpeed', {}).get('noaa'),
            'wind_speed_20m': hour.get('windSpeed20m', {}).get('noaa'),
            'wind_speed_30m': hour.get('windSpeed30m', {}).get('noaa'),
            'wind_speed_40m': hour.get('windSpeed40m', {}).get('noaa'),
            'wind_speed_50m': hour.get('windSpeed50m', {}).get('noaa'),
            'wind_speed_80m': hour.get('windSpeed80m', {}).get('noaa'),
            'wind_speed_100m': hour.get('windSpeed100m', {}).get('noaa'),
            'wind_speed_1000hpa': hour.get('windSpeed1000hpa', {}).get('noaa'),
            'wind_speed_800hpa': hour.get('windSpeed800hpa', {}).get('noaa'),
            'wind_speed_500hpa': hour.get('windSpeed500hpa', {}).get('noaa'),
            'wind_speed_200hpa': hour.get('windSpeed200hpa', {}).get('noaa'),
        }
        
        create_weather(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
            **weather_data
        )

def get_weather_data(latitude, longitude, timestamp):
    session = sessionmaker(bind=db.engine)()

    result = session.query(
        Weather.air_temperature,
        Weather.pressure,
        Weather.wind_speed,
        Weather.humidity
    ).filter(
        Weather.latitude == latitude,
        Weather.longitude == longitude,
        Weather.timestamp == timestamp
    ).first()

    session.close()

    if result:
        return {
            'air_temperature': result.air_temperature,
            'pressure': result.pressure,
            'wind_speed': result.wind_speed,
            'humidity': result.humidity
        }
    else:
        return None    


def get_daily_average_temperature(datetime_str, latitude, longitude):
    session = sessionmaker(bind=db.engine)()

    # Convertir le datetime string en objet datetime
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    
    # Extraire la date pour les bornes de la journée
    start_of_day = datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day)
    end_of_day = start_of_day + timedelta(days=1)  # La fin du jour est le début du jour suivant

    # Requête pour calculer la température moyenne pour la journée spécifique
    result = session.query(
        func.avg(Weather.air_temperature).label('average_temperature')
    ).filter(
        Weather.latitude == latitude,
        Weather.longitude == longitude,
        Weather.timestamp >= start_of_day,
        Weather.timestamp < end_of_day
    ).scalar()  # Utiliser scalar() pour obtenir une seule valeur

    session.close()

    return result
