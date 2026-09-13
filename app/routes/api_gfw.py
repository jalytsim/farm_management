from flask import Blueprint, json, jsonify, request, send_file, Response
from app.models import Crop, District, Farm, FarmData, Forest, GFWLog, PaidFeatureAccess, User
from app.routes.map import (
    gfw_async, gfw_async_from_geojson,
    gfw_async_carbon, gfw_async_carbon_from_geojson,
)
import os, hashlib, asyncio, tempfile, requests, csv, io
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from urllib.parse import urlencode
from playwright.async_api import async_playwright
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
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

def _log_gfw(action_type, entity_type, entity_id, agent_id=None):
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
            agent_id=str(agent_id)[:100] if agent_id else None,
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


# ✅ NOUVEAU — adaptateur pour la génération PDF invité côté Carbon.
#
# build_carbon_farm_pdf() attend `report` comme une LISTE ORDONNÉE
# (report[0]=emissions, report[1]=removals, report[2]=net_flux,
#  report[3]=séquestration belowground, report[4]=séquestration aboveground),
# exactement l'ordre dans lequel DATASET_CONFIG['carbon'] déclare ses
# datasets/pixels dans map.py.
#
# Mais le rapport stocké côté invité (Geojson/CarbonReportFromFile) est au
# format GROUPÉ PAR DATASET (_group_by_dataset), le même format que celui
# affiché à l'écran par CarbonReportSection.jsx. Ce helper reconstruit la
# liste ordonnée à partir du dict groupé, sans dupliquer la logique de
# calcul GFW.
_CARBON_ORDER = [
    ('forest carbon gross emissions', 0),
    ('forest carbon gross removals', 0),
    ('forest carbon net flux', 0),
    ('full extent aboveground carbon potential sequestration', 0),  # belowground (1er pixel du dataset)
    ('full extent aboveground carbon potential sequestration', 1),  # aboveground (2e pixel du dataset)
]

def _carbon_grouped_to_list(gfw_data: dict) -> list:
    result = []
    for key, idx in _CARBON_ORDER:
        items = gfw_data.get(key, []) if isinstance(gfw_data, dict) else []
        result.append(items[idx] if idx < len(items) else {})
    return result


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

def _send_pdf(pdf_bytes: bytes, filename: str, as_attachment: bool = True, browser_safe: bool = False):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp.write(pdf_bytes)
    tmp.close()
    # ✅ FIX (IDM) : pour les endpoints invités affichés inline, on évite
    # 'application/pdf' dans le Content-Type réseau — IDM (et gestionnaires
    # de téléchargement similaires) l'interceptent automatiquement dès que
    # la taille dépasse leur seuil, quel que soit Content-Disposition.
    # Le frontend re-type le blob en 'application/pdf' lui-même après coup.
    mimetype = 'application/octet-stream' if browser_safe else 'application/pdf'
    return send_file(tmp.name, mimetype=mimetype,
                     as_attachment=as_attachment, download_name=filename)


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
# ✅ NOUVEAU — PDF ENDPOINTS INVITÉ — même moteur ReportLab que le client,
# sans dépendance à une Farm en base de données.
#
# Le frontend envoie directement le `report` déjà calculé et affiché à
# l'écran (même format que celui stocké dans useReports.jsx / reports.eudr /
# reports.carbon), plus des infos optionnelles (farm_info, carte forêt).
# ============================================

@bp.route('/guest/eudr-pdf', methods=['POST'])
def guest_eudr_pdf():
    """
    Rapport EUDR invité — 100 % backend ReportLab.
    POST /api/gfw/guest/eudr-pdf
    Body JSON attendu :
      {
        "report": {...},          # dict groupé par dataset (voir _group_by_dataset),
                                   # identique à ce que renvoie ReportFromFile
        "farm_info": {...},       # optionnel : name, geolocation, subcounty,
                                   # district_name, crops[], farm_id...
        "forest_map_image": "...",# optionnel : base64 de la carte StaticForestMap
        "guest_id": "..."         # optionnel : identifiant pour le nom du fichier
      }
    """
    req_data = request.json or {}
    gfw_data = req_data.get('report')

    if not gfw_data or not isinstance(gfw_data, dict):
        return jsonify({"error": "Missing or invalid 'report' data"}), 400

    farm_info          = req_data.get('farm_info') or {}
    forest_map_base64  = req_data.get('forest_map_image')
    guest_id           = req_data.get('guest_id') or farm_info.get('farm_id') or 'GUEST'
    agent_id           = req_data.get('agent_id')

    try:
        pdf_bytes = build_eudr_farm_pdf(
            farm_id           = str(guest_id),
            farm_info         = farm_info,
            gfw_data          = gfw_data,
            logo_parrot       = LOGO_PARROT,
            logo_agri         = LOGO_AGRI,
            forest_map_base64 = forest_map_base64,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Génération PDF échouée: {str(e)}"}), 500

    _log_gfw('guest_eudr_pdf', 'guest', guest_id, agent_id=agent_id)
    return _send_pdf(pdf_bytes, f'EUDR_Report_{guest_id}.pdf', as_attachment=False, browser_safe=True)

@bp.route('/guest/carbon-pdf', methods=['POST'])
def guest_carbon_pdf():
    """
    Rapport Carbon invité — 100 % backend ReportLab.
    POST /api/gfw/guest/carbon-pdf
    Body JSON attendu :
      {
        "report": {...},     # dict groupé par dataset (format CarbonReportFromFile)
        "farm_info": {...},  # optionnel
        "guest_id": "..."    # optionnel
      }
    """
    req_data = request.json or {}
    gfw_data = req_data.get('report')

    if not gfw_data or not isinstance(gfw_data, dict):
        return jsonify({"error": "Missing or invalid 'report' data"}), 400

    farm_info  = req_data.get('farm_info') or {}
    guest_id   = req_data.get('guest_id') or farm_info.get('farm_id') or 'GUEST'
    agent_id   = req_data.get('agent_id')

    # Adaptation dict groupé -> liste ordonnée attendue par build_carbon_farm_pdf
    report_list = _carbon_grouped_to_list(gfw_data)

    try:
        pdf_bytes = build_carbon_farm_pdf(
            farm_id     = str(guest_id),
            farm_info   = farm_info,
            report      = report_list,
            logo_parrot = LOGO_PARROT,
            logo_agri   = LOGO_AGRI,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Génération PDF échouée: {str(e)}"}), 500

    _log_gfw('guest_carbon_pdf', 'guest', guest_id, agent_id=agent_id)
    return _send_pdf(pdf_bytes, f'Carbon_Report_{guest_id}.pdf', as_attachment=False, browser_safe=True)


# ============================================
# ✅ NOUVEAU — EXPORT AGENT_ID (suivi terrain / commissions)
#
# agent_id est saisi librement par le guest dans StepUserInfo.jsx pour
# identifier l'agent de terrain qui l'a accompagné ; il est loggé dans
# GFWLog à chaque génération de PDF (guest_eudr_pdf / guest_carbon_pdf).
# ============================================

def _require_admin():
    """Retourne None si l'utilisateur courant est admin, sinon une réponse d'erreur."""
    user_id = get_jwt_identity()
    if isinstance(user_id, dict):
        user_id = user_id.get('id')
    user = User.query.get(user_id) if user_id is not None else None
    if not user or not user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    return None


def _agent_logs_query():
    query = GFWLog.query.filter(GFWLog.agent_id.isnot(None))

    agent_filter = request.args.get('agent_id')
    if agent_filter:
        query = query.filter(GFWLog.agent_id == agent_filter)

    date_from = request.args.get('date_from')
    if date_from:
        try:
            query = query.filter(GFWLog.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
        except ValueError:
            pass

    date_to = request.args.get('date_to')
    if date_to:
        try:
            query = query.filter(GFWLog.created_at < datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1))
        except ValueError:
            pass

    return query


def _agent_revenue_query():
    """
    Même filtres que _agent_logs_query() (agent_id, date_from, date_to) mais
    sur PaidFeatureAccess.payment_status == 'success' — chaque ligne porte le
    `amount`/`currency` FIGÉS au moment du paiement (voir create_payment_attempt),
    donc sommer ces montants donne le chiffre réel facturé par agent sur la
    période, même si le tarif de la feature a changé depuis.
    """
    query = PaidFeatureAccess.query.filter(
        PaidFeatureAccess.agent_id.isnot(None),
        PaidFeatureAccess.payment_status == 'success',
    )

    agent_filter = request.args.get('agent_id')
    if agent_filter:
        query = query.filter(PaidFeatureAccess.agent_id == agent_filter)

    date_from = request.args.get('date_from')
    if date_from:
        try:
            query = query.filter(PaidFeatureAccess.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
        except ValueError:
            pass

    date_to = request.args.get('date_to')
    if date_to:
        try:
            query = query.filter(PaidFeatureAccess.created_at < datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1))
        except ValueError:
            pass

    return query


@bp.route('/admin/agents/summary', methods=['GET'])
@jwt_required()
def agents_summary():
    """
    GET /api/gfw/admin/agents/summary — statistiques agrégées par agent_id
    (nombre de soumissions EUDR/Carbon/NDVI, montant réellement facturé par
    devise, dernière soumission), pour affichage dans une page admin avant
    export. Le nombre de rapports seul ne suffit pas pour la comptabilité
    car le prix des features peut changer dans le temps — voir amount_by_currency.
    Query params optionnels : date_from, date_to (YYYY-MM-DD).
    """
    forbidden = _require_admin()
    if forbidden:
        return forbidden

    rows = (
        _agent_logs_query().with_entities(
            GFWLog.agent_id,
            GFWLog.action_type,
            func.count(GFWLog.id),
            func.max(GFWLog.created_at),
        )
        .group_by(GFWLog.agent_id, GFWLog.action_type)
        .all()
    )

    by_agent = {}
    for agent_id, action_type, count, last_seen in rows:
        entry = by_agent.setdefault(agent_id, {
            'agent_id': agent_id, 'total': 0, 'by_action': {}, 'last_submission': None,
            'amount_by_currency': {},
        })
        entry['total'] += count
        entry['by_action'][action_type] = count
        if last_seen and (entry['last_submission'] is None or last_seen.isoformat() > entry['last_submission']):
            entry['last_submission'] = last_seen.isoformat()

    revenue_rows = (
        _agent_revenue_query().with_entities(
            PaidFeatureAccess.agent_id,
            PaidFeatureAccess.currency,
            func.sum(PaidFeatureAccess.amount),
        )
        .group_by(PaidFeatureAccess.agent_id, PaidFeatureAccess.currency)
        .all()
    )
    for agent_id, currency, total_amount in revenue_rows:
        entry = by_agent.setdefault(agent_id, {
            'agent_id': agent_id, 'total': 0, 'by_action': {}, 'last_submission': None,
            'amount_by_currency': {},
        })
        entry['amount_by_currency'][currency or 'UGX'] = float(total_amount or 0)

    agents = sorted(by_agent.values(), key=lambda a: a['total'], reverse=True)
    return jsonify({"agents": agents, "total_agents": len(agents)})


@bp.route('/admin/agents/export', methods=['GET'])
@jwt_required()
def export_agents_csv():
    """
    GET /api/gfw/admin/agents/export — export CSV brut des soumissions guest
    par agent_id (une ligne par soumission). Mêmes filtres que /summary.
    """
    forbidden = _require_admin()
    if forbidden:
        return forbidden

    logs = _agent_logs_query().order_by(GFWLog.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['agent_id', 'action_type', 'entity_type', 'entity_id', 'guest_phone', 'created_at'])
    for log in logs:
        writer.writerow([
            log.agent_id, log.action_type, log.entity_type, log.entity_id or '',
            log.guest_phone or '', log.created_at.isoformat() if log.created_at else '',
        ])

    csv_bytes = output.getvalue().encode('utf-8-sig')  # BOM : accents lisibles dans Excel
    return Response(
        csv_bytes,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=agent_submissions.csv'},
    )


@bp.route('/admin/agents/export-revenue', methods=['GET'])
@jwt_required()
def export_agents_revenue_csv():
    """
    GET /api/gfw/admin/agents/export-revenue — export CSV des paiements guest
    réussis par agent_id (une ligne par paiement, montant figé au moment du
    paiement). Complète /export (comptages) avec le montant réellement
    facturé — nécessaire car le prix des features change dans le temps.
    Mêmes filtres que /summary.
    """
    forbidden = _require_admin()
    if forbidden:
        return forbidden

    payments = _agent_revenue_query().order_by(PaidFeatureAccess.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['agent_id', 'feature_name', 'guest_phone_number', 'amount', 'currency', 'payment_method', 'created_at'])
    for p in payments:
        writer.writerow([
            p.agent_id, p.feature_name, p.guest_phone_number or '',
            p.amount if p.amount is not None else '', p.currency or '', p.payment_method or '',
            p.created_at.isoformat() if p.created_at else '',
        ])

    csv_bytes = output.getvalue().encode('utf-8-sig')
    return Response(
        csv_bytes,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=agent_revenue.csv'},
    )


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