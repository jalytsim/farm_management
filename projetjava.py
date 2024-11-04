import json

# Function to get all pixel meanings from a JSON file
def get_pixel_meanings(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        # Collect pixel meanings in a list
        pixel_meanings = []
        if "data" in data:
            for entry in data["data"]:
                pixel_meaning = entry.get("pixel_meaning")
                if pixel_meaning:  # Check if pixel_meaning is not None
                    pixel_meanings.append(pixel_meaning)
        return pixel_meanings

# Example usage
json_file_path = r'D:\project\Brian\farm_management\gfw.json'  # Replace with the actual path to your JSON file
pixel_meanings = get_pixel_meanings(json_file_path)

if pixel_meanings:
    print("Pixel Meanings:")
    for meaning in pixel_meanings:
        print(f"- {meaning}")
else:
    print("No pixel meanings found.")
