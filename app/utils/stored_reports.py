"""
Conservation des rapports PDF générés (invités ET utilisateurs connectés).

Un rapport ne doit pas disparaître au rechargement de la page : chaque PDF
généré est conservé sur disque sous un nom aléatoire, et la réponse porte un
en-tête X-Report-Token — jeton signé et daté qui permet de le re-télécharger
sans le régénérer, via GET /api/gfw/stored-report/<token>.

Si le PDF a été généré par un utilisateur connecté, son id est inscrit dans le
jeton : seul ce même utilisateur peut alors le re-télécharger.
"""
import os
import secrets
from datetime import datetime, timedelta

from flask import current_app, jsonify, send_file
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

STORED_REPORTS_DIR = 'uploads/stored_reports'
STORED_REPORT_RETENTION = timedelta(days=7)
os.makedirs(STORED_REPORTS_DIR, exist_ok=True)


def _serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='guest-report-pdf')


def _current_user_id():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
    except Exception:
        return None
    return identity.get('id') if isinstance(identity, dict) else identity


def _purge_old_reports():
    cutoff = (datetime.now() - STORED_REPORT_RETENTION).timestamp()
    for name in os.listdir(STORED_REPORTS_DIR):
        path = os.path.join(STORED_REPORTS_DIR, name)
        try:
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
        except OSError:
            pass


def attach_stored_report(response, pdf_bytes: bytes, filename: str):
    """Conserve pdf_bytes et ajoute X-Report-Token à `response` (réponse PDF déjà construite)."""
    _purge_old_reports()
    report_id = secrets.token_urlsafe(24)
    with open(os.path.join(STORED_REPORTS_DIR, f'{report_id}.pdf'), 'wb') as f:
        f.write(pdf_bytes)

    payload = {'id': report_id, 'name': filename}
    user_id = _current_user_id()
    if user_id is not None:
        payload['uid'] = str(user_id)

    response.headers['X-Report-Token'] = _serializer().dumps(payload)
    response.headers['Access-Control-Expose-Headers'] = 'X-Report-Token'
    return response


def send_stored_report(token):
    """Réponse Flask pour GET /stored-report/<token> : le PDF, ou 404/403/410."""
    try:
        data = _serializer().loads(token, max_age=int(STORED_REPORT_RETENTION.total_seconds()))
    except SignatureExpired:
        return jsonify({"error": "Report expired"}), 410
    except BadSignature:
        return jsonify({"error": "Invalid report link"}), 404

    if data.get('uid') is not None and str(_current_user_id()) != data['uid']:
        return jsonify({"error": "This report belongs to another account"}), 403

    report_id = str(data.get('id', ''))
    # token_urlsafe -> [A-Za-z0-9_-] uniquement (pas de secure_filename, qui retire les '_' de tête)
    if not report_id or not all(c.isalnum() or c in '-_' for c in report_id):
        return jsonify({"error": "Invalid report link"}), 404
    path = os.path.join(STORED_REPORTS_DIR, f"{report_id}.pdf")
    if not os.path.exists(path):
        return jsonify({"error": "Report expired"}), 410
    return send_file(os.path.abspath(path), mimetype='application/octet-stream',
                     as_attachment=False, download_name=data.get('name') or 'report.pdf')
