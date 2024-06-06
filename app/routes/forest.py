from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required

from app.utils.forest_utils import create_forest, delete_forest, get_all_forests, update_forest
from app.utils.point_utils import get_all_points

bp = Blueprint('forest', __name__)

@bp.route('/forest')
@login_required
def index():
    forests = get_all_forests()
    points = get_all_points()
    return render_template('forest.html', forests=forests, points=points)

@bp.route('/forest/create', methods=['POST'])
@login_required
def handle_create_forest():
    name = request.form['name']
    create_forest(name)
    return redirect(url_for('forest.index'))

@bp.route('/forest/update/<int:id>', methods=['POST'])
@login_required
def handle_update_forest(id):
    name = request.form['name']
    update_forest(id, name)
    return redirect(url_for('forest.index'))

@bp.route('/forest/delete/<int:id>', methods=['POST'])
@login_required
def handle_delete_forest(id):
    delete_forest(id)
    return redirect(url_for('forest.index'))

@bp.route('/forest/view')
@login_required
def view():
    forests = get_all_forests()
    points = get_all_points()
    return render_template('forest.html', forests=forests, points=points)