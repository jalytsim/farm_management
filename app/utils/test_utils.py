import hashlib
import math
import segno
from reportlab.pdfgen import canvas
# def deg_to_m(lat1, lon1, lat2, lon2):
#     """Convert degrees to meters using a simple flat earth approximation."""
#     # Constants
#     R = 6378137  # Radius of Earth in meters

#     # Convert latitude and longitude from degrees to radians
#     lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
#     lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

#     # Differences in coordinates
#     delta_lat = lat2_rad - lat1_rad
#     delta_lon = lon2_rad - lon1_rad

#     # Haversine formula
#     a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

#     distance = R * c  # Output distance in meters
#     return distance

# def convert_to_cartesian(vertices):
#     """Convert geographic coordinates to Cartesian coordinates in meters."""
#     origin_lat = vertices[0][0]
#     origin_lon = vertices[0][1]

#     cartesian_vertices = []
#     for lat, lon in vertices:
#         x = deg_to_m(origin_lat, origin_lon, origin_lat, lon)
#         y = deg_to_m(origin_lat, origin_lon, lat, origin_lon)
#         cartesian_vertices.append((x, y))
    
#     return cartesian_vertices

# def calculate_area(vertices):
#     n = len(vertices)
#     area = 0.0

#     for i in range(n):
#         j = (i + 1) % n
#         area += vertices[i][0] * vertices[j][1]
#         area -= vertices[j][0] * vertices[i][1]

#     area = abs(area) / 2.0
#     return area

# # Exemple d'utilisation avec vos coordonnées
# vertices = [
# (32.588851,0.54519),
# (32.588883,0.545424),
# (32.58914,0.545861),
# (32.590049,0.545409),
# (32.590066,0.545245),
# (32.590386,0.545663),
# (32.590741,0.545458),
# (32.590601,0.545196),
# (32.591077,0.54479),
# (32.591221,0.544532),
# (32.591223,0.544332),
# (32.591454,0.54422),
# (32.59116,0.543855),
# (32.591492,0.543857),
# (32.591973,0.543428),
# (32.591661,0.542925),
# (32.591228,0.542902),
# (32.590995,0.542433),
# ]

# # Convertir les coordonnées en mètres
# cartesian_vertices = convert_to_cartesian(vertices)

# # Calculer l'aire
# polygon_area = calculate_area(cartesian_vertices)
# print(f"L'aire du polygone est : {polygon_area} mètres carrés")
# # Conversion en kilomètres carrés
# area_km2 = polygon_area / 1000000

# print(f"L'aire du polygone est : {area_km2} kilomètres carrés")

import tempfile
from zipfile import ZipFile


def create_qr_codes(data, pdf_filename):
    zip_temp = tempfile.NamedTemporaryFile(delete=False)
    with ZipFile(zip_temp, 'w') as zip_file:
        pdf_file_name = pdf_filename
        pdf = canvas.Canvas(pdf_file_name)

        serial_number = hashlib.md5(data.encode('utf-8')).hexdigest()
        formatted_data = f"{data}\nSerial Number: {serial_number}"

        # Generate the QR code
        qr = segno.make(formatted_data)
        
        # Save the QR code image to a temporary file
        qr_file = f'temp_qr.png'
        qr.save(qr_file, scale=5)

create_qr_codes('test', 'test_file')