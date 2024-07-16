from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Forest, Tree
from app.routes.forest import forest_or_admin_required
from app.utils.qr_generator import generate_qr_codes_dynamic
from app.utils.tree_utils import create_tree, delete_tree, get_all_tree, get_tree_by_id, update_tree

bp = Blueprint('tree', __name__)

@bp.route('/trees', methods=['GET'])
@login_required
@forest_or_admin_required
def list_trees():
    trees = get_all_tree()
    return render_template('tree/list.html', trees=trees)

@bp.route('/tree/<int:tree_id>', methods=['GET'])
@login_required
@forest_or_admin_required
def view_tree(tree_id):
    tree = get_tree_by_id(tree_id)
    return render_template('tree/view.html', tree=tree)

@bp.route('/trees/create', methods=['GET', 'POST'])
@login_required
@forest_or_admin_required
def create_tree_route():
    if request.method == 'POST':
        name = request.form.get('name')
        type = request.form.get('type')
        forest_id = request.form.get('forest_id')
        point_id = request.form.get('point_id')
        date_planted = request.form.get('date_planted')
        cutting_date = request.form.get('cutting_date')
        height = request.form.get('height')
        diameter = request.form.get('diameter')
        created_by = current_user.id  # Assuming you have current_user

        create_tree(name, type, forest_id, point_id, date_planted, cutting_date, height, diameter, created_by)
        flash('Tree created successfully.', 'success')
        return redirect(url_for('tree.list_trees'))
    return render_template('tree/create.html')

@bp.route('/tree/edit/<int:tree_id>', methods=['GET', 'POST'])
@login_required
@forest_or_admin_required
def edit_tree_route(tree_id):
    tree = get_tree_by_id(tree_id)
    if request.method == 'POST':
        name = request.form.get('name')
        type = request.form.get('type')
        forest_id = request.form.get('forest_id')
        point_id = request.form.get('point_id')
        date_planted = request.form.get('date_planted')
        cutting_date = request.form.get('cutting_date')
        height = request.form.get('height')
        diameter = request.form.get('diameter')
        modified_by = current_user.id  # Assuming you have current_user

        update_tree(tree_id, name, type, forest_id, point_id, date_planted, cutting_date, height, diameter, modified_by)
        flash('Tree updated successfully.', 'success')
        return redirect(url_for('tree.list_trees'))
    return render_template('tree/edit.html', tree=tree)

@bp.route('/tree/delete/<int:tree_id>', methods=['POST'])
@login_required
@forest_or_admin_required
def delete_tree_route(tree_id):
    delete_tree(tree_id)
    flash('Tree deleted successfully.', 'success')
    return redirect(url_for('tree.list_trees'))

@bp.route('/tree/qr/<int:tree_id>', methods=['GET'])
@login_required
@forest_or_admin_required
def qr_tree_route(tree_id):
    tree = get_tree_by_id(tree_id)
    if tree is None:
        flash('Tree not found.', 'error')
        return redirect(url_for('tree.list_trees'))

    data = f"Forest ID: {tree.forest_id}\nTree ID: {tree.id}\nType: {tree.type}\nCutting Date: {tree.date_cut}\nHeight: {tree.height}\nDiameter: {tree.diameter}"
    pdf_filename = f"tree_{tree.id}_qr_code.pdf"
    qr_pdf_path = generate_qr_codes_dynamic(data, pdf_filename)

    return send_file(qr_pdf_path, as_attachment=True, download_name=pdf_filename, mimetype='application/pdf')
