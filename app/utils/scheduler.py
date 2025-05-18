from alerts import fetch_weather_data, detect_anomalies
from app.models import db, Farm
import requests

def run_weather_check(app):
    with app.app_context():
        farms = Farm.query.all()

        for farm in farms:
            try:
                lat, lon = map(float, farm.geolocation.split(','))
            except (ValueError, AttributeError):
                print(f"[ERROR] Invalid geolocation for farm '{farm.name}': {farm.geolocation}")
                continue

            print(f"[INFO] Checking weather for '{farm.name}' at ({lat}, {lon})")

            try:
                weather_data = fetch_weather_data(lat, lon)
                alerts = detect_anomalies(weather_data)

                if alerts:
                    print(f"⚠️  Weather Alert for '{farm.name}':")
                    for alert in alerts:
                        print(
                            f"- {alert['time']} | {', '.join(alert['alerts'])} | "
                            f"🌡 {alert['temperature']}°C | 💧 {alert['humidity']}% | "
                            f"☔ {alert['precipitation']}mm | 🌬 {alert['wind_speed']}km/h"
                        )

                        # 🔔 SEND SMS
                        try:
                            sms_message = (
                                f"⚠️ Weather alert for {farm.name} at {alert['time']}:\n"
                                f"{', '.join(alert['alerts'])} - "
                                f"{alert['temperature']}°C, "
                                f"{alert['humidity']}% humidity, "
                                f"{alert['precipitation']}mm rain, "
                                f"{alert['wind_speed']}km/h wind."
                            )

                            response = requests.post("http://localhost:5000/api/notifications/sms", json={
                                "phone": "256783130358",  # ✅ FIXED PHONE NUMBER HERE
                                "message": sms_message
                            })

                            if response.status_code == 200:
                                print(f"[✅] SMS successfully sent to 256783130358")
                            else:
                                print(f"[❌] SMS sending failed: {response.text}")

                        except Exception as sms_error:
                            print(f"[❌] SMS sending error: {sms_error}")
                else:
                    print(f"[OK] No anomalies found for '{farm.name}'.")

            except Exception as e:
                print(f"[ERROR] Weather processing failed for '{farm.name}': {e}")
