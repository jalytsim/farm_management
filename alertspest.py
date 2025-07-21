import requests
from datetime import datetime

GDD_BASE_TEMP = 10  # Température de base pour GDD

# Seuils GDD pour les ravageurs
PEST_GDD_THRESHOLDS = {
      "Fall Armyworm": 140,
    "Aphids": 100,
    "Stem Borers": 180,
    "Corn Earworm": 220,
    "Black Cutworm": 280,
    "Peach Twig Borer": 350,
    "Coffee Berry Borer": 120
}

def fetch_weather_data(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m"
        f"&forecast_days=10"
        f"&timezone=auto"
    )
    print(f"[DEBUG] Requesting Open-Meteo: {url}")
    response = requests.get(url)

    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch weather data: {response.status_code}")
        return {}

    data = response.json()

    temps = data.get("hourly", {}).get("temperature_2m", [])
    print(f"[INFO] Weather data received: {len(temps)} temperature points")
    return data

def detect_gdd_and_pest_alerts(data):
    alerts = []

    if not data:
        print("[ERROR] No data provided to pest alert detection")
        return alerts

    hours = data.get("hourly", {})
    times = hours.get("time", [])
    temperatures = hours.get("temperature_2m", [])

    if not times or not temperatures:
        print("[WARNING] No time or temperature data in forecast")
        return alerts

    gdd_cumulative = 0
    triggered_pests = set()

    for i in range(len(times)):
        try:
            current_time = datetime.strptime(times[i], "%Y-%m-%dT%H:%M")
        except ValueError:
            continue

        try:
            temp = float(temperatures[i])
        except (TypeError, ValueError):
            continue

        gdd = max(0, temp - GDD_BASE_TEMP)
        gdd_cumulative += gdd

        print(f"[DEBUG] {current_time} - Temp: {temp}°C → GDD: {gdd} → Cumulative: {gdd_cumulative}")

        current_alerts = []
        for pest, threshold in PEST_GDD_THRESHOLDS.items():
            if gdd_cumulative >= threshold and pest not in triggered_pests:
                current_alerts.append(pest)
                triggered_pests.add(pest)

        if current_alerts:
            print(f"[ALERT] Pests triggered at {current_time}: {current_alerts}")
            alerts.append({
                "time": current_time.strftime("%Y-%m-%d %H:%M"),
                "alerts": current_alerts,
                "gdd": round(gdd_cumulative, 1),
                "temperature": temp
            })

    if not alerts:
        print("[INFO] No pest alerts detected after evaluating GDD.")

    return alerts
