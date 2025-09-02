from alerts import fetch_weather_data, detect_anomalies
import requests

ADMIN_PHONE = "256783130358"  # Admin receives all alerts

# Short and simple explanations for each type of weather alert
ALERT_DESCRIPTIONS = {
    "Strong Wind": "Strong wind. Tie or cover your crops and keep things safe.",
    "Extreme Heat": "Very hot. Water your crops and stay in the shade.",
    "Heavy Rain": "Heavy rain. Check for water paths and cover young crops.",
    "Cold Temperatures": "Cold weather. Cover crops to keep them warm.",
    "Storm": "Storm. Do not go out and protect your farm.",
}

def run_weather_check(app):
    from app.models import db, Farm 
    with app.app_context():
        farms = Farm.query.all()
        print("✅ Scheduler WeatherCheck.")
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
                    print(f"[ALERT] Weather warning for '{farm.name}'")

                    messages = [f"WEATHER ALERT for your farm: {farm.name}"]

                    for alert in alerts:
                        alert_names = ", ".join(alert["alerts"])
                        alert_message = f"\nTime: {alert['time']}"
                        alert_message += f"\nAlert: {alert_names}"

                        # Add basic explanations
                        for a in alert["alerts"]:
                            if a in ALERT_DESCRIPTIONS:
                                alert_message += f"\nAdvice: {ALERT_DESCRIPTIONS[a]}"

                        # Add weather values
                        alert_message += (
                            f"\nTemp: {alert['temperature']}°C"
                            f"\nHumidity: {alert['humidity']}%"
                            f"\nRain: {alert['precipitation']} mm"
                            f"\nWind: {alert['wind_speed']} km/h"
                        )

                        messages.append(alert_message)
                        print(alert_message)

                    final_message = "\n".join(messages).strip()

                    # Recipients: only admin
                    recipients = [ADMIN_PHONE]

                    # Commented out: no sending to farmers
                    if farm.phonenumber:
                        recipients.append(farm.phonenumber)
                    if farm.phonenumber2:
                        recipients.append(farm.phonenumber2)

                    for phone in recipients:
                        try:
                            response = requests.post("http://localhost:5000/api/notifications/sms", json={
                                "phone": phone,
                                "message": final_message
                            })

                            if response.status_code == 200:
                                print(f"[SENT] SMS sent to {phone}")
                            else:
                                print(f"[FAILED] Could not send SMS to {phone}: {response.text}")

                        except Exception as sms_error:
                            print(f"[ERROR] SMS sending error to {phone}: {sms_error}")
                else:
                    print(f"[OK] No weather alerts for '{farm.name}'")

            except Exception as e:
                print(f"[ERROR] Weather check failed for '{farm.name}': {e}")
