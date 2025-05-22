from alertspest import fetch_weather_data, detect_gdd_and_pest_alerts
import requests

ADMIN_PHONE = "256783130358"

PEST_ALERT_DESCRIPTION = {
    "Fall Armyworm": "Risk of Fall Armyworm. Monitor your crops for leaf damage.",
    "Aphids": "Aphid activity possible. Check for sticky residue and treat accordingly.",
    "Stem Borers": "Stem Borer risk. Inspect stems for holes or damage.",
}

def run_gdd_pest_check(app):
    from app.models import db, Farm
    with app.app_context():
        farms = Farm.query.all()

        for farm in farms:
            try:
                lat, lon = map(float, farm.geolocation.split(','))
            except (ValueError, AttributeError):
                print(f"[ERROR] Invalid geolocation for farm '{farm.name}'")
                continue

            print(f"[INFO] Checking GDD/Pest alerts for '{farm.name}'")

            try:
                weather_data = fetch_weather_data(lat, lon)
                pest_alerts = detect_gdd_and_pest_alerts(weather_data)

                if pest_alerts:
                    print(f"[ALERT] Pest risk detected for '{farm.name}'")
                    messages = [f"PEST ALERT for your farm: {farm.name}"]

                    for alert in pest_alerts:
                        pest_names = ", ".join(alert["alerts"])
                        message = f"\nTime: {alert['time']}\nRisk: {pest_names}"
                        message += f"\nTemp: {alert['temperature']}°C"
                        message += f"\nGDD Cumulative: {alert['gdd']}"

                        for pest in alert["alerts"]:
                            if pest in PEST_ALERT_DESCRIPTION:
                                message += f"\nAdvice: {PEST_ALERT_DESCRIPTION[pest]}"

                        messages.append(message)
                        print(message)

                    final_msg = "\n".join(messages).strip()

                    recipients = []
                    if farm.phonenumber:
                        recipients.append(farm.phonenumber)
                    if farm.phonenumber2:
                        recipients.append(farm.phonenumber2)
                    recipients.append(ADMIN_PHONE)

                    for phone in recipients:
                        try:
                            response = requests.post("http://localhost:5000/api/notifications/sms", json={
                                "phone": phone,
                                "message": final_msg
                            })
                            if response.status_code == 200:
                                print(f"[SENT] Pest alert SMS sent to {phone}")
                            else:
                                print(f"[FAILED] SMS not sent to {phone}: {response.text}")
                        except Exception as sms_error:
                            print(f"[ERROR] SMS sending error to {phone}: {sms_error}")
                else:
                    print(f"[OK] No pest alerts for '{farm.name}'")
            except Exception as e:
                print(f"[ERROR] Pest check failed for '{farm.name}': {e}")