from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
from app import Config 
from app.models import Forest
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
@forest_or_admin_required
def index():
    page = request.args.get('page', 1, type=int)
    
    # Check if the user is an admin
    if current_user.is_admin:
        forests = Forest.query.paginate(page=page, per_page=6)
    else:
        forests = Forest.query.filter_by(created_by=current_user.id).paginate(page=page, per_page=6)

    points = get_all_points()
    districts = get_all_districts()
    owner_types = ['Farmer', 'Forest', 'Both']
    
    return render_template('forest/forest.html', forests=forests, points=points, districts=districts, owner_types=owner_types)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@bp.route('/forest/create', methods=['POST'])
@forest_or_admin_required
def handle_create_forest():
    if request.method == 'POST':
        name = request.form.get('name')
        
        if 'image' in request.files:
            file = request.files['image']
        
            if file.filename != '':
                if not allowed_file(file.filename):
                    flash('Invalid file format. Allowed formats are png, jpg, jpeg, gif', 'danger')
                    return redirect(request.url)
                
                filename = secure_filename(file.filename)
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)  # Create the UPLOAD_FOLDER if it doesn't exist
                file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            else:
                filename = None
        else:
            filename = None

        create_forest(name)
        flash('Forest created successfully', 'success')
        return redirect(url_for('forest.index'))
    
    return redirect(url_for('forest.index'))

    
    
@bp.route('/forest/update/<int:id>', methods=['POST'])
@forest_or_admin_required
def handle_update_forest(id):
    name = request.form['name']
    update_forest(id, name)
    return redirect(url_for('forest.index'))

@bp.route('/forest/delete/<int:id>', methods=['POST'])
@forest_or_admin_required
def handle_delete_forest(id):
    delete_forest(id)
    return redirect(url_for('forest.index'))

@bp.route('/forest/view')
@forest_or_admin_required
def view():
    forests = get_all_forests()
    points = get_all_points()
    return render_template('forest/forest.html', forests=forests, points=points)