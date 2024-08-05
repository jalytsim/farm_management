from app.models import Forest, Weather
from datetime import datetime
from flask_login import current_user
import numpy as np
from app import db
from flask import current_app as app
from datetime import datetime


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
def create_weather(data):
    new_weather = Weather(
        latitude=data['latitude'],
        longitude=data['longitude'],
        air_temperature=data.get('air_temperature'),
        air_temperature_80m=data.get('air_temperature_80m'),
        air_temperature_100m=data.get('air_temperature_100m'),
        air_temperature_1000hpa=data.get('air_temperature_1000hpa'),
        air_temperature_800hpa=data.get('air_temperature_800hpa'),
        air_temperature_500hpa=data.get('air_temperature_500hpa'),
        air_temperature_200hpa=data.get('air_temperature_200hpa'),
        pressure=data.get('pressure'),
        cloud_cover=data.get('cloud_cover'),
        current_direction=data.get('current_direction'),
        current_speed=data.get('current_speed'),
        gust=data.get('gust'),
        humidity=data.get('humidity'),
        ice_cover=data.get('ice_cover'),
        precipitation=data.get('precipitation'),
        snow_depth=data.get('snow_depth'),
        sea_level=data.get('sea_level'),
        swell_direction=data.get('swell_direction'),
        swell_height=data.get('swell_height'),
        swell_period=data.get('swell_period'),
        secondary_swell_period=data.get('secondary_swell_period'),
        secondary_swell_direction=data.get('secondary_swell_direction'),
        secondary_swell_height=data.get('secondary_swell_height'),
        visibility=data.get('visibility'),
        water_temperature=data.get('water_temperature'),
        wave_direction=data.get('wave_direction'),
        wave_height=data.get('wave_height'),
        wave_period=data.get('wave_period'),
        wind_wave_direction=data.get('wind_wave_direction'),
        wind_wave_height=data.get('wind_wave_height'),
        wind_wave_period=data.get('wind_wave_period'),
        wind_direction=data.get('wind_direction'),
        wind_direction_20m=data.get('wind_direction_20m'),
        wind_direction_30m=data.get('wind_direction_30m'),
        wind_direction_40m=data.get('wind_direction_40m'),
        wind_direction_50m=data.get('wind_direction_50m'),
        wind_direction_80m=data.get('wind_direction_80m'),
        wind_direction_100m=data.get('wind_direction_100m'),
        wind_direction_1000hpa=data.get('wind_direction_1000hpa'),
        wind_direction_800hpa=data.get('wind_direction_800hpa'),
        wind_direction_500hpa=data.get('wind_direction_500hpa'),
        wind_direction_200hpa=data.get('wind_direction_200hpa'),
        wind_speed=data.get('wind_speed'),
        wind_speed_20m=data.get('wind_speed_20m'),
        wind_speed_30m=data.get('wind_speed_30m'),
        wind_speed_40m=data.get('wind_speed_40m'),
        wind_speed_50m=data.get('wind_speed_50m'),
        wind_speed_80m=data.get('wind_speed_80m'),
        wind_speed_100m=data.get('wind_speed_100m'),
        wind_speed_1000hpa=data.get('wind_speed_1000hpa'),
        wind_speed_800hpa=data.get('wind_speed_800hpa'),
        wind_speed_500hpa=data.get('wind_speed_500hpa'),
        wind_speed_200hpa=data.get('wind_speed_200hpa'),
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow(),
    )
    db.session.add(new_weather)
    db.session.commit()

# Update an existing weather record
def update_weather(id, data):
    weather = db.session.query(Weather).get(id)
    if weather:
        weather.latitude = data.get('latitude', weather.latitude)
        weather.longitude = data.get('longitude', weather.longitude)
        weather.air_temperature = data.get('air_temperature', weather.air_temperature)
        weather.air_temperature_80m = data.get('air_temperature_80m', weather.air_temperature_80m)
        weather.air_temperature_100m = data.get('air_temperature_100m', weather.air_temperature_100m)
        weather.air_temperature_1000hpa = data.get('air_temperature_1000hpa', weather.air_temperature_1000hpa)
        weather.air_temperature_800hpa = data.get('air_temperature_800hpa', weather.air_temperature_800hpa)
        weather.air_temperature_500hpa = data.get('air_temperature_500hpa', weather.air_temperature_500hpa)
        weather.air_temperature_200hpa = data.get('air_temperature_200hpa', weather.air_temperature_200hpa)
        weather.pressure = data.get('pressure', weather.pressure)
        weather.cloud_cover = data.get('cloud_cover', weather.cloud_cover)
        weather.current_direction = data.get('current_direction', weather.current_direction)
        weather.current_speed = data.get('current_speed', weather.current_speed)
        weather.gust = data.get('gust', weather.gust)
        weather.humidity = data.get('humidity', weather.humidity)
        weather.ice_cover = data.get('ice_cover', weather.ice_cover)
        weather.precipitation = data.get('precipitation', weather.precipitation)
        weather.snow_depth = data.get('snow_depth', weather.snow_depth)
        weather.sea_level = data.get('sea_level', weather.sea_level)
        weather.swell_direction = data.get('swell_direction', weather.swell_direction)
        weather.swell_height = data.get('swell_height', weather.swell_height)
        weather.swell_period = data.get('swell_period', weather.swell_period)
        weather.secondary_swell_period = data.get('secondary_swell_period', weather.secondary_swell_period)
        weather.secondary_swell_direction = data.get('secondary_swell_direction', weather.secondary_swell_direction)
        weather.secondary_swell_height = data.get('secondary_swell_height', weather.secondary_swell_height)
        weather.visibility = data.get('visibility', weather.visibility)
        weather.water_temperature = data.get('water_temperature', weather.water_temperature)
        weather.wave_direction = data.get('wave_direction', weather.wave_direction)
        weather.wave_height = data.get('wave_height', weather.wave_height)
        weather.wave_period = data.get('wave_period', weather.wave_period)
        weather.wind_wave_direction = data.get('wind_wave_direction', weather.wind_wave_direction)
        weather.wind_wave_height = data.get('wind_wave_height', weather.wind_wave_height)
        weather.wind_wave_period = data.get('wind_wave_period', weather.wind_wave_period)
        weather.wind_direction = data.get('wind_direction', weather.wind_direction)
        weather.wind_direction_20m = data.get('wind_direction_20m', weather.wind_direction_20m)
        weather.wind_direction_30m = data.get('wind_direction_30m', weather.wind_direction_30m)
        weather.wind_direction_40m = data.get('wind_direction_40m', weather.wind_direction_40m)
        weather.wind_direction_50m = data.get('wind_direction_50m', weather.wind_direction_50m)
        weather.wind_direction_80m = data.get('wind_direction_80m', weather.wind_direction_80m)
        weather.wind_direction_100m = data.get('wind_direction_100m', weather.wind_direction_100m)
        weather.wind_direction_1000hpa = data.get('wind_direction_1000hpa', weather.wind_direction_1000hpa)
        weather.wind_direction_800hpa = data.get('wind_direction_800hpa', weather.wind_direction_800hpa)
        weather.wind_direction_500hpa = data.get('wind_direction_500hpa', weather.wind_direction_500hpa)
        weather.wind_direction_200hpa = data.get('wind_direction_200hpa', weather.wind_direction_200hpa)
        weather.wind_speed = data.get('wind_speed', weather.wind_speed)
        weather.wind_speed_20m = data.get('wind_speed_20m', weather.wind_speed_20m)
        weather.wind_speed_30m = data.get('wind_speed_30m', weather.wind_speed_30m)
        weather.wind_speed_40m = data.get('wind_speed_40m', weather.wind_speed_40m)
        weather.wind_speed_50m = data.get('wind_speed_50m', weather.wind_speed_50m)
        weather.wind_speed_80m = data.get('wind_speed_80m', weather.wind_speed_80m)
        weather.wind_speed_100m = data.get('wind_speed_100m', weather.wind_speed_100m)
        weather.wind_speed_1000hpa = data.get('wind_speed_1000hpa', weather.wind_speed_1000hpa)
        weather.wind_speed_800hpa = data.get('wind_speed_800hpa', weather.wind_speed_800hpa)
        weather.wind_speed_500hpa = data.get('wind_speed_500hpa', weather.wind_speed_500hpa)
        weather.wind_speed_200hpa = data.get('wind_speed_200hpa', weather.wind_speed_200hpa)
        weather.date_updated = datetime.utcnow()
        db.session.commit()

# Delete a weather record
def delete_weather(id):
    weather = db.session.query(Weather).get(id)
    if weather:
        db.session.delete(weather)
        db.session.commit()

# Get all weather records
def get_all_weathers():
    return db.session.query(Weather).all()
