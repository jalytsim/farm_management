from flask import Blueprint, request, jsonify, send_file, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import QRCode, User
from app import db
import hashlib, base64, tempfile, json
from playwright.sync_api import sync_playwright
from sqlalchemy import func
from datetime import datetime


bp = Blueprint('api_qr', __name__, url_prefix='/api/qrcode')


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
    qr = QRCode.query.filter_by(hash_md5=hash_md5, created_by=user_id).first()
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
        description = data.get('description', "Automatically generated receipt by Nkusu.")
        qr_type = data.get('qr_type', "default")

        receipts = []
        for qr_data in qr_data_list:
            save_qr_in_db(qr_data, user_id, description, qr_type=qr_type)
            receipt_html = render_template('qrcode.html', description=description, qr_data=qr_data)
            receipts.append(receipt_html)

        html_content = prepare_multi_receipt_html(receipts)
        pdf_buffer = generate_pdf_with_playwright(html_content)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(pdf_buffer)
        temp_file.close()

        return send_file(temp_file.name, as_attachment=True, download_name='receipts.pdf', mimetype='application/pdf')

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