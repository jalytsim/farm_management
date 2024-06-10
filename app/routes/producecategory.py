from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import ProduceCategory, db, FarmerGroup
from app.routes.farm import farmer_or_admin_required
from app.utils import producecategory_utils

bp = Blueprint('producecategory', __name__)

@bp.route('/producecategory')
@login_required
@farmer_or_admin_required
def index():
    pcs = ProduceCategory.query.all()
    return render_template('producecategory/index.html', pcs=pcs)
@bp.route('/producecategory/create', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def create_pc():
    if request.method == 'POST':
        name = request.form['name']
        grade = request.form['grade']

        producecategory_utils.create_pc(name, grade)
        return redirect(url_for('producecategory.index'))

    return render_template('producecategory/index.html')


@bp.route('/producecategory/<int:pc_id>/edit', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def edit_pc(pc_id):
    pcs = ProduceCategory.query.all()
    if request.method == 'POST':
        pcs = ProduceCategory.query.get_or_404(pc_id)
        name = request.form['name']
        grade = request.form['grade']
        producecategory_utils.update_pc(pc, name,grade)
        return redirect(url_for('producecategory.index'))
    return render_template('producecategory/index.html', pcs=pcs)

@bp.route('/producecategory/<int:pc_id>/delete', methods=['POST'])
@login_required
@farmer_or_admin_required
def delete_pc(pc_id):
    pc = ProduceCategory.query.get_or_404(pc_id)
    producecategory_utils.delete_pc(pc_id)
    return redirect(url_for('producecategory.index'))