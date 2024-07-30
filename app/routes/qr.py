from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
import segno
from io import BytesIO
import tempfile
from reportlab.pdfgen import canvas
from app.utils.qr_generator import generate_qr_codes, generate_qr_codes_dynamic

bp = Blueprint('qr', __name__)

@bp.route('/qrcode')
@login_required
def qrcode():
    return render_template('qrcode/index.html')

@bp.route('/test')
@login_required
def test():
    pass

@bp.route('/generate_qr', methods=['POST', 'GET'])
@login_required
def generate_qr():
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        qr_zip_file = generate_qr_codes(farm_id)
        print (qr_zip_file)
        if qr_zip_file:
            return send_file(qr_zip_file, as_attachment=True, download_name=f"QR_{farm_id}.zip")
        else:
            return render_template('qrcode/codeQr.html', qr_image='No data found for the farm.')
    return render_template('qrcode/codeQr.html')

@bp.route('/generate_tree_qr', methods=['GET', 'POST'])
@login_required
def generate_tree_qr():
    if request.method == 'POST':
        forest_name = request.form['forest_name']
        forest_id = request.form['forest_id']
        tree_type = request.form['tree_type']
        date_cutting = request.form['date_cutting']
        gps_coordinates = request.form['gps_coordinates']
        height = request.form['height']
        diameter = request.form['diameter']
        export = request.form.get('export')  # Checkbox value
        export_name = request.form.get('export_name')  # Export name if provided

        data = (f"Forest Name: {forest_name}\nForest ID: {forest_id}\nTree Type: {tree_type}\n"
                f"Date of Cutting: {date_cutting}\nGPS Coordinates: {gps_coordinates}\n"
                f"Height: {height} m\nDiameter: {diameter} cm")

        if export and export_name:
            data += f"\nExport Name: {export_name}"

        zip_file_path = generate_qr_codes_dynamic(data, f"Tree_{tree_type}.pdf")
        
        return send_file(zip_file_path, as_attachment=True, download_name=f"Tree_{tree_type}.pdf")
    
    return render_template('qrcode/generate_tree_qr.html')


@bp.route('/generate_farmer_qr', methods=['GET', 'POST'])
@login_required
def generate_farmer_qr():
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        weight = request.form['weight']
        price_per_kg = request.form['price_per_kg']
        total_value = request.form['total_value']
        store_id = request.form['store_id']
        warehouse = request.form['warehouse']
        export = request.form.get('export')  # Checkbox value
        export_name = request.form.get('export_name')  # Export name if provided

        data = f"Farm ID: {farm_id}\nWeight: {weight} kgs\nPrice per Kg: {price_per_kg} Ugshs\nTotal Value: {total_value} Ugshs\nStore ID: {store_id}\nWarehouse: {warehouse}\n"

        if export and export_name:
            data += f"Export Name: {export_name}\n"

        zip_file_path = generate_qr_codes_dynamic(data, f"Farmer_{farm_id}.pdf")
    
        return send_file(zip_file_path, as_attachment=True, download_name=f"Farmer_{farm_id}.pdf")

    return render_template('qrcode/generate_farmer_qr.html')

@bp.route('/generate_qr_static', methods=['POST', 'GET'])
@login_required
def generate_qr_static():
    if request.method == 'POST':
        # Extract form data
        country = request.form['country']
        farm_id = request.form['farm_id']
        group_id = request.form['group_id']
        geolocation = request.form['geolocation']
        land_boundaries = request.form['land_boundaries']
        district = request.form['district']
        crop = request.form['crop']
        grade = request.form['grade']
        tilled_land_size = request.form['tilled_land_size']
        season = request.form['season']
        quality = request.form['quality']
        produce_weight = request.form['produce_weight']
        harvest_date = request.form['harvest_date']
        timestamp = request.form['timestamp']
        district_region = request.form['district_region']
        batch_number = request.form['batch_number']
        channel_partner = request.form['channel_partner']
        destination_country = request.form['destination_country']
        customer_name = request.form['customer_name']
        serial_number = request.form['serial_number']

        # Prepare data for QR code generation
        data = (
            f"Country: {country}\n"
            f"Farm ID: {farm_id}\n"
            f"Group ID: {group_id}\n"
            f"Geolocation: {geolocation}\n"
            f"Land Boundaries: {land_boundaries}\n"
            f"District: {district}\n"
            f"Crop: {crop}\n"
            f"Grade: {grade}\n"
            f"Tilled Land Size: {tilled_land_size}\n"
            f"Season: {season}\n"
            f"Quality: {quality}\n"
            f"Produce Weight: {produce_weight}\n"
            f"Harvest Date: {harvest_date}\n"
            f"Timestamp: {timestamp}\n"
            f"District Region: {district_region}\n"
            f"Batch Number: {batch_number}\n"
            f"Channel Partner: {channel_partner}\n"
            f"Destination Country: {destination_country}\n"
            f"Customer Name: {customer_name}\n"
            f"Serial Number: {serial_number}\n"
        )

        # Generate QR codes and save to PDF
        zip_file_path = generate_qr_codes_dynamic(data, f"Farmer_{farm_id}.pdf")

        # Send the file to the client
        return send_file(zip_file_path, as_attachment=True, download_name=f"Farmer_{farm_id}.pdf")

    return render_template('qrcode/codeQr.html')