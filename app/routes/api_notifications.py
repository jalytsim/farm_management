from flask import Blueprint, request, jsonify
import requests
import urllib3
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api_notifications_bp = Blueprint('api_notifications', __name__, url_prefix='/api/notifications')


@api_notifications_bp.route('/sms', methods=['POST'])
def send_sms():
    data = request.get_json()
    phone = data.get("phone")
    message = data.get("message")

    if not phone or not message:
        return jsonify({"error": "Missing phone or message"}), 400

    try:
        url = f"https://188.166.125.28/nkusu-iot/api/nkusu-iot/sms?msg={message}&msisdns={phone}"
        res = requests.get(url, verify=False)
        return jsonify({"status": res.status_code}), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_notifications_bp.route('/email', methods=['POST'])
def send_email_with_attachment():
    data = request.get_json()
    to_email = data.get("to_email")
    report_type = data.get("report_type", "Report")
    pdf_base64 = data.get("pdf_base64")

    if not to_email or not pdf_base64:
        return jsonify({"error": "Missing to_email or pdf_base64"}), 400

    try:
        # Convert base64 to bytes
        pdf_bytes = base64.b64decode(pdf_base64)

        # Email config
        from_email = "nomenatsimijaly@gmail.com"  # Remplace par ton adresse Gmail
        password = "rmiiwmaknfggxzlw"       # Mot de passe d'application Gmail

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = f"{report_type} PDF Report"

        # Email body
        body = f"Hello,\n\nPlease find attached your {report_type} report.\n\nBest regards."
        msg.attach(MIMEText(body, 'plain'))

        # Attachment
        part = MIMEApplication(pdf_bytes, _subtype='pdf')
        part.add_header('Content-Disposition', 'attachment', filename=f'{report_type}_Report.pdf')
        msg.attach(part)

        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()

        return jsonify({"status": "sent"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
