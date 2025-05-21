import requests
from datetime import datetime

GDD_BASE_TEMP = 10  # Température de base pour GDD

# Seuils GDD pour les différents ravageurs
PEST_GDD_THRESHOLDS = {
     "Fall Armyworm": 140,        # Spodoptera frugiperda
    "Corn Earworm": 220,         # Helicoverpa zea
    "Black Cutworm": 280,        # Agrotis ipsilon
    "Peach Twig Borer": 350      # Anarsia lineatella
}

def fetch_weather_data(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m"
        f"&forecast_days=10"
    )
    response = requests.get(url)
    return response.json()

def detect_gdd_and_pest_alerts(data):
    alerts = []
    hours = data.get("hourly", {})
    times = hours.get("time", [])
    temperatures = hours.get("temperature_2m", [])

    gdd_cumulative = 0
    triggered_pests = set()

    for i in range(len(times)):
        try:
            current_time = datetime.strptime(times[i], "%Y-%m-%dT%H:%M")
        except ValueError:
            continue

        temp = temperatures[i]
        gdd = max(0, temp - GDD_BASE_TEMP)
        gdd_cumulative += gdd

        current_alerts = []

        for pest, threshold in PEST_GDD_THRESHOLDS.items():
            if gdd_cumulative >= threshold and pest not in triggered_pests:
                current_alerts.append(pest)
                triggered_pests.add(pest)

        if current_alerts:
            alerts.append({
                "time": current_time.strftime("%Y-%m-%d %H:%M"),
                "alerts": current_alerts,
                "gdd": round(gdd_cumulative, 1),
                "temperature": temp
            })

    return alerts
