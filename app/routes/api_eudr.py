# app/api/eudr_submission.py
from flask import Blueprint, request, jsonify
from app.services.eudr_submission import submit_statement

bp = Blueprint('api_eudr_submission', __name__, url_prefix='/api/eudr')

@bp.route('/submit', methods=['POST'])
def submit():
    payload = request.json
    response = submit_statement(payload)
    return jsonify({
        'status_code': response.status_code,
        'response': response.text
    }), response.status_code
