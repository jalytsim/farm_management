from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
from app import Config 
from app.utils.district_utils import get_all_districts
from app.utils.forest_utils import create_forest, delete_forest, get_all_forests, update_forest
from app.utils.point_utils import get_all_points

bp = Blueprint('forest', __name__)


def forest_or_admin_required(f):
    @login_required
    def wrap(*args, **kwargs):
        if current_user.user_type != 'forest' and not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@bp.route('/forest')
@login_required
@forest_or_admin_required
def index():
    forests = get_all_forests()
    points = get_all_points()
    districts = get_all_districts()
    owner_types = ['Farmer', 'Forest', 'Both']
    return render_template('forest/forest.html', forests=forests, points=points, districts=districts, owner_types=owner_types)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@bp.route('/forest/create')
@login_required
@forest_or_admin_required
def handle_create_forest():
    if request.method == 'POST':
        name = request.form['name']
        
        if 'image' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['image']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)  # Create the UPLOAD_FOLDER if it doesn't exist
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            create_forest(name)
            return redirect(url_for('forest.index'))
        else:
            flash('Invalid file format. Allowed formats are png, jpg, jpeg, gif', 'danger')
            return redirect(request.url)
    return redirect(url_for('forest.index'))
    
    
@bp.route('/forest/update/<int:id>', methods=['POST'])
@login_required
@forest_or_admin_required
def handle_update_forest(id):
    name = request.form['name']
    update_forest(id, name)
    return redirect(url_for('forest.index'))

@bp.route('/forest/delete/<int:id>', methods=['POST'])
@login_required
@forest_or_admin_required
def handle_delete_forest(id):
    delete_forest(id)
    return redirect(url_for('forest.index'))

@bp.route('/forest/view')
@login_required
@forest_or_admin_required
def view():
    forests = get_all_forests()
    points = get_all_points()
    return render_template('forest/forest.html', forests=forests, points=points)