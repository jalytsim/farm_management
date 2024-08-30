from flask import jsonify, request, send_file, render_template
import segno
import hashlib
from io import BytesIO
from zipfile import ZipFile
import tempfile
from reportlab.pdfgen import canvas
import os
from app.utils.farm_utils import get_farm_properties  # Use SQLAlchemy for queries
from app.models import Crop, Farm, FarmerGroup, db


def generate_qr_codes(farm_id):
    data = get_farm_properties(farm_id)

    if not data:
        print("No data found for the farm. qrgen.py")
        return None

    # Name the PDF file using the farm_id
    pdf_filename = f'{farm_id}.pdf'
    pdf_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_file_name = pdf_temp.name
    pdf_temp.close()  # Close the file to avoid permission issues

    # Create a canvas object and write to the PDF file
    pdf = canvas.Canvas(pdf_file_name)

    for row in data:
        (farm_id, farmergroup_id, geolocation, district_id, crop_id, tilled_land_size, season, 
        quality, produce_weight, harvest_date, timestamp, channel_partner, destination_country, 
        customer_name, district_name, district_region) = row

        farm = Farm.query.filter_by(farm_id=farm_id).first()
        farmer_name = farm.name if farm else 'N/A'

        farmergroup = FarmerGroup.query.get(farmergroup_id)
        farmerg_name = farmergroup.name if farmergroup else 'N/A'

        crop = Crop.query.get(crop_id)
        crop_name = crop.name if crop else 'N/A'
        grade = crop.category_id if crop else 'N/A'
        weight = crop.weight if crop else 0

        bags_per_yield = weight
        batch_number = int(produce_weight / bags_per_yield)

        for i in range(batch_number):
            serial_data = f"{farmer_name}_{crop_name}_{i+1}"
            serial_number = hashlib.md5(serial_data.encode('utf-8')).hexdigest()
            formatted_data = f"""Country: Uganda
Farm ID: {farmer_name}
Group ID: {farmerg_name}
Geolocation: {geolocation}
Land boundaries: http://164.92.211.54:5000/boundaries/{district_name}/{farm_id}
District: {district_name}
Crop: {crop_name}
Grade: {grade}
Tilled Land Size: {tilled_land_size} ACRES
Season: {season}
Quality: {quality}
Produce Weight: {produce_weight} KG
Harvest Date: {harvest_date}
Timestamp: {timestamp}
District Region: {district_region}
Batch Number: {i+1}
Channel Partner: {channel_partner}
Destination Country: {destination_country}
Customer Name: {customer_name}
Serial Number: {serial_number}"""

            qr = segno.make(formatted_data)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as qr_file:
                qr.save(qr_file.name, scale=5)
                pdf.drawInlineImage(qr_file.name, 150, 300, width=300, height=300)
                pdf.setTitle(f'QR_{farmer_name}_{crop_id}')
                pdf.showPage()

            os.remove(qr_file.name)  # Remove the QR code image after adding to PDF

    pdf.save()  # Save and close the PDF file

    # Add the named PDF file to a zip file
    zip_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    zip_temp.close()  # Close the file to avoid permission issues
    with ZipFile(zip_temp.name, 'w') as zip_file:
        zip_file.write(pdf_file_name, arcname=pdf_filename)  # Use arcname to rename within the zip file

    os.remove(pdf_file_name)  # Remove the temporary PDF file after adding to zip

    return zip_temp.name

def generate_qr_codes_png(farm_id):
    data = get_farm_properties(farm_id)

    if not data:
        print("No data found for the farm. qrgen.py")
        return None

    # Create a temporary file to save the QR code PNG
    qr_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    qr_file_name = qr_temp.name
    qr_temp.close()  # Close the file to avoid permission issues

    # Generate QR codes and save them to the PNG file
    for row in data:
        (farm_id, farmergroup_id, geolocation, district_id, crop_id, tilled_land_size, season, 
        quality, produce_weight, harvest_date, timestamp, channel_partner, destination_country, 
        customer_name, district_name, district_region) = row

        farm = Farm.query.filter_by(farm_id=farm_id).first()
        farmer_name = farm.name if farm else 'N/A'

        farmergroup = FarmerGroup.query.get(farmergroup_id)
        farmerg_name = farmergroup.name if farmergroup else 'N/A'

        crop = Crop.query.get(crop_id)
        crop_name = crop.name if crop else 'N/A'
        grade = crop.category_id if crop else 'N/A'
        weight = crop.weight if crop else 0

        bags_per_yield = weight
        batch_number = int(produce_weight / bags_per_yield)

        for i in range(batch_number):
            serial_data = f"{farmer_name}_{crop_name}_{i+1}"
            serial_number = hashlib.md5(serial_data.encode('utf-8')).hexdigest()
            formatted_data = f"""Country: Uganda
Farm ID: {farmer_name}
Group ID: {farmerg_name}
Geolocation: {geolocation}
Land boundaries: http://164.92.211.54:5000/boundaries/{district_name}/{farm_id}
District: {district_name}
Crop: {crop_name}
Grade: {grade}
Tilled Land Size: {tilled_land_size} ACRES
Season: {season}
Quality: {quality}
Produce Weight: {produce_weight} KG
Harvest Date: {harvest_date}
Timestamp: {timestamp}
District Region: {district_region}
Batch Number: {i+1}
Channel Partner: {channel_partner}
Destination Country: {destination_country}
Customer Name: {customer_name}
Serial Number: {serial_number}"""

            qr = segno.make(formatted_data)
            qr.save(qr_file_name, scale=5)  # Save the QR code to the PNG file

    return qr_file_name



def generate_qr_codes_dynamic(data, pdf_filename):
    zip_temp = tempfile.NamedTemporaryFile(delete=False)
    with ZipFile(zip_temp, 'w') as zip_file:
        pdf_file_name = f'{pdf_filename}'
        pdf = canvas.Canvas(pdf_file_name)

        serial_number = hashlib.md5(data.encode('utf-8')).hexdigest()
        formatted_data = f"{data}\nSerial Number: {serial_number}"

        # Generate the QR code
        qr = segno.make(formatted_data)
        
        # Save the QR code image to a temporary file
        qr_file = f'temp_qr.png'
        qr.save(qr_file, scale=5)

        # Draw the QR code onto the PDF
        pdf.drawInlineImage(qr_file, 150, 300, width=300, height=300)
        pdf.setTitle(pdf_filename)
        pdf.showPage()
        
        if os.path.exists(qr_file):
            os.remove(qr_file)

        # Save the PDF
        pdf.save()
        zip_file.write(pdf_file_name)
        if os.path.exists(pdf_file_name):
            os.remove(pdf_file_name)
    
    return zip_temp.name

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
        qr_file = f'{pdf_file_name}.png'
        qr.save(qr_file, scale=5)

import hashlib
from flask import jsonify

def generate_farm_data_json(farm_id):
    data = get_farm_properties(farm_id)

    if not data:
        return {"error": "No data found for the farm."}, 404

    farm_data_list = []

    for row in data:
        (farm_id, farmergroup_id, geolocation, district_id, crop_id, tilled_land_size, season, 
        quality, produce_weight, harvest_date, timestamp, channel_partner, destination_country, 
        customer_name, district_name, district_region) = row

        farm = Farm.query.filter_by(farm_id=farm_id).first()
        farmer_name = farm.name if farm else 'N/A'

        farmergroup = FarmerGroup.query.get(farmergroup_id)
        farmerg_name = farmergroup.name if farmergroup else 'N/A'

        crop = Crop.query.get(crop_id)
        crop_name = crop.name if crop else 'N/A'
        grade = crop.category_id if crop else 'N/A'
        weight = crop.weight if crop else 0

        bags_per_yield = weight
        batch_number = int(produce_weight / bags_per_yield)

        for i in range(batch_number):
            serial_data = f"{farmer_name}_{crop_name}_{i+1}"
            serial_number = hashlib.md5(serial_data.encode('utf-8')).hexdigest()

            farm_data = {
                "Country": "Uganda",
                "Farm ID": farmer_name,
                "Group ID": farmerg_name,
                "Geolocation": geolocation,
                "Land Boundaries URL": f"http://164.92.211.54:5000/boundaries/{district_name}/{farm_id}",
                "District": district_name,
                "Crop": crop_name,
                "Grade": grade,
                "Tilled Land Size": f"{tilled_land_size} ACRES",
                "Season": season,
                "Quality": quality,
                "Produce Weight": f"{produce_weight} KG",
                "Harvest Date": harvest_date,
                "Timestamp": timestamp,
                "District Region": district_region,
                "Batch Number": i+1,
                "Channel Partner": channel_partner,
                "Destination Country": destination_country,
                "Customer Name": customer_name,
                "Serial Number": serial_number
            }

            farm_data_list.append(farm_data)

    return farm_data_list, 200
