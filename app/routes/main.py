from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('main', __name__)

@bp.route('/')
def landing():
    return render_template('main/landing.html')
@bp.route('/home')
@login_required
def home():
    return render_template('main/home.html')

@bp.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

