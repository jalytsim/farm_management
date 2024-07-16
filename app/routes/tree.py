from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
import os
from app import Config 
from app.models import Forest, Tree
from app.routes.forest import forest_or_admin_required
from app.utils.tree_utils import create_tree, delete_tree, get_all_tree, get_tree_by_id, update_tree

bp = Blueprint('tree', __name__)



@bp.route('/trees', methods=['GET'])
@login_required
@forest_or_admin_required
def list_trees():
    districts = get_all_tree()
    return render_template('tree/list.html', districts=districts)

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
        region = request.form.get('region')
        create_tree(name, region)
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
        region = request.form.get('region')
        update_tree(tree_id, name, region)
        print('Tree updated successfully.', 'success')
        return redirect(url_for('tree.list_trees'))
    return render_template('tree/edit.html', tree=tree)

@bp.route('/tree/delete/<int:tree_id>', methods=['POST'])
@login_required
@forest_or_admin_required
def delete_tree_route(tree_id):
    delete_tree(tree_id)
    print('Tree deleted successfully.', 'success')
    return redirect(url_for('tree.list_trees'))