from flask import Blueprint, jsonify
from app.models import Farm
from alertspest import fetch_weather_data, detect_gdd_and_pest_alerts
from alerts import detect_anomalies

bp = Blueprint('alerts', __name__)

@bp.route('/api/alerts', methods=['GET'])
def get_alerts():
    farms = Farm.query.all()
    results = []

    for farm in farms:
        try:
            lat, lon = map(float, farm.geolocation.split(','))
            weather_data = fetch_weather_data(lat, lon)
            weather_alerts = detect_anomalies(weather_data)
            pest_alerts = detect_gdd_and_pest_alerts(weather_data)

            results.append({
                "farm": {
                    "id": farm.id,
                    "name": farm.name,
                    "geolocation": farm.geolocation,
                    "phonenumber": farm.phonenumber,
                },
                "weather_alerts": weather_alerts,
                "pest_alerts": pest_alerts
            })
        except Exception as e:
            print(f"[ERROR] Problem with farm {farm.name}: {e}")
    
    print("[DEBUG] Returning alerts:", results)
    return jsonify(results)
