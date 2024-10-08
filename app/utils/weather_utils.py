from sqlalchemy import and_, func
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
    print(type(T),"===================================================")
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



# Calcul pour ETc
def calculate_penman_etc(T, RH, Rs, u2, P, crop_name):
    """
    Calcul de l'ETc en utilisant l'ET₀ de Penman et le Kc de la culture.
    
    :param T: Température moyenne (°C)
    :param RH: Humidité relative (%)
    :param Rs: Radiation solaire (W/m²)
    :param u2: Vitesse du vent à 2 m (m/s)
    :param P: Pression atmosphérique (Pa)
    :param crop_name: Nom de la culture (par exemple 'Maïs')
    :return: ETc en mm/jour
    """
    # Calcul de l'ET₀ avec la méthode Penman
    ET0 = calculate_penman_et0(T, RH, Rs, u2, P)
    
    # Récupération du coefficient cultural (Kc) depuis la base de données
    # Kc = get_kc_for_crop(crop_name)
    Kc= 1.2
    # Calcul de l'ETc
    ETc = ET0 * Kc
    
    return ETc


def create_weather(latitude, longitude, timestamp, **kwargs):
    # Check if a weather entry with the same latitude, longitude, and timestamp already exists
    existing_weather = Weather.query.filter(
        and_(
            Weather.latitude == latitude,
            Weather.longitude == longitude,
            Weather.timestamp == timestamp
        )
    ).first()
    
    # If no duplicate is found, create a new weather entry
    if not existing_weather:
        new_weather = Weather(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
            date_created=datetime.utcnow(),
            date_updated=datetime.utcnow(),
            **kwargs
        )
        db.session.add(new_weather)
        db.session.commit()
        return new_weather
    else:
        return None 

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

def get_weather_data(latitude, longitude, timestamp = None):
    session = sessionmaker(bind=db.engine)()
    print(latitude, longitude,timestamp)
    result = session.query(
        Weather.air_temperature,
        Weather.pressure,
        Weather.wind_speed,
        Weather.humidity,
        Weather.precipitation
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
            'humidity': result.humidity,
            'precipitation': result.precipitation
        }
    else:
        return None    


def get_daily_temperature_stats(datetime_str, latitude, longitude):
    session = sessionmaker(bind=db.engine)()

    # Convert the datetime string into a datetime object
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    
    # Extract the start and end of the day
    start_of_day = datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day)
    end_of_day = start_of_day + timedelta(days=1)  # End of the day is the start of the next day

    # Query to calculate the min, max, and average temperatures for the specific day
    result = session.query(
        func.min(Weather.air_temperature).label('min_temperature'),
        func.max(Weather.air_temperature).label('max_temperature'),
        func.avg(Weather.air_temperature).label('average_temperature')
    ).filter(
        Weather.latitude == latitude,
        Weather.longitude == longitude,
        Weather.timestamp >= start_of_day,
        Weather.timestamp < end_of_day
    ).one()  # Use one() to get a tuple with the results

    session.close()

    # Return the min, max, and average temperatures
    return {
        'min_temperature': result.min_temperature,
        'max_temperature': result.max_temperature,
        'average_temperature': result.average_temperature
    }


def get_hourly_weather_data(datetime_str, latitude, longitude):
    # Create a session
    session = sessionmaker(bind=db.engine)()

    # Convert the datetime string to a datetime object
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

    # Extract the date to define the day bounds
    start_of_day = datetime(datetime_obj.year, datetime_obj.month, datetime_obj.day)
    end_of_day = start_of_day + timedelta(days=1)

    # Define the columns to query dynamically (can be expanded)
    columns = [
        Weather.timestamp,
        Weather.air_temperature,
        Weather.pressure,
        Weather.wind_speed,
        Weather.humidity,
        Weather.precipitation
    ]

    # Query to fetch hourly weather data (temperature, pressure, wind speed, etc.)
    hourly_weather_data = session.query(*columns).filter(
        and_(
            Weather.latitude == latitude,
            Weather.longitude == longitude,
            Weather.timestamp >= start_of_day,
            Weather.timestamp < end_of_day
        )
    ).order_by(Weather.timestamp).all()  # Order by timestamp to get data in sequence

    session.close()

    # Return both the data and the columns to dynamically construct the response
    return hourly_weather_data,[col.name for col in columns]


def get_weekly_weather_data(datetime_str, latitude, longitude):
    # Create a session
    session = sessionmaker(bind=db.engine)()

    # Convert the datetime string to a datetime object
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    print("======= ireto ny data ======",datetime_str,datetime_obj,  latitude, longitude)
    print("================================zay ihany =====================")
    # Define the start of the week (Monday) and end of the week (Sunday)
    start_of_week = datetime_obj #- timedelta(days=datetime_obj.weekday())  # Monday of the current week
    end_of_week = start_of_week + timedelta(days=10)  # Next Monday (exclusive)
    print('======= data=========' ,start_of_week, end_of_week,latitude,longitude ) #
    # Query to fetch weekly weather data (temperature, pressure, wind speed, etc.)
    data = session.query(
        func.date(Weather.timestamp).label('date'),
        func.min(Weather.air_temperature).label('min_temperature'),
        func.max(Weather.air_temperature).label('max_temperature'),
        func.avg(Weather.air_temperature).label('avg_temperature'),
        func.min(Weather.pressure).label('min_pressure'),
        func.max(Weather.pressure).label('max_pressure'),
        func.avg(Weather.pressure).label('avg_pressure'),
        func.min(Weather.wind_speed).label('min_wind_speed'),
        func.max(Weather.wind_speed).label('max_wind_speed'),
        func.avg(Weather.wind_speed).label('avg_wind_speed'),
        func.min(Weather.humidity).label('min_humidity'),
        func.max(Weather.humidity).label('max_humidity'),
        func.avg(Weather.humidity).label('avg_humidity'),
        func.sum(Weather.precipitation).label('total_precipitation')  # Sum for precipitation
    ).filter(
        and_(
            Weather.latitude == latitude,
            Weather.longitude == longitude,
            Weather.timestamp >= start_of_week,
            Weather.timestamp < end_of_week
        )
    ).group_by(func.date(Weather.timestamp)).order_by(func.date(Weather.timestamp)).all()

    session.close()

    # Convert the query result into a list of dictionaries
    weekly_data = [
        {
            "date": str(record.date),  # Date in YYYY-MM-DD format
            "min_temperature": record.min_temperature,
            "max_temperature": record.max_temperature,
            "average_temperature": record.avg_temperature,
            "min_pressure": record.min_pressure,
            "max_pressure": record.max_pressure,
            "average_pressure": record.avg_pressure,
            "min_wind_speed": record.min_wind_speed,
            "max_wind_speed": record.max_wind_speed,
            "average_wind_speed": record.avg_wind_speed,
            "min_humidity": record.min_humidity,
            "max_humidity": record.max_humidity,
            "average_humidity": record.avg_humidity,
            "total_precipitation": record.total_precipitation  # Total precipitation for the day
        }
        for record in data
    ]

    print("weather data", weekly_data)

    return weekly_data
