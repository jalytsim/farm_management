from flask import Blueprint, request, jsonify
import requests
import urllib3
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
        res = requests.get(url, verify=False)  # <-- désactive vérif SSL
        return jsonify({"status": res.status_code}), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

