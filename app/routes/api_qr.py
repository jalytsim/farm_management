from flask import Blueprint, request, jsonify, send_file, render_template, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (QRCode, User, Farm, District, FarmerGroup, FarmData, Crop,
                        Grade, ProduceCategory, Store, Forest)
from app import db
from app.utils.site_url import site_url
import hashlib, base64, json, io, re
import qrcode
from playwright.sync_api import sync_playwright
from sqlalchemy import func
from datetime import datetime


bp = Blueprint('api_qr', __name__, url_prefix='/api/qrcode')

# Un reçu par lot 1..batch_number : sans plafond, un numéro de lot comme 2026
# demandait 2026 reçus (~500 pages) à Chromium sur un serveur à 2 vCPU.
MAX_RECEIPTS = 100


# -----------------------------------------------------------
# 🔹 UTILS : Préparer HTML multi-reçus pour le PDF
# -----------------------------------------------------------
def prepare_multi_receipt_html(receipts):
    pages_html = ""
    for start in range(0, len(receipts), 4):
        batch = receipts[start:start+4]
        while len(batch) < 4:
            batch.append("<div class='empty'></div>")
        slots_html = "".join([f"<div class='slot'>{r}</div>" for r in batch])
        pages_html += f"<div class='page'>{slots_html}</div>"

    return f"""
    <html>
    <head>
      <style>
        @page {{ size: A4; margin: 0; }}
        body {{ margin: 0; padding: 0; }}
        .page {{
          display: grid;
          grid-template-columns: 1fr 1fr;
          grid-template-rows: 1fr 1fr;
          width: 100%;
          height: 100vh;
          page-break-after: always;
        }}
        .slot {{
          border: 1px dashed #ccc;
          padding: 5px;
          display: flex;
          justify-content: center;
          align-items: center;
          overflow: hidden;
          box-sizing: border-box;
        }}
        .slot > * {{ max-width: 100%; max-height: 100%; }}
        .empty {{ background: #f9f9f9; }}
      </style>
    </head>
    <body>
      {pages_html}
    </body>
    </html>
    """


def generate_pdf_with_playwright(html_content):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content, wait_until='networkidle')

        pdf_buffer = page.pdf(
            format='A4',
            print_background=True,
            margin={'top': '1cm', 'right': '1cm', 'bottom': '1cm', 'left': '1cm'},
            display_header_footer=True,
            header_template="<div style='font-size:10px;text-align:center;width:100%;'>www.nkusu.com</div>",
            footer_template="<div style='font-size:10px;text-align:center;width:100%;'>Page <span class='pageNumber'></span> sur <span class='totalPages'></span></div>"
        )

        browser.close()
        return pdf_buffer


def qr_png_data_uri(content: str) -> str:
    img = qrcode.make(content, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def public_trace_url(qr: QRCode) -> str:
    # Le QR imprimé ouvre la page publique de traçabilité de CE reçu
    # (fermes, culture, grade, entrepôt), au lieu d'un JSON illisible au scan.
    return f"{site_url()}/trace/{qr.hash_md5}"


# -----------------------------------------------------------
# 🔹 Sauvegarde du QR en DB avec suivi
# -----------------------------------------------------------
def save_qr_in_db(data: dict, user_id: int, description: str = None, qr_type: str = "default"):
    # Convert dict → JSON string stable
    data_str = json.dumps(data, sort_keys=True)

    # Hash MD5 sur la string
    hash_md5 = hashlib.md5(data_str.encode()).hexdigest()

    # Encodage en base64
    data_b64 = base64.b64encode(data_str.encode()).decode()

    # Vérifie si déjà existant
    # hash_md5 est UNIQUE en base : filtrer aussi par created_by faisait planter
    # (IntegrityError) quand un autre utilisateur avait déjà émis le même reçu.
    qr = QRCode.query.filter_by(hash_md5=hash_md5).first()
    if not qr:
        qr = QRCode(
            hash_md5=hash_md5,
            data_base64=data_b64,
            description=description,
            qr_type=qr_type,
            created_by=user_id
        )
        db.session.add(qr)
        db.session.commit()

    return qr


# -----------------------------------------------------------
# 🔹 UTILS : Gestion du scope admin (mine|all)
# -----------------------------------------------------------
def _is_admin(user_id):
    """Vérifie is_admin directement en DB (fiable, indépendant du contenu du JWT)."""
    user = User.query.get(user_id)
    return bool(user and user.is_admin)


def _resolve_scope(user_id):
    """
    Lit ?scope=mine|all dans la query string.
    'all' n'est honoré que si l'utilisateur est admin ; sinon on retombe sur 'mine'.
    Retourne (scope, is_admin).
    """
    is_admin = _is_admin(user_id)
    scope = request.args.get('scope', 'mine')
    if scope not in ('mine', 'all'):
        scope = 'mine'
    if scope == 'all' and not is_admin:
        scope = 'mine'
    return scope, is_admin


# -----------------------------------------------------------
# 🔹 API : Génération PDF de QR Codes
# -----------------------------------------------------------
@bp.route('/generate_pdf', methods=['POST'])
@jwt_required()
def generate_pdfs():
    try:
        identity = get_jwt_identity()
        user_id = identity['id']

        data = request.get_json()
        if not data or 'qr_data_list' not in data:
            return jsonify({"error": "Invalid JSON payload. 'qr_data_list' is required."}), 400

        qr_data_list = data['qr_data_list']
        if not isinstance(qr_data_list, list) or not qr_data_list:
            return jsonify({"error": "'qr_data_list' must be a non-empty list."}), 400
        if len(qr_data_list) > MAX_RECEIPTS:
            return jsonify({"error": f"At most {MAX_RECEIPTS} receipts per PDF "
                                     f"({len(qr_data_list)} requested)."}), 400
        description = data.get('description', "Automatically generated receipt by Nkusu.")
        qr_type = data.get('qr_type', "default")

        receipts, hashes = [], []
        for qr_data in qr_data_list:
            qr = save_qr_in_db(qr_data, user_id, description, qr_type=qr_type)
            hashes.append(qr.hash_md5)
            receipt_html = render_template('qrcode.html', description=description,
                                           qr_src=qr_png_data_uri(public_trace_url(qr)))
            receipts.append(receipt_html)

        html_content = prepare_multi_receipt_html(receipts)
        pdf_buffer = generate_pdf_with_playwright(html_content)

        # En mémoire : le fichier temporaire d'avant n'était jamais supprimé
        resp = send_file(io.BytesIO(pdf_buffer), as_attachment=True,
                         download_name='receipts.pdf', mimetype='application/pdf')
        # Le front affiche le lien public de chaque reçu sous l'aperçu
        resp.headers['X-Trace-Hashes'] = ','.join(hashes)
        resp.headers['Access-Control-Expose-Headers'] = 'X-Trace-Hashes, Content-Disposition'
        return resp

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error generating PDF: {str(e)}"}), 500


# -----------------------------------------------------------
# 🔹 API : Stats & Suivi des QR Codes
# -----------------------------------------------------------
@bp.route('/stats/count', methods=['GET'])
@jwt_required()
def qr_count():
    identity = get_jwt_identity()
    user_id = identity['id']
    scope, is_admin = _resolve_scope(user_id)

    query = QRCode.query
    if scope == 'mine':
        query = query.filter_by(created_by=user_id)
    count = query.count()

    return jsonify({"user_id": user_id, "count": count, "scope": scope, "is_admin": is_admin})


@bp.route('/stats/list', methods=['GET'])
@jwt_required()
def qr_list():
    identity = get_jwt_identity()
    user_id = identity['id']
    scope, is_admin = _resolve_scope(user_id)

    # Pagination simple (utile pour le dashboard, évite de charger toute la table)
    try:
        limit = min(int(request.args.get('limit', 100)), 200)
    except ValueError:
        limit = 100
    try:
        offset = max(int(request.args.get('offset', 0)), 0)
    except ValueError:
        offset = 0

    query = QRCode.query
    if scope == 'mine':
        query = query.filter_by(created_by=user_id)
    qrs = query.order_by(QRCode.date_created.desc()).offset(offset).limit(limit).all()

    # Map created_by -> username utile seulement en vue admin ("all")
    creators = {}
    if scope == 'all':
        user_ids = {qr.created_by for qr in qrs if qr.created_by}
        if user_ids:
            creators = {u.id: u.username for u in User.query.filter(User.id.in_(user_ids)).all()}

    return jsonify([
        {
            "hash": qr.hash_md5,
            "type": qr.qr_type,
            "description": qr.description,
            "batch_number": qr.data_dict.get("batch_number"),
            "created_by": qr.created_by,
            "created_by_username": creators.get(qr.created_by) if scope == 'all' else None,
            "created_at": qr.date_created.isoformat()
        }
        for qr in qrs
    ])


@bp.route('/stats/by_type', methods=['GET'])
@jwt_required()
def qr_by_type():
    identity = get_jwt_identity()
    user_id = identity['id']
    scope, is_admin = _resolve_scope(user_id)

    q = db.session.query(QRCode.qr_type, func.count(QRCode.id))
    if scope == 'mine':
        q = q.filter(QRCode.created_by == user_id)
    stats = q.group_by(QRCode.qr_type).all()

    return jsonify({t or "unknown": c for t, c in stats})


# -----------------------------------------------------------
# 🔹 API : Dashboard agrégé (1 seul appel pour toute la vue)
# -----------------------------------------------------------
@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def qr_dashboard():
    identity = get_jwt_identity()
    user_id = identity['id']
    scope, is_admin = _resolve_scope(user_id)

    try:
        recent_limit = min(int(request.args.get('limit', 20)), 100)
    except ValueError:
        recent_limit = 20

    base_query = QRCode.query
    if scope == 'mine':
        base_query = base_query.filter(QRCode.created_by == user_id)

    total_count = base_query.count()

    # Répartition par type
    type_q = db.session.query(QRCode.qr_type, func.count(QRCode.id))
    if scope == 'mine':
        type_q = type_q.filter(QRCode.created_by == user_id)
    type_stats = type_q.group_by(QRCode.qr_type).all()

    # Répartition par lot (description)
    lot_q = db.session.query(QRCode.description, func.count(QRCode.id))
    if scope == 'mine':
        lot_q = lot_q.filter(QRCode.created_by == user_id)
    lot_stats = lot_q.filter(QRCode.description.isnot(None)).group_by(QRCode.description).all()
    top_lots = sorted(lot_stats, key=lambda x: x[1], reverse=True)[:10]

    # Derniers QR générés
    recent = base_query.order_by(QRCode.date_created.desc()).limit(recent_limit).all()

    creators = {}
    if scope == 'all':
        user_ids = {qr.created_by for qr in recent if qr.created_by}
        if user_ids:
            creators = {u.id: u.username for u in User.query.filter(User.id.in_(user_ids)).all()}

    return jsonify({
        "scope": scope,
        "is_admin": is_admin,
        "total_count": total_count,
        "distinct_lots": len(lot_stats),
        "by_type": {t or "unknown": c for t, c in type_stats},
        "top_lots": [{"description": d, "count": c} for d, c in top_lots],
        "recent": [
            {
                "hash": qr.hash_md5,
                "type": qr.qr_type,
                "description": qr.description,
                "batch_number": qr.data_dict.get("batch_number"),
                "created_by": qr.created_by,
                "created_by_username": creators.get(qr.created_by) if scope == 'all' else None,
                "created_at": qr.date_created.isoformat(),
            }
            for qr in recent
        ],
    })


# -----------------------------------------------------------
# 🔹 API : Vérification d’un QR existant
# -----------------------------------------------------------
@bp.route('/check_qr', methods=['POST'])
@jwt_required()
def check_qr():
    data = request.get_json()
    qr_data = data.get("qr_data")
    if not qr_data:
        return jsonify({"error": "qr_data is required"}), 400

    if isinstance(qr_data, dict):
        qr_str = json.dumps(qr_data, sort_keys=True)
    else:
        qr_str = str(qr_data)

    hash_md5 = hashlib.md5(qr_str.encode()).hexdigest()
    qr = QRCode.query.filter_by(hash_md5=hash_md5).first()

    if not qr:
        return jsonify({"exists": False}), 404

    return jsonify({
        "exists": True,
        "hash": qr.hash_md5,
        "type": qr.qr_type,
        "description": qr.description,
        "batch_number": qr.data_dict.get("batch_number"),
        "created_by": qr.created_by,
        "created_at": qr.date_created.isoformat()
    })


# -----------------------------------------------------------
# 🔹 API : QR Codes par description (= lot)
# -----------------------------------------------------------
@bp.route('/stats/by_description', methods=['GET'])
@jwt_required()
def qr_by_description():
    identity = get_jwt_identity()
    user_id = identity['id']
    scope, is_admin = _resolve_scope(user_id)
    description = request.args.get("description")

    if not description:
        return jsonify({"error": "description is required"}), 400

    query = QRCode.query.filter_by(description=description)
    if scope == 'mine':
        query = query.filter_by(created_by=user_id)
    qrs = query.all()

    return jsonify([
        {
            "hash": qr.hash_md5,
            "batch_number": qr.data_dict.get("batch_number"),
            "created_at": qr.date_created.isoformat()
        }
        for qr in sorted(qrs, key=lambda x: int(x.data_dict.get("batch_number") or 0))
    ])


# -----------------------------------------------------------
# 🔹 API : QR spécifique d’un lot (description + batch_number)
# -----------------------------------------------------------
@bp.route('/stats/by_batch', methods=['GET'])
@jwt_required()
def qr_by_batch():
    identity = get_jwt_identity()
    user_id = identity['id']
    scope, is_admin = _resolve_scope(user_id)
    description = request.args.get("description")
    batch_number = request.args.get("batch_number")

    if not description or not batch_number:
        return jsonify({"error": "description and batch_number are required"}), 400

    query = QRCode.query.filter_by(description=description)
    if scope == 'mine':
        query = query.filter_by(created_by=user_id)
    qrs = query.all()

    for qr in qrs:
        if qr.data_dict.get("batch_number") == str(batch_number):
            return jsonify({
                "hash": qr.hash_md5,
                "description": qr.description,
                "batch_number": batch_number,
                "created_at": qr.date_created.isoformat()
            })

    return jsonify({"error": "QR not found"}), 404

# -----------------------------------------------------------
# 🔹 API PUBLIQUE : page de traçabilité d'un reçu QR (sans compte)
# -----------------------------------------------------------
# C'est là qu'arrive le QR imprimé (/trace/<hash>). Tout ce qu'on sait du reçu :
# fermes (identité, district, groupement, GPS, cultures déclarées), culture,
# catégorie, grade, entrepôt, émetteur. Volontairement exclus : CIN et
# numéro d'identité nationale. Téléphones affichés en entier (demande client).

def _phone(phone):
    phone = str(phone or '').strip()
    return phone or None


def _safe(fn, default=None):
    # Page publique : une info annexe illisible (colonne absente en prod, donnée
    # corrompue) ne doit pas faire tomber toute la page en 500.
    try:
        return fn()
    except Exception:
        current_app.logger.exception("QR public trace: enrichment failed")
        db.session.rollback()
        return default


def _iso(d):
    return d.isoformat() if d else None


def _find_farm(value):
    value = str(value or '').strip()
    if not value:
        return None
    farm = Farm.query.get(int(value)) if value.isdigit() else None
    return farm or Farm.query.filter_by(farm_id=value).first()


def _farm_public(farm, receipt_phone=None, qty=None):
    district = District.query.get(farm.district_id) if farm.district_id else None
    group = FarmerGroup.query.get(farm.farmergroup_id) if farm.farmergroup_id else None
    records = _safe(lambda: FarmData.query.filter_by(farm_id=farm.farm_id)
                    .order_by(FarmData.date_created.desc()).limit(20).all(), [])
    crops = []
    for r in records:
        crop = Crop.query.get(r.crop_id)
        crops.append({
            'crop': crop.name if crop else None,
            'land_type': r.land_type,
            'tilled_land_size': r.tilled_land_size,
            'planting_date': _iso(r.planting_date),
            'harvest_date': _iso(r.harvest_date),
            'season': r.season,
            'quality': r.quality,
            'quantity': r.quantity,
            'expected_yield': r.expected_yield,
            'actual_yield': r.actual_yield,
            'number_of_trees': r.number_of_tree,
            'hs_code': r.hs_code,
        })
    return {
        'farm_id': farm.farm_id,
        'name': farm.name,
        'subcounty': farm.subcounty,
        'country': farm.country,
        'district': district.name if district else None,
        'region': district.region if district else None,
        'farmer_group': group.name if group else None,
        'geolocation': farm.geolocation,
        'gender': farm.gender,
        'phone': _phone(receipt_phone or farm.phonenumber or farm.phonenumber2),
        'quantity_kg': qty,
        'crops': crops,
    }


@bp.route('/public/<string:hash_md5>', methods=['GET'])
def public_trace(hash_md5):
    if not re.fullmatch(r'[0-9a-f]{32}', hash_md5 or ''):
        return jsonify({"error": "Invalid code."}), 400
    qr = QRCode.query.filter_by(hash_md5=hash_md5).first()
    if not qr:
        return jsonify({"error": "This QR code is not registered on Nkusu."}), 404

    data = qr.data_dict
    # Lu avant les enrichissements : _safe() peut faire un rollback qui expire qr
    meta = {'hash': qr.hash_md5, 'type': qr.qr_type, 'description': qr.description,
            'issued_at': _iso(qr.date_created), 'created_by': qr.created_by}

    # Fermes : clés farm_<i>_id / _phone / _qty du formulaire
    indices = sorted({int(m.group(1)) for k in data
                      for m in [re.fullmatch(r'farm_(\d+)_id', k)] if m})
    farms = []
    for i in indices:
        raw_id = data.get(f'farm_{i}_id')
        farm = _find_farm(raw_id)
        if farm:
            farms.append(_farm_public(farm, data.get(f'farm_{i}_phone'), data.get(f'farm_{i}_qty')))
        elif raw_id:
            farms.append({'farm_id': str(raw_id), 'name': None, 'unknown': True,
                          'quantity_kg': data.get(f'farm_{i}_qty'), 'crops': []})

    # Culture / catégorie / grade (Produce : crop_id + Crop_grade ; Export : crop + crop_grade)
    crop_ref = str(data.get('crop_id') or data.get('crop') or '').strip()
    crop = Crop.query.get(int(crop_ref)) if crop_ref.isdigit() else None
    category = crop.category.name if crop and crop.category else None
    if not category:
        cat_ref = str(data.get('crop_category') or '').strip()
        cat = ProduceCategory.query.get(int(cat_ref)) if cat_ref.isdigit() else None
        category = cat.name if cat else (data.get('produceCategory') or cat_ref or None)
    grade_value = data.get('Crop_grade') or data.get('crop_grade')
    grade = (_safe(lambda: Grade.query.filter_by(crop_id=crop.id, grade_value=grade_value).first())
             if crop and grade_value else None)
    product = {
        'category': category,
        'crop': crop.name if crop else None,
        'grade': grade_value,
        'grade_description': grade.description if grade else None,
        'variety': _safe(lambda: grade.variety.name if grade and grade.variety else None),
    }

    # Entrepôt
    store = None
    store_ref = str(data.get('store_id') or '').strip()
    if store_ref.isdigit():
        s = _safe(lambda: Store.query.get(int(store_ref)))
        if s:
            store = {
                'name': s.name, 'code': s.code, 'location': s.location,
                'district': s.district, 'country': s.country, 'type': s.store_type,
                'certified': bool(s.is_certified), 'phone': s.phone_number, 'email': s.email,
            }
    if not store and data.get('store_name'):
        store = {'name': data.get('store_name')}

    # Forêt (reçus Conservation)
    forest = None
    forest_ref = str(data.get('forest_id') or '').strip()
    if forest_ref.isdigit():
        f = _safe(lambda: Forest.query.get(int(forest_ref)))
        if f:
            forest = {'name': f.name, 'tree_type': f.tree_type, 'country': f.country}

    issuer = _safe(lambda: User.query.get(meta['created_by'])) if meta['created_by'] else None

    # Le reste des champs du reçu, tels que saisis (sans les clés de fermes
    # déjà détaillées ni les identifiants internes)
    hidden = {'crop_id', 'store_id'}
    details = {k: v for k, v in data.items()
               if not k.startswith('farm_') and k not in hidden and v not in (None, '')}

    return jsonify({
        'hash': meta['hash'],
        'type': meta['type'],
        'description': meta['description'],
        'issued_at': meta['issued_at'],
        'issuer': (issuer.company_name or issuer.username) if issuer else None,
        'batch_number': data.get('batch_number'),
        'farms': farms,
        'product': product,
        'store': store,
        'forest': forest,
        'details': details,
    })
