import json
import requests
import aiohttp

# Replace with your actual API key
api_key = '2a63c69c-ab85-49c3-ba2c-f7456277fc6e'


async def query_forest_watch_async(dataset, geometry, sql_query):
    payload = {
        "geometry": geometry,
        "sql": sql_query
    }

    if dataset == "gfw_soil_carbon":
        url = f'https://data-api.globalforestwatch.org/dataset/gfw_soil_carbon/v20230322/query'
    elif dataset == "jrc_global_forest_cover":
        url = f'https://data-api.globalforestwatch.org/dataset/jrc_global_forest_cover/v2020/query'
    else:
        url = f'https://data-api.globalforestwatch.org/dataset/{dataset}/latest/query'

    # Generate CURL command for debugging in the requested format
    curl_command = (
        f"curl --location --request POST '{url}' "
        f"--header 'x-api-key: {api_key}' "
        f"--header 'Content-Type: application/json' "
        f"--data-raw '{json.dumps(payload)}'"
    )

    # Log query details
    # print("---- QUERY DETAILS ----")
    # print(f"Dataset: {dataset}")
    # print(f"URL: {url}")
    # print(f"SQL Query: {sql_query}")
    # print(f"Payload: {json.dumps(payload, indent=4)}")
    # print(f"Generated CURL command:\n{curl_command}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers={
                    'x-api-key': api_key,
                    'Content-Type': 'application/json'
                },
                json=payload
            ) as response:
                print(f"HTTP Status Code: {response.status}")
                response_data = await response.json()
                if dataset == "gfw_soil_carbon":
                    print("hello",response_data)
                print(response_data)
                return response_data
    except Exception as e:
        # Log errors explicitly
        print(f"Error occurred for dataset '{dataset}': {str(e)}")
        return {"error": str(e)}


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