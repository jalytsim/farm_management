import json
from datetime import datetime
from app.utils.solar_utils import create_solar

def insert_solar_data_from_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    latitude = data['meta']['lat']
    longitude = data['meta']['lng']
    
    for hour in data['hours']:
        timestamp = datetime.fromisoformat(hour['time'].replace('Z', '+00:00'))
        uv_index = hour['uvIndex']['noaa']  # Vous pouvez utiliser 'sg' si nécessaire
        downward_short_wave_radiation_flux = hour['downwardShortWaveRadiationFlux']['noaa']  # Vous pouvez utiliser 'sg' si nécessaire
        
        create_solar(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
            uv_index=uv_index,
            downward_short_wave_radiation_flux=downward_short_wave_radiation_flux
        )

# Exécution du script
insert_solar_data_from_json('C:\\Users\\Backira Babazhelia\\Documents\\nomenaProjetBrian\\farm_management\\solar_data.json')





# import arrow
# import requests
# import json

# # Get first hour of today
# start = arrow.now().floor('day')

# # Get last hour of today
# end = arrow.now().ceil('day')

# response = requests.get(
#   'https://api.stormglass.io/v2/solar/point',
#   params={
#     'lat':0.292225,
#     'lng': 32.576809,
#     'params': ','.join(['uvIndex', 'downwardShortWaveRadiationFlux']),
#     # 'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
#     # 'end': end.to('UTC').timestamp()  # Convert to UTC timestamp
#   },
#   headers={
#     'Authorization': 'a6b685ea-5014-11ef-8a8f-0242ac130004-a6b68676-5014-11ef-8a8f-0242ac130004'
#   }
# )

# # Get JSON data from the response
# json_data = response.json()

# # Define the file path
# file_path = 'solar_data.json'

# # Write JSON data to a file
# with open(file_path, 'w') as file:
#     json.dump(json_data, file, indent=4)  # Pretty-print with indentation
