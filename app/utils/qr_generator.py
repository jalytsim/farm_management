from flask import request, send_file, render_template
import segno
import hashlib
from io import BytesIO
from zipfile import ZipFile
import tempfile
from reportlab.pdfgen import canvas
import os
from app.utils.farm_utils import get_farmProperties  # Use SQLAlchemy for queries
from app.models import Crop, Farm, FarmerGroup, db

def generate_qr_codes(farm_id):
    data = get_farmProperties(farm_id)

    if not data:
        print("No data found for the farm.")
        return None

    zip_temp = tempfile.NamedTemporaryFile(delete=False)
    with ZipFile(zip_temp, 'w') as zip_file:
        pdf_file_added = {}
        for row in data:
            (farm_id, farmergroup_id, geolocation, district_id, crop_id, tilled_land_size, season, 
            quality, produce_weight, harvest_date, timestamp, channel_partner, destination_country, 
            customer_name, district_name, district_region) = row

            district_name = district_name
            # Get the farm name
            farm = Farm.query.get(farm_id)
            farmer_name = farm.name if farm else 'N/A'
            print(farm) 

            # Get the farmer group name
            farmergroup = FarmerGroup.query.get(farmergroup_id)
            farmerg_name = farmergroup.name if farmergroup else 'N/A'

            # Get the crop details
            crop = Crop.query.get(crop_id)
            crop_name = crop.name if crop else 'N/A'
            grade = crop.category_id if crop else 'N/A'
            weight = crop.weight if crop else 0

            # Calculate the batch number
            bags_per_yield = weight  # Assuming weight in kg per bag
            batch_number = int(produce_weight / bags_per_yield)
            pdf_file_name = f'QR_{farmer_name}_{crop_name}.pdf'
            pdf = canvas.Canvas(pdf_file_name)

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

                    # Generate the QR code
                qr = segno.make(formatted_data)


                # Save the QR code image to a temporary file
                qr_file = f'temp_qr_{i+1}.png'
                qr.save(qr_file, scale=5)

                # Draw the QR code onto the PDF
                pdf.drawInlineImage(qr_file, 150, 300, width=300, height=300)
                pdf.setTitle(f'QR_{farmer_name}_{crop_id}')
                pdf.showPage()
                if os.path.exists(qr_file):
                    os.remove(qr_file)

            # Save the PDF
            if pdf_file_name not in pdf_file_added:
                pdf_file_added[pdf_file_name] = True
                pdf.save()
                zip_file.write(pdf_file_name)
                if os.path.exists(pdf_file_name):
                    os.remove(pdf_file_name)
            else:
                print('already added')

    return zip_temp.name

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
