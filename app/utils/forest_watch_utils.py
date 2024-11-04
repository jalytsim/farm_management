import json
import requests
import aiohttp
import asyncio

# Replace with your actual API key
api_key = '2a63c69c-ab85-49c3-ba2c-f7456277fc6e'


async def query_forest_watch_async(dataset, geometry, sql_query):
    payload = {
        "geometry": geometry,
        "sql": sql_query
    }
    url = f'https://data-api.globalforestwatch.org/dataset/{dataset}/latest/query'
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            headers={
                'x-api-key': api_key,
                'Content-Type': 'application/json'
            },
            json=payload
        ) as response:
            return await response.json()


def query_forest_watch(dataset, geometry, sql_query):
    # Create the payload dynamically
    payload = {
        "geometry": geometry,
        "sql": sql_query
    }
    
    # Define the URL dynamically based on the dataset
    url = f'https://data-api.globalforestwatch.org/dataset/{dataset}/latest/query'
    
    # Send the POST request
    response = requests.post(
        url,
        headers={
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        },
        json=payload
    )
    
    # Return the response
    return response.json()

def get_pixel_meaning(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        if "data" in data and len(data["data"]) > 0:
            pixel_meaning = data["data"][0].get("pixel_meaning")
            return pixel_meaning
    return None

def create_sql_query(pixel_meaning):
    if pixel_meaning:
        return f"SELECT COUNT({pixel_meaning}) FROM results"
    return "SELECT * FROM results"  # Fallback query if pixel_meaning is not found