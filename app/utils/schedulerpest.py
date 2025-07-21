from alertspest import fetch_weather_data, detect_gdd_and_pest_alerts
import requests

ADMIN_PHONE = "256783130358"

# Updated pest alert descriptions and messages
PEST_ALERT_DESCRIPTION = {
    "Fall Armyworm": (
        "Fall Armyworm development due to environmental conditions at your farm. "
        "Monitor your crops for leaf damage and/or pest eggs emergence and take preventive actions."
    ),
    "Aphids": (
        "Aphid activity possible due to environmental conditions at your farm. "
        "Inspect for sticky residue on leaves and consider appropriate treatment measures."
    ),
    "Stem Borers": (
        "Stem borer risk occurrence due to environmental conditions at your farm. "
        "Inspect stems for holes or damage and implement remedial actions as needed."
    ),
    "Corn Earworm": (
        "Corn earworm risk occurrence due to environmental conditions at your farm. "
        "Make spot inspections to check for tunnels in kernels, premature fruit ripening, damage to corn silk, and take remedial action."
    ),
    "Black Cutworm": (
        "Black cutworm risk occurrence due to environmental conditions at your farm. "
        "Check for feeding holes in leaves, cut stems, wilting plants, and take remedial action."
    ),
    "Peach Twig Borer": (
        "Peach twig borer risk occurrence due to environmental conditions at your farm. "
        "Make spot inspections for wilting of young plants and take remedial action."
    ),
    "Coffee Berry Borer": (
        "Coffee Berry Borer development due to environmental conditions at your farm. "
        "Check for fruit drop of young green cherries, dark brown spots, and inspect cherries on branches for small holes or damaged beans."
    ),
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
                    messages = []

                    for alert in pest_alerts:
                        for pest in alert["alerts"]:
                            desc = PEST_ALERT_DESCRIPTION.get(pest)
                            if desc:
                                message = (
                                    f"PEST Alert for your Farm: {farm.name}. {desc}"
                                )
                                messages.append(message)
                                print(f"[MESSAGE] {message}")

                    final_msg = "\n\n".join(messages)

                    # Send only to admin
                    recipients = [ADMIN_PHONE]

                    # Include farmer numbers if available
                    if farm.phonenumber:
                        recipients.insert(0, farm.phonenumber)
                    if farm.phonenumber2:
                        recipients.insert(1, farm.phonenumber2)

                    for phone in recipients:
                        try:
                            response = requests.post(
                                "http://localhost:5000/api/notifications/sms",
                                json={"phone": phone, "message": final_msg}
                            )
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
