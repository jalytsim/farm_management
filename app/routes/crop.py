# routes/crop_routes.py
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import ProduceCategory, db, Crop
from app.routes.farm import farmer_or_admin_required

crop_bp = Blueprint('crop', __name__, url_prefix='/crop')

@crop_bp.route('/')
@login_required
@farmer_or_admin_required
def index():
    crops = Crop.query.all()
    categories = ProduceCategory.query.all()
    return render_template('crop/index.html', crops=crops, categories=categories)

@crop_bp.route('/create', methods=['POST'])
@login_required
@farmer_or_admin_required
def create_crop():
    name = request.form.get('name')
    weight = request.form.get('weight')
    category_id = request.form.get('category_id')
    new_crop = Crop(
        name=name,
        weight=weight,
        category_id=category_id,
        created_by=current_user.id,
        modified_by=current_user.id,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )
    db.session.add(new_crop)
    db.session.commit()
    flash('Crop created successfully!', 'success')
    return redirect(url_for('crop.index'))

@crop_bp.route('/<int:id>/edit', methods=['POST'])
@login_required
@farmer_or_admin_required
def edit_crop(id):
    crop = Crop.query.get_or_404(id)
    crop.name = request.form.get('name')
    crop.weight = request.form.get('weight')
    crop.category_id = request.form.get('category_id')
    crop.modified_by = current_user.id
    crop.date_updated = datetime.utcnow()
    db.session.commit()
    flash('Crop updated successfully!', 'success')
    return redirect(url_for('crop.index'))

@crop_bp.route('/<int:id>/edit', methods=['GET'])
@login_required
@farmer_or_admin_required
def get_crop(id):
    crop = Crop.query.get_or_404(id)
    crop_data = {
        'name': crop.name,
        'weight': crop.weight,
        'category_id': crop.category_id
    }
    return jsonify(crop_data)

@crop_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@farmer_or_admin_required
def delete_crop(id):
    crop = Crop.query.get_or_404(id)
    db.session.delete(crop)
    db.session.commit()
    flash('Crop deleted successfully!', 'success')
    return redirect(url_for('crop.index'))
