from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.utils.qr_generator import generate_farm_data_json, generate_qr_codes_dynamic

bp = Blueprint('api_qr', __name__, url_prefix='/api/qrcode')

@bp.route('/')
def qrcode():
    farm_id = 'WAK0002'
    qr_data = generate_farm_data_json(farm_id)
    # Here we would generate the QR code and return its data, but now we'll return JSON
    return jsonify({
        "farm_id": farm_id,
        "qr_data": qr_data,
        "message": "QR code data generated successfully"
    }), 200

@bp.route('/test')
def test():
    return jsonify({"message": "Test endpoint"}), 200

@bp.route('/generate_qr', methods=['POST'])
def generate_qr():
    if request.method == 'POST':
        # farm_id = request.form['farm_id']
        farm_id = 'WAK0002'
        qr_data = generate_farm_data_json(farm_id)
        # Here we would generate the QR code and return its data, but now we'll return JSON
        return jsonify({
            "farm_id": farm_id,
            "qr_data": qr_data,
            "message": "QR code data generated successfully"
        }), 200

@bp.route('/generate_tree_qr', methods=['POST'])
def generate_tree_qr():
    if request.method == 'POST':
        forest_name = request.form['forest_name']
        forest_id = request.form['forest_id']
        tree_type = request.form['tree_type']
        date_cutting = request.form['date_cutting']
        gps_coordinates = request.form['gps_coordinates']
        height = request.form['height']
        diameter = request.form['diameter']
        export = request.form.get('export')
        export_name = request.form.get('export_name')

        data = {
            "Forest Name": forest_name,
            "Forest ID": forest_id,
            "Tree Type": tree_type,
            "Date of Cutting": date_cutting,
            "GPS Coordinates": gps_coordinates,
            "Height": f"{height} m",
            "Diameter": f"{diameter} cm"
        }

        if export and export_name:
            data["Export Name"] = export_name

        return jsonify({
            "tree_data": data,
            "message": "Tree QR code data generated successfully"
        }), 200

@bp.route('/generate_farmer_qr', methods=['POST'])
def generate_farmer_qr():
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        weight = request.form['weight']
        price_per_kg = request.form['price_per_kg']
        total_value = request.form['total_value']
        store_id = request.form['store_id']
        warehouse = request.form['warehouse']
        export = request.form.get('export')
        export_name = request.form.get('export_name')

        data = {
            "Farm ID": farm_id,
            "Weight": f"{weight} kgs",
            "Price per Kg": f"{price_per_kg} Ugshs",
            "Total Value": f"{total_value} Ugshs",
            "Store ID": store_id,
            "Warehouse": warehouse
        }

        if export and export_name:
            data["Export Name"] = export_name

        return jsonify({
            "farmer_data": data,
            "message": "Farmer QR code data generated successfully"
        }), 200

@bp.route('/generate_qr_static', methods=['POST'])
def generate_qr_static():
    if request.method == 'POST':
        # Extract form data
        data = {
            "Country": request.form['country'],
            "Farm ID": request.form['farm_id'],
            "Group ID": request.form['group_id'],
            "Geolocation": request.form['geolocation'],
            "Land Boundaries": request.form['land_boundaries'],
            "District": request.form['district'],
            "Crop": request.form['crop'],
            "Grade": request.form['grade'],
            "Tilled Land Size": request.form['tilled_land_size'],
            "Season": request.form['season'],
            "Quality": request.form['quality'],
            "Produce Weight": request.form['produce_weight'],
            "Harvest Date": request.form['harvest_date'],
            "Timestamp": request.form['timestamp'],
            "District Region": request.form['district_region'],
            "Batch Number": request.form['batch_number'],
            "Channel Partner": request.form['channel_partner'],
            "Destination Country": request.form['destination_country'],
            "Customer Name": request.form['customer_name'],
            "Serial Number": request.form['serial_number'],
        }

        return jsonify({
            "qr_static_data": data,
            "message": "Static QR code data generated successfully"
        }), 200
