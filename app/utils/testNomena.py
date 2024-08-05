import arrow
import requests
import json

# Get first hour of today
start = arrow.now().floor('day')

# Get last hour of today
end = arrow.now().ceil('day')

# List of all parameters
params_list = [
    'airTemperature', 'airTemperature80m', 'airTemperature100m', 'airTemperature1000hpa', 'airTemperature800hpa', 
    'airTemperature500hpa', 'airTemperature200hpa', 'pressure', 'cloudCover', 'currentDirection', 'currentSpeed', 
    'gust', 'humidity', 'iceCover', 'precipitation', 'snowDepth', 'seaLevel', 'swellDirection', 'swellHeight', 
    'swellPeriod', 'secondarySwellPeriod', 'secondarySwellDirection', 'secondarySwellHeight', 'visibility', 
    'waterTemperature', 'waveDirection', 'waveHeight', 'wavePeriod', 'windWaveDirection', 'windWaveHeight', 
    'windWavePeriod', 'windDirection', 'windDirection20m', 'windDirection30m', 'windDirection40m', 'windDirection50m', 
    'windDirection80m', 'windDirection100m', 'windDirection1000hpa', 'windDirection800hpa', 'windDirection500hpa', 
    'windDirection200hpa', 'windSpeed', 'windSpeed20m', 'windSpeed30m', 'windSpeed40m', 'windSpeed50m', 'windSpeed80m', 
    'windSpeed100m', 'windSpeed1000hpa', 'windSpeed800hpa', 'windSpeed500hpa', 'windSpeed200hpa'
]

response = requests.get(
    'https://api.stormglass.io/v2/weather/point',
    params={
        'lat': 0.292225,
        'lng': 32.576809,
        'params': ','.join(params_list),
        # 'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
        # 'end': end.to('UTC').timestamp()  # Convert to UTC timestamp
    },
    headers={
        'Authorization': 'a6b685ea-5014-11ef-8a8f-0242ac130004-a6b68676-5014-11ef-8a8f-0242ac130004'
    }
)

# Get JSON data from the response
json_data = response.json()

# Define the file path
file_path = 'Weather_data.json'

# Write JSON data to a file
with open(file_path, 'w') as file:
    json.dump(json_data, file, indent=4)  # Pretty-print with indentation
