from flask import Blueprint, json, jsonify, request, send_file
from app.models import Crop, District, Farm, FarmData, Forest, GFWLog
from app.routes.map import gfw_async, gfw_async_from_geojson
from app.routes.map import gfw_async, gfw_async_carbon, gfw_async_carbon_from_geojson, gfw_async_from_geojson
import os
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename
import tempfile
import requests
from urllib.parse import urlencode
from weasyprint import HTML
from app import db

UPLOAD_FOLDER = 'uploads/geojsons'
LOG_FILE      = 'logs/geojson_uploads.log'
ALLOWED_EXTENSIONS = {'geojson'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

bp = Blueprint('api_gfw', __name__, url_prefix='/api/gfw')


# ─── Helpers ────────────────────────────────────────────────────────────────

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_hash(file_stream):
    hasher = hashlib.sha256()
    for chunk in iter(lambda: file_stream.read(4096), b""):
        hasher.update(chunk)
    file_stream.seek(0)
    return hasher.hexdigest()

def send_sms(phone, message):
    if not phone or not message:
        return
    query = urlencode({"msg": message, "msisdns": phone})
    url   = f"https://188.166.125.28/nkusu-iot/api/nkusu-iot/sms?{query}"
    try:
        res = requests.get(url, verify=False)
        print(f"✅ SMS envoyé à {phone} : {res.status_code}")
    except Exception as e:
        print(f"❌ Erreur SMS : {e}")

def is_valid_geojson(file_stream):
    try:
        data = json.load(file_stream)
        file_stream.seek(0)
        return "type" in data and data["type"] in {
            "FeatureCollection", "Feature", "GeometryCollection"
        }
    except Exception:
        file_stream.seek(0)
        return False

def log_upload(ip, user_agent, filename, filehash, guest_id):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(
            f"{datetime.utcnow().isoformat()} | GuestID: {guest_id} | "
            f"IP: {ip} | UA: {user_agent} | File: {filename} | Hash: {filehash}\n"
        )

def _log_gfw(action_type, entity_type, entity_id):
    """Journalise silencieusement une action GFW dans GFWLog."""
    try:
        user_id = None
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                user_id = identity['id'] if isinstance(identity, dict) else identity
        except Exception:
            pass

        log = GFWLog(
            user_id     = user_id,
            action_type = action_type,
            entity_type = entity_type,
            entity_id   = str(entity_id) if entity_id else None,
            ip_address  = request.remote_addr,
            user_agent  = request.headers.get('User-Agent', '')[:255],
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"[GFWLog] Erreur : {e}")


# ============================================
# FOREST ENDPOINTS
# ============================================

@bp.route('/forests/<int:forest_id>/report', methods=['GET'])
async def forestReport(forest_id):
    """Récupérer le rapport GFW d'une forêt (format groupé par dataset)."""
    forest = Forest.query.filter_by(id=forest_id).first()
    if forest is None:
        return jsonify({"error": "Forest not found"}), 404

    forest_info = {
        'farm_id':      forest.id,
        'name':         forest.name,
        'tree_type':    forest.tree_type,
        'date_created': forest.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_updated': forest.date_updated.strftime('%Y-%m-%d %H:%M:%S'),
    }

    data, status_code = await gfw_async(owner_type='forest', owner_id=str(forest_id))
    if status_code != 200:
        return jsonify(data), status_code

    report_by_dataset = {}
    for item in data['dataset_results']:
        dataset = item['dataset']
        if dataset not in report_by_dataset:
            report_by_dataset[dataset] = []
        report_by_dataset[dataset].append({
            "pixel":       item["pixel"],
            "data_fields": item["data_fields"],
            "coordinates": item["coordinates"],
        })

    return jsonify({"forest_info": forest_info, "report": report_by_dataset}), 200


# ============================================
# FARM ENDPOINTS
# ============================================

@bp.route('/farm/<string:farm_id>/report', methods=['GET'])
async def farmerReport(farm_id):
    """Récupérer le rapport GFW d'une ferme."""
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if farm is None:
        return jsonify({"error": "Farm not found"}), 404

    district = District.query.get(farm.district_id)

    farm_info = {
        'farm_id':         farm.farm_id,
        'name':            farm.name,
        'subcounty':       farm.subcounty,
        'district_name':   district.name   if district else 'N/A',
        'district_region': district.region if district else 'N/A',
        'geolocation':     farm.geolocation,
        'phonenumber':     farm.phonenumber,
        'phonenumber2':    farm.phonenumber2,
        'date_created':    farm.date_created.strftime('%Y-%m-%d %H:%M:%S') if farm.date_created else 'N/A',
        'date_updated':    farm.date_updated.strftime('%Y-%m-%d %H:%M:%S') if farm.date_updated else 'N/A',
        'crops':           [],
    }

    crops_data = FarmData.query.filter_by(farm_id=farm_id).all()
    for fd in crops_data:
        crop_name = Crop.query.get(fd.crop_id).name if fd.crop_id else 'N/A'
        farm_info['crops'].append({
            'crop':               crop_name,
            'land_type':          fd.land_type,
            'tilled_land_size':   fd.tilled_land_size,
            'planting_date':      fd.planting_date.strftime('%Y-%m-%d') if fd.planting_date else 'N/A',
            'season':             fd.season,
            'quality':            fd.quality,
            'quantity':           fd.quantity,
            'harvest_date':       fd.harvest_date.strftime('%Y-%m-%d') if fd.harvest_date else 'N/A',
            'expected_yield':     fd.expected_yield,
            'actual_yield':       fd.actual_yield,
            'timestamp':          fd.timestamp.strftime('%Y-%m-%d %H:%M:%S') if fd.timestamp else 'N/A',
            'channel_partner':    fd.channel_partner,
            'destination_country':fd.destination_country,
            'customer_name':      fd.customer_name,
        })

    data, status_code = await gfw_async(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code

    report_by_dataset = {}
    for item in data['dataset_results']:
        dataset = item['dataset']
        if dataset not in report_by_dataset:
            report_by_dataset[dataset] = []
        report_by_dataset[dataset].append({
            "pixel":       item["pixel"],
            "data_fields": item["data_fields"],
            "coordinates": item["coordinates"],
        })

    return jsonify({"farm_info": farm_info, "report": report_by_dataset}), 200


# ============================================
# CARBON REPORT ENDPOINTS  — ★ NASA/ORNL
# ============================================

@bp.route('/farm/<string:farm_id>/CarbonReport', methods=['GET'])
async def CarbonReport(farm_id):
    """Rapport carbone pour une ferme."""
    print(farm_id)
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if farm is None:
        return jsonify({"error": "Farm not found"}), 404

    farm_info = {
        'farm_id':      farm.farm_id,
        'name':         farm.name,
        'subcounty':    farm.subcounty,
        'district_name':   'N/A',
        'district_region': 'N/A',
        'geolocation':  farm.geolocation,
        'phonenumber':  farm.phonenumber,
        'phonenumber2': farm.phonenumber2,
        'date_created': farm.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_updated': farm.date_updated.strftime('%Y-%m-%d %H:%M:%S'),
        'crops': []
    }

    crops_data = FarmData.query.filter_by(farm_id=farm_id).all()
    for data in crops_data:
        crop_name = Crop.query.get(data.crop_id).name if data.crop_id else 'N/A'
        farm_info['crops'].append({
            'crop':             crop_name,
            'land_type':        data.land_type,
            'tilled_land_size': data.tilled_land_size,
            'planting_date':    data.planting_date.strftime('%Y-%m-%d') if data.planting_date else 'N/A',
            'season':           data.season,
            'quality':          data.quality,
            'quantity':         data.quantity,
            'harvest_date':     data.harvest_date.strftime('%Y-%m-%d') if data.harvest_date else 'N/A',
            'expected_yield':   data.expected_yield,
            'actual_yield':     data.actual_yield,
            'timestamp':        data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'channel_partner':  data.channel_partner,
            'destination_country': data.destination_country,
            'customer_name':    data.customer_name
        })

    data, status_code = await gfw_async_carbon(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code

    print(farm_info)
    return jsonify({
        "farm_info": farm_info,
        "report":    data['dataset_results']
    }), 200


@bp.route('/forest/<string:forest_id>/CarbonReport', methods=['GET'])
async def CarbonReportforest(forest_id):
    """Rapport carbone pour une forêt."""
    forest = Forest.query.filter_by(id=forest_id).first()
    if forest is None:
        return jsonify({"error": "Forest not found"}), 404

    forest_info = {
        'name':         forest.name,
        'tree_type':    forest.tree_type,
        'date_created': forest.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_updated': forest.date_updated.strftime('%Y-%m-%d %H:%M:%S'),
    }

    data, status_code = await gfw_async_carbon(owner_type='forest', owner_id=forest_id)
    if status_code != 200:
        return jsonify(data), status_code

    print(forest_info)
    return jsonify({
        "forest_info": forest_info,
        "report":      data['dataset_results']
    }), 200


# ============================================
# GEOJSON FILE UPLOAD ENDPOINTS
# ============================================

@bp.route('/Geojson/ReportFromFile', methods=['POST'])
async def report_from_file():
    """Générer un rapport GFW à partir d'un fichier GeoJSON."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only .geojson files are allowed'}), 400

    if not is_valid_geojson(file.stream):
        return jsonify({'error': 'Invalid GeoJSON content'}), 400

    filehash  = file_hash(file.stream)
    guest_id  = request.headers.get('X-Guest-ID', 'unknown_guest')
    ip        = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    filename  = secure_filename(file.filename)
    saved_path = os.path.join(UPLOAD_FOLDER, f"{filehash}.geojson")

    if os.path.exists(saved_path):
        try:
            with open(saved_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
        except Exception as e:
            return jsonify({'error': f'Error reading existing file: {str(e)}'}), 500

        data, status_code = await gfw_async_from_geojson(geojson_data)
        if status_code != 200:
            return jsonify(data), status_code

        report_by_dataset = _group_by_dataset(data['dataset_results'])
        return jsonify({
            "message": "Duplicate file, using cached content",
            "report":  report_by_dataset,
            "hash":    filehash,
        }), 200

    file.save(saved_path)
    log_upload(ip, user_agent, filename, filehash, guest_id)

    try:
        geojson_data = json.load(open(saved_path))
    except Exception as e:
        return jsonify({'error': f'Could not parse saved file: {str(e)}'}), 400

    data, status_code = await gfw_async_from_geojson(geojson_data)
    if status_code != 200:
        return jsonify(data), status_code

    return jsonify({
        "message": "file OK",
        "report":  _group_by_dataset(data['dataset_results']),
    }), 200


@bp.route('/Geojson/CarbonReportFromFile', methods=['POST'])
async def carbon_report_from_file():
    """Générer un rapport carbone à partir d'un fichier GeoJSON."""
    print("📂 Carbon report from file endpoint called")

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only .geojson files are allowed'}), 400

    if not is_valid_geojson(file.stream):
        return jsonify({'error': 'Invalid GeoJSON content'}), 400

    filehash   = file_hash(file.stream)
    guest_id   = request.headers.get('X-Guest-ID', 'unknown_guest')
    ip         = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    filename   = secure_filename(file.filename)
    saved_path = os.path.join(UPLOAD_FOLDER, f"{filehash}.geojson")

    if os.path.exists(saved_path):
        try:
            with open(saved_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
        except Exception as e:
            return jsonify({'error': f'Error reading existing file: {str(e)}'}), 500

        data, status_code = await gfw_async_carbon_from_geojson(geojson_data)
        if status_code != 200:
            return jsonify(data), status_code

        report_by_dataset = _group_by_dataset(data['dataset_results'])
        return jsonify({
            "message": "Duplicate file, using cached content",
            "report":  report_by_dataset,
            "hash":    filehash
        }), 200

    file.save(saved_path)
    log_upload(ip, user_agent, filename, filehash, guest_id)

    try:
        geojson_data = json.load(open(saved_path))
    except Exception as e:
        return jsonify({'error': f'Could not parse saved file: {str(e)}'}), 400

    data, status_code = await gfw_async_carbon_from_geojson(geojson_data)
    if status_code != 200:
        return jsonify(data), status_code

    return jsonify({
        "message": "file OK",
        "report":  _group_by_dataset(data['dataset_results']),
    }), 200


# ============================================
# PDF GENERATION ENDPOINTS
# ============================================

@bp.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """Générer un PDF à partir de HTML."""
    data         = request.json
    html_content = data.get('html')

    if not html_content:
        return {"error": "No HTML provided"}, 400

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        HTML(string=html_content).write_pdf(temp_pdf.name)

    return send_file(
        temp_pdf.name,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='report.pdf',
    )


@bp.route('/generate-receipt', methods=['POST'])
def generate_receipt():
    """Générer un reçu PDF."""
    data         = request.json
    html_content = data.get('html')

    if not html_content:
        return {"error": "No HTML provided"}, 400

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        HTML(string=html_content).write_pdf(temp_pdf.name)

    return send_file(
        temp_pdf.name,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='receipt.pdf',
    )


# ── Utilitaire interne ───────────────────────────────────────────────────────

def _group_by_dataset(dataset_results):
    """Regroupe les résultats GFW par dataset (format standard)."""
    report_by_dataset = {}
    for item in dataset_results:
        dataset = item['dataset']
        if dataset not in report_by_dataset:
            report_by_dataset[dataset] = []
        report_by_dataset[dataset].append({
            "pixel":       item["pixel"],
            "data_fields": item["data_fields"],
            "coordinates": item["coordinates"],
        })
    return report_by_dataset