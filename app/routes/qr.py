from flask import Blueprint, render_template, request, send_file
from flask_login import login_required

from app.utils.qr_generator import generate_qr_codes

bp = Blueprint('qr', __name__)

@bp.route('/qrcode')
@login_required
def qrcode():
    return render_template('codeQr.html')

@bp.route('/generate_qr', methods=['POST'])
@login_required
def generate_qr():
    # Get the Farm ID from the form
    farm_id = request.form['farm_id']
    # Generate QR codes
    qr_zip_file = generate_qr_codes(farm_id)
    if qr_zip_file:
        # Return the QR code image as binary data for rendering
        return send_file(qr_zip_file, as_attachment=True, download_name=f"QR_{farm_id}.zip")
    else:
        return render_template('codeQr.html', qr_image='No data found for the farm.')
