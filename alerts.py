# alerts.py
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask import Blueprint, flash, jsonify, render_template, redirect, request, url_for, send_file


# Flask app
app = Flask(__name__)
bp = Blueprint('lesalerte', __name__)

# Seuils météo
TEMP_THRESHOLD_LOW = 15
TEMP_THRESHOLD_HIGH = 30
HEAVY_RAIN_THRESHOLD = 10
STRONG_WIND_THRESHOLD = 20
DRYNESS_HUMIDITY_THRESHOLD = 30

def fetch_weather_data(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
        f"&forecast_days=10"
    )
    response = requests.get(url)
    return response.json()

def detect_anomalies(data):
    alerts = []
    hours = data.get('hourly', {})

    time = hours.get("time", [])
    temperature = hours.get("temperature_2m", [])
    humidity = hours.get("relative_humidity_2m", [])
    precipitation = hours.get("precipitation", [])
    wind_speed = hours.get("wind_speed_10m", [])

    for i in range(len(time)):
        try:
            current_time = datetime.strptime(time[i], "%Y-%m-%dT%H:%M")
        except ValueError:
            continue

        alert_types = []

        if precipitation[i] > HEAVY_RAIN_THRESHOLD:
            alert_types.append("Heavy Rain")
        if temperature[i] > TEMP_THRESHOLD_HIGH:
            alert_types.append("Extreme Heat")
        if temperature[i] < TEMP_THRESHOLD_LOW:
            alert_types.append("Extreme Cold")
        if wind_speed[i] > STRONG_WIND_THRESHOLD:
            alert_types.append("Strong Wind")
        if humidity[i] < DRYNESS_HUMIDITY_THRESHOLD:
            alert_types.append("Dryness Alert")

        if alert_types:
            alerts.append({
                "time": current_time.strftime("%Y-%m-%d %H:%M"),
                "alerts": alert_types,
                "temperature": temperature[i],
                "humidity": humidity[i],
                "precipitation": precipitation[i],
                "wind_speed": wind_speed[i]
            })

    return alerts
