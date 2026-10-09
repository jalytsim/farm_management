"""
api_notifications.py — SMS et Email avec journalisation SMSLog.
"""

from flask import Blueprint, request, jsonify
import requests
import urllib3
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from urllib.parse import urlencode

import os

from flask_jwt_extended import get_jwt_identity, jwt_required

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api_notifications_bp = Blueprint('api_notifications', __name__, url_prefix='/api/notifications')

# Plusieurs SMS concaténés au maximum (alertes météo/ravageurs incluses).
SMS_MAX_LENGTH = 1600


def deliver_sms(phone, message, user_id=None):
    """
    Envoie un SMS et le journalise. Appelé par la route /sms ET directement
    par les schedulers (alertes météo/ravageurs) — plus d'appel HTTP interne.
    Retourne le code HTTP du fournisseur (None si injoignable).
    """
    try:
        query = urlencode({"msg": message, "msisdns": phone})
        url   = f"https://188.166.125.28/nkusu-iot/api/nkusu-iot/sms?{query}"
        res   = requests.get(url, verify=False, timeout=15)
    except Exception:
        _log_sms(user_id, phone, message, 'failed', None)
        raise
    _log_sms(user_id, phone, message, 'success' if res.status_code == 200 else 'failed', res.status_code)
    return res.status_code


# 🔒 Authentification obligatoire : sans elle, n'importe qui pouvait envoyer
# un SMS arbitraire à n'importe quel numéro aux frais de Nkusu.
@api_notifications_bp.route('/sms', methods=['POST'])
@jwt_required()
def send_sms():
    data    = request.get_json(silent=True) or {}
    phone   = data.get("phone")
    message = data.get("message")

    if not phone or not message:
        return jsonify({"error": "Missing phone or message"}), 400
    if len(str(message)) > SMS_MAX_LENGTH:
        return jsonify({"error": f"Message too long (max {SMS_MAX_LENGTH} characters)"}), 400

    identity = get_jwt_identity()
    user_id  = identity['id'] if isinstance(identity, dict) else identity

    try:
        code = deliver_sms(phone, message, user_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"status": f"Message sent to {phone}", "remote_status": code}), code


def _log_sms(user_id, phone, message, status, http_code):
    """Insère un enregistrement SMSLog sans propager les exceptions."""
    try:
        from app import db
        from app.models import SMSLog
        log = SMSLog(
            user_id   = user_id,
            phone     = phone,
            message   = message,
            status    = status,
            http_code = http_code,
        )
        db.session.add(log)
        db.session.commit()
    except Exception as err:
        print(f"[SMSLog] Erreur lors de la journalisation : {err}")


# 🔒 Authentification obligatoire (sinon relais d'emails ouvert depuis le compte
# Gmail de Nkusu). Identifiants SMTP lus dans l'environnement, plus dans le code.
@api_notifications_bp.route('/email', methods=['POST'])
@jwt_required()
def send_email_with_attachment():
    data       = request.get_json()
    to_email   = data.get("to_email")
    report_type = data.get("report_type", "Report")
    pdf_base64 = data.get("pdf_base64")

    if not to_email or not pdf_base64:
        return jsonify({"error": "Missing to_email or pdf_base64"}), 400

    try:
        pdf_bytes = base64.b64decode(pdf_base64)

        from_email = os.getenv("SMTP_USER")
        password   = os.getenv("SMTP_PASSWORD")
        if not from_email or not password:
            return jsonify({"error": "Email sending is not configured (SMTP_USER / SMTP_PASSWORD)"}), 503

        msg = MIMEMultipart()
        msg['From']    = from_email
        msg['To']      = to_email
        msg['Subject'] = f"{report_type} PDF Report"

        body = f"Hello,\n\nPlease find attached your {report_type} report.\n\nBest regards."
        msg.attach(MIMEText(body, 'plain'))

        part = MIMEApplication(pdf_bytes, _subtype='pdf')
        part.add_header('Content-Disposition', 'attachment',
                        filename=f'{report_type}_Report.pdf')
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()

        return jsonify({"status": "sent"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500