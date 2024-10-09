from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from app.routes.farm import farmer_or_admin_required
from app.utils import farmdata_utils
from app.models import Farm, Crop, FarmData

bp = Blueprint('farmdata', __name__)

@bp.route('/farmdata')
@login_required
@farmer_or_admin_required
def index():
    farm_id = request.args.get('farm_id')
    
    # Check if the user is an admin
    if current_user.is_admin:
        if farm_id:
            farmdata_list = FarmData.query.filter_by(farm_id=farm_id).all()
        else:
            farmdata_list = FarmData.query.all()
    else:
        if farm_id:
            farmdata_list = FarmData.query.filter_by(farm_id=farm_id, created_by=current_user.id).all()
        else:
            farmdata_list = FarmData.query.filter_by(created_by=current_user.id).all()
    
    return render_template('farmdata/index.html', farmdata_list=farmdata_list)


@bp.route('/farmdata/create', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def create_farmdata():
    if request.method == 'POST':
        data = {
            'farm_id': request.form['farm_id'],
            'crop_id': request.form['crop_id'],
            'land_type': request.form['land_type'],
            'tilled_land_size': request.form['tilled_land_size'],
            'planting_date': request.form['planting_date'],
            'season': request.form['season'],
            'quality': request.form['quality'],
            'quantity': request.form['quantity'],
            'harvest_date': request.form['harvest_date'],
            'expected_yield': request.form['expected_yield'],
            'actual_yield': request.form['actual_yield'],
            'timestamp': request.form['timestamp'],
            'channel_partner': request.form['channel_partner'],
            'destination_country': request.form['destination_country'],
            'customer_name': request.form['customer_name']
        }
        farm_id = request.form['farm_id']

        farmdata_utils.create_farmdata(data)
        flash('FarmData created successfully.', 'success')
        return redirect(url_for('farmdata.index', farm_id=farm_id))

    farms = Farm.query.all()
    crops = Crop.query.all()
    return render_template('farmdata/create.html', farms=farms, crops=crops)

@bp.route('/farmdata/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@farmer_or_admin_required
def edit_farmdata(id):
    farmdata = farmdata_utils.get_farmdata_by_id(id)
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        data = {
            'farm_id': request.form['farm_id'],
            'crop_id': request.form['crop_id'],
            'land_type': request.form['land_type'],
            'tilled_land_size': request.form['tilled_land_size'],
            'planting_date': request.form['planting_date'],
            'season': request.form['season'],
            'quality': request.form['quality'],
            'quantity': request.form['quantity'],
            'harvest_date': request.form['harvest_date'],
            'expected_yield': request.form['expected_yield'],
            'actual_yield': request.form['actual_yield'],
            'timestamp': request.form['timestamp'],
            'channel_partner': request.form['channel_partner'],
            'destination_country': request.form['destination_country'],
            'customer_name': request.form['customer_name']
        }

        farmdata_utils.update_farmdata(farmdata, data)
        flash('FarmData updated successfully.', 'success')
        return redirect(url_for('farmdata.index', farm_id=farm_id))

    farms = Farm.query.all()
    crops = Crop.query.all()
    return render_template('farmdata/edit.html', farmdata=farmdata, farms=farms, crops=crops)

@bp.route('/farmdata/<int:id>/delete', methods=['DELETE'])
@login_required
@farmer_or_admin_required
def delete_farmdata(id):
    farmdata = farmdata_utils.get_farmdata_by_id(id)
    farmdata_utils.delete_farmdata(farmdata)
    flash('FarmData deleted successfully.', 'success')
    return redirect(url_for('farmdata.index'))
