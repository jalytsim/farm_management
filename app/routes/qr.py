from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('qr', __name__)

@bp.route('/qrcode')
@login_required
def qrcode():
    return render_template('codeQr.html')
