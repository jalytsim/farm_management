import segno
import hashlib
from io import BytesIO
from zipfile import ZipFile
import tempfile
from reportlab.pdfgen import canvas
import os

def generate_qr_codes(farm_id):
    data = get_farmProperties(farm_id)
    if not data:
        print("No data found for the farm.")
        return None

    zip_temp = tempfile.NamedTemporaryFile(delete=False)
    with ZipFile(zip_temp, 'w') as zip_file:
        pdf_file_added = {}
        for row in data:
            farm_id, farmergroup_id, geolocation, district_id, crop_id, tilled_land_size, season, quality, produce_weight, harvest_date, timestamp, channel_partner, destination_country, customer_name, district_name, district_region = row
            print(geolocation)

            district_name = get_district_name(district_id)
            farmer_name = get_farm_name(farm_id)
            farmerg_name = get_farmergroup_name(farmergroup_id)
            crop_name, grade, weight = get_crop_data(crop_id)
            bags_per_yield = weight  # Assuming 10 kg per bag
            batch_number = int(produce_weight / bags_per_yield)
            pdf_file_name = f'QR_{farmer_name}_{crop_name}.pdf'
            pdf = canvas.Canvas(pdf_file_name)

            for i in range(batch_number):
                serial_data = f"{farmer_name}_{crop_name}_{i+1}"
                serial_number = hashlib.md5(serial_data.encode('utf-8')).hexdigest()
                formatted_data = f"Country: Uganda\nFarm ID: {farmer_name}\nGroup ID: {farmerg_name}\nGeolocation: {geolocation}\nLand poundaries: http://164.92.211.54:5000/boundaries/{district_name}/{farm_id}\nDistrict: {district_name}\nCrop: {crop_name}\nGrade: {grade}\nTilled Land Size: {tilled_land_size} ACRES\nSeason: {season}\nQuality: {quality}\nProduce Weight: {produce_weight} KG\nHarvest Date: {harvest_date}\nTimestamp: {timestamp}\nDistrict Region: {district_region}\nBatch Number: {i+1}\nChannel Partner: {channel_partner}\n Destination Country: {destination_country}\n Customer Name: {customer_name}\nSerial Number: {serial_number}\n"

                qr = segno.make(formatted_data)
                qr_file = f'temp_qr_{i+1}.png'
                qr.save(qr_file, scale=5)
                pdf.drawInlineImage(qr_file, 150, 300, width=300, height=300)
                pdf.setTitle(f'QR_{farmer_name}_{crop_name}')
                pdf.showPage()
                if os.path.exists(qr_file):
                    os.remove(qr_file)

            if pdf_file_name not in pdf_file_added:
                pdf_file_added[pdf_file_name] = True
                pdf.save()
                zip_file.write(pdf_file_name)
                if os.path.exists(pdf_file_name):
                    os.remove(pdf_file_name)

    return zip_temp.name
