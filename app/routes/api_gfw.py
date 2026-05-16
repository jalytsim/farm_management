from flask import Blueprint, json, jsonify, request, send_file
from app.models import Crop, District, Farm, FarmData, Forest, GFWLog
from app.routes.map import (
    gfw_async, gfw_async_from_geojson,
    gfw_async_carbon, gfw_async_carbon_from_geojson,
)
import os, hashlib, asyncio, tempfile, requests
from datetime import datetime
from werkzeug.utils import secure_filename
from urllib.parse import urlencode
from playwright.async_api import async_playwright
from app import db

from app.utils.pdf_reports import (
    build_eudr_farm_pdf,
    build_eudr_forest_pdf,
    build_carbon_farm_pdf,
    build_carbon_forest_pdf,
)

UPLOAD_FOLDER      = 'uploads/geojsons'
LOG_FILE           = 'logs/geojson_uploads.log'
ALLOWED_EXTENSIONS = {'geojson'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

bp = Blueprint('api_gfw', __name__, url_prefix='/api/gfw')

# ── Chemins logos ─────────────────────────────────────────────────────────────
# Logos dans app/static/ — copies logo.jpg et parrotlogo.png dans ce dossier
_STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
LOGO_PARROT = os.path.join(_STATIC_DIR, 'parrotlogo.png')
LOGO_AGRI   = os.path.join(_STATIC_DIR, 'logo.jpg')
print(f'[PDF Logos] parrot={LOGO_PARROT} exists={os.path.exists(LOGO_PARROT)}')
print(f'[PDF Logos] agri={LOGO_AGRI} exists={os.path.exists(LOGO_AGRI)}')


# ─── Helpers ─────────────────────────────────────────────────────────────────

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
            user_id=user_id, action_type=action_type,
            entity_type=entity_type, entity_id=str(entity_id) if entity_id else None,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:255],
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"[GFWLog] Erreur : {e}")

def _group_by_dataset(dataset_results):
    report = {}
    for item in dataset_results:
        ds = item['dataset']
        if ds not in report:
            report[ds] = []
        report[ds].append({
            "pixel":       item["pixel"],
            "data_fields": item["data_fields"],
            "coordinates": item["coordinates"],
        })
    return report

def _build_farm_info(farm):
    district = District.query.get(farm.district_id)
    info = {
        'farm_id':         farm.farm_id,
        'name':            farm.name,
        'subcounty':       farm.subcounty,
        'district_name':   district.name   if district else 'N/A',
        'district_region': district.region if district else 'N/A',
        'geolocation':     farm.geolocation,
        'phonenumber':     farm.phonenumber,
        'phonenumber2':    farm.phonenumber2,
        'date_created':    farm.date_created.strftime('%Y-%m-%d') if farm.date_created else 'N/A',
        'date_updated':    farm.date_updated.strftime('%Y-%m-%d') if farm.date_updated else 'N/A',
        'crops':           [],
    }
    for fd in FarmData.query.filter_by(farm_id=farm.farm_id).all():
        crop_name = Crop.query.get(fd.crop_id).name if fd.crop_id else 'N/A'
        info['crops'].append({'crop': crop_name, 'land_type': fd.land_type})
    return info


# ============================================
# FOREST DATA ENDPOINTS
# ============================================

@bp.route('/forests/<int:forest_id>/report', methods=['GET'])
async def forestReport(forest_id):
    forest = Forest.query.filter_by(id=forest_id).first()
    if not forest:
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
    return jsonify({"forest_info": forest_info,
                    "report": _group_by_dataset(data['dataset_results'])}), 200


# ============================================
# FARM DATA ENDPOINTS
# ============================================

@bp.route('/farm/<string:farm_id>/report', methods=['GET'])
async def farmerReport(farm_id):
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if not farm:
        return jsonify({"error": "Farm not found"}), 404
    data, status_code = await gfw_async(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code
    return jsonify({"farm_info": _build_farm_info(farm),
                    "report": _group_by_dataset(data['dataset_results'])}), 200


# ============================================
# CARBON DATA ENDPOINTS
# ============================================

@bp.route('/farm/<string:farm_id>/CarbonReport', methods=['GET'])
async def CarbonReport(farm_id):
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if not farm:
        return jsonify({"error": "Farm not found"}), 404
    data, status_code = await gfw_async_carbon(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code
    return jsonify({"farm_info": _build_farm_info(farm),
                    "report": data['dataset_results']}), 200


@bp.route('/forest/<string:forest_id>/CarbonReport', methods=['GET'])
async def CarbonReportforest(forest_id):
    forest = Forest.query.filter_by(id=forest_id).first()
    if not forest:
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
    return jsonify({"forest_info": forest_info,
                    "report": data['dataset_results']}), 200


# ============================================
# PDF ENDPOINTS — ReportLab (100 % backend)
# ============================================

def _send_pdf(pdf_bytes: bytes, filename: str):
    """Helper : écrit les bytes dans un fichier temp et retourne send_file."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp.write(pdf_bytes)
    tmp.close()
    return send_file(tmp.name, mimetype='application/pdf',
                     as_attachment=True, download_name=filename)


@bp.route('/farm/<string:farm_id>/eudr-pdf', methods=['POST'])
async def farm_eudr_pdf(farm_id):  # <-- Changé en 'async def' pour pouvoir utiliser 'await'
    """
    Rapport EUDR ferme — 100 % backend ReportLab avec injection de la carte du front.
    POST /api/gfw/farm/<farm_id>/eudr-pdf
    """
    # 1. Extraction de la string Base64 de la carte forestière envoyée par le frontend
    req_data = request.json or {}
    forest_map_base64 = req_data.get('forest_map_image')

    # 2. Récupération de la ferme en base de données
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if not farm:
        return jsonify({"error": "Farm not found"}), 404

    # 3. Récupération asynchrone des données GFW
    data, status_code = await gfw_async(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code

    # 4. Génération sécurisée du PDF avec ReportLab
    try:
        pdf_bytes = build_eudr_farm_pdf(
            farm_id           = str(farm_id),
            farm_info         = _build_farm_info(farm),
            gfw_data          = _group_by_dataset(data['dataset_results']),
            logo_parrot       = LOGO_PARROT,
            logo_agri         = LOGO_AGRI,
            forest_map_base64 = forest_map_base64  # <-- Paramètre injecté correctement ici
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Génération PDF échouée: {str(e)}"}), 500

    # 5. Envoi du fichier PDF généré
    return _send_pdf(pdf_bytes, f'EUDR_Report_{farm_id}.pdf')


@bp.route('/forests/<int:forest_id>/eudr-pdf', methods=['GET'])
async def eudr_forest_pdf(forest_id):
    """
    Rapport EUDR forêt — 100 % backend ReportLab.
    GET /api/gfw/forests/<forest_id>/eudr-pdf
    """
    forest = Forest.query.filter_by(id=forest_id).first()
    if not forest:
        return jsonify({"error": "Forest not found"}), 404

    forest_info = {
        'name':         forest.name,
        'tree_type':    forest.tree_type,
        'date_created': forest.date_created.strftime('%Y-%m-%d'),
        'date_updated': forest.date_updated.strftime('%Y-%m-%d'),
    }

    data, status_code = await gfw_async(owner_type='forest', owner_id=str(forest_id))
    if status_code != 200:
        return jsonify(data), status_code

    try:
        pdf_bytes = build_eudr_forest_pdf(
            forest_id   = forest_id,
            forest_info = forest_info,
            gfw_data    = _group_by_dataset(data['dataset_results']),
            logo_parrot = LOGO_PARROT,
            logo_agri   = LOGO_AGRI,
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    return _send_pdf(pdf_bytes, f'EUDR_Report_Forest_{forest_id}.pdf')


@bp.route('/farm/<string:farm_id>/carbon-pdf', methods=['GET'])
async def carbon_farm_pdf(farm_id):
    """
    Rapport Carbon ferme — 100 % backend ReportLab.
    GET /api/gfw/farm/<farm_id>/carbon-pdf
    """
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if not farm:
        return jsonify({"error": "Farm not found"}), 404

    data, status_code = await gfw_async_carbon(owner_type='farmer', owner_id=farm_id)
    if status_code != 200:
        return jsonify(data), status_code

    try:
        pdf_bytes = build_carbon_farm_pdf(
            farm_id     = farm_id,
            farm_info   = _build_farm_info(farm),
            report      = data['dataset_results'],
            logo_parrot = LOGO_PARROT,
            logo_agri   = LOGO_AGRI,
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    return _send_pdf(pdf_bytes, f'Carbon_Farm_Report_{farm_id}.pdf')


@bp.route('/forest/<int:forest_id>/carbon-pdf', methods=['GET'])
async def carbon_forest_pdf(forest_id):
    """
    Rapport Carbon forêt — 100 % backend ReportLab.
    GET /api/gfw/forest/<forest_id>/carbon-pdf
    """
    forest = Forest.query.filter_by(id=forest_id).first()
    if not forest:
        return jsonify({"error": "Forest not found"}), 404

    forest_info = {
        'name':         forest.name,
        'tree_type':    forest.tree_type,
        'date_created': forest.date_created.strftime('%Y-%m-%d'),
        'date_updated': forest.date_updated.strftime('%Y-%m-%d'),
    }

    data, status_code = await gfw_async_carbon(owner_type='forest', owner_id=forest_id)
    if status_code != 200:
        return jsonify(data), status_code

    try:
        pdf_bytes = build_carbon_forest_pdf(
            forest_id   = forest_id,
            forest_info = forest_info,
            report      = data['dataset_results'],
            logo_parrot = LOGO_PARROT,
            logo_agri   = LOGO_AGRI,
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    return _send_pdf(pdf_bytes, f'Carbon_Forest_Report_{forest_id}.pdf')


# ============================================
# GEOJSON FILE UPLOAD ENDPOINTS
# ============================================

@bp.route('/Geojson/ReportFromFile', methods=['POST'])
async def report_from_file():
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
        with open(saved_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        data, status_code = await gfw_async_from_geojson(geojson_data)
        if status_code != 200:
            return jsonify(data), status_code
        return jsonify({"message": "Duplicate file, using cached content",
                        "report": _group_by_dataset(data['dataset_results']),
                        "hash": filehash}), 200

    file.save(saved_path)
    log_upload(ip, user_agent, filename, filehash, guest_id)
    geojson_data = json.load(open(saved_path))
    data, status_code = await gfw_async_from_geojson(geojson_data)
    if status_code != 200:
        return jsonify(data), status_code
    return jsonify({"message": "file OK",
                    "report": _group_by_dataset(data['dataset_results'])}), 200


@bp.route('/Geojson/CarbonReportFromFile', methods=['POST'])
async def carbon_report_from_file():
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
        with open(saved_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        data, status_code = await gfw_async_carbon_from_geojson(geojson_data)
        if status_code != 200:
            return jsonify(data), status_code
        return jsonify({"message": "Duplicate file, using cached content",
                        "report": _group_by_dataset(data['dataset_results']),
                        "hash": filehash}), 200

    file.save(saved_path)
    log_upload(ip, user_agent, filename, filehash, guest_id)
    geojson_data = json.load(open(saved_path))
    data, status_code = await gfw_async_carbon_from_geojson(geojson_data)
    if status_code != 200:
        return jsonify(data), status_code
    return jsonify({"message": "file OK",
                    "report": _group_by_dataset(data['dataset_results'])}), 200


# ============================================
# LEGACY  —  Playwright (generate-receipt, etc.)
# ============================================

async def _html_to_pdf_bytes(html_content: str) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        page = await browser.new_page(viewport={"width": 1200, "height": 900})
        await page.set_content(html_content, wait_until="networkidle")
        await page.evaluate("""
            async () => {
                const imgs = Array.from(document.images);
                await Promise.all(imgs.map(img =>
                    img.complete ? Promise.resolve()
                    : new Promise(r => { img.onload = r; img.onerror = r; })
                ));
                await new Promise(r => setTimeout(r, 800));
            }
        """)
        pdf_bytes = await page.pdf(
            format='A4', print_background=True,
            margin={"top":"15mm","bottom":"15mm","left":"12mm","right":"12mm"},
        )
        await browser.close()
        return pdf_bytes


@bp.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data         = request.json or {}
    html_content = data.get('html', '')
    filename     = data.get('filename', 'report.pdf')
    if not html_content:
        return jsonify({"error": "No HTML provided"}), 400
    try:
        loop      = asyncio.new_event_loop()
        pdf_bytes = loop.run_until_complete(_html_to_pdf_bytes(html_content))
        loop.close()
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp.write(pdf_bytes); tmp.close()
    return send_file(tmp.name, mimetype='application/pdf',
                     as_attachment=True, download_name=filename)


@bp.route('/generate-receipt', methods=['POST'])
def generate_receipt():
    data         = request.json or {}
    html_content = data.get('html', '')
    if not html_content:
        return jsonify({"error": "No HTML provided"}), 400
    try:
        loop      = asyncio.new_event_loop()
        pdf_bytes = loop.run_until_complete(_html_to_pdf_bytes(html_content))
        loop.close()
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp.write(pdf_bytes); tmp.close()
    return send_file(tmp.name, mimetype='application/pdf',
                     as_attachment=True, download_name='receipt.pdf')