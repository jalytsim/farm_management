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
