import pandas as pd
import os
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import District, Farm, Forest, Point
from app.routes.admin import admin_required
from app.routes.farm import farmer_or_admin_required
from app import db
from app.utils.point_utils import create_point, delete_point, get_all_points, get_point_by_id, update_point
from werkzeug.utils import secure_filename
from app import Config 

bp = Blueprint('points', __name__)

@bp.route('/points', methods=['GET'])
@login_required
def list_points():
    page = request.args.get('page', 1, type=int)
    
    # Check if the user is an admin
    if current_user.is_admin:
        points = Point.query.paginate(page=page, per_page=6)
    else:
        points = Point.query.filter_by(created_by=current_user.id).paginate(page=page, per_page=6)
    
    return render_template('points/list.html', points=points)

@bp.route('/points/<int:point_id>', methods=['GET'])
@login_required
def view_point(point_id):
    point = get_point_by_id(point_id)
    if not point:
        flash('Point not found.', 'error')
        return redirect(url_for('points.list_points'))
    return render_template('points/view.html', point=point)

@bp.route('/points/create', methods=['GET', 'POST'])
@login_required
def create_point_route():
    if request.method == 'POST':
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        owner_type = request.form.get('owner_type')
        forest_id = request.form.get('forest_id')
        farmer_id = request.form.get('farmer_id')
        district_id = request.form.get('district_id')
        print(district_id)

        # Validate required fields
        if not longitude or not latitude or not owner_type:
            flash('Longitude, latitude, and owner type are required.', 'error')
            return render_template('points/create.html')

        # Validate and process forest_id and farmer_id based on owner_type
        if owner_type == 'forest':
            if forest_id:
                forest_id = int(forest_id)
                forest = Forest.query.get(forest_id)
                if not forest:
                    flash('Invalid Forest ID.', 'error')
                    return render_template('points/create.html')
            else:
                forest_id = None
            farmer_id = None
        elif owner_type == 'farmer':
            farmer_id = int(farmer_id) if farmer_id else None
            forest_id = None
        else:
            flash('Invalid owner type.', 'error')
            return render_template('points/create.html')

        try:
            create_point(longitude, latitude, owner_type, district_id, forest_id, farmer_id)
            flash('Point created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating point: {e}', 'error')

        return redirect(url_for('points.list_points'))
    
    districts = District.query.all()
    forests = Forest.query.all()
    farms = Farm.query.all()
    return render_template('points/create.html', districts=districts, forests=forests, farms=farms)

@bp.route('/points/edit/<int:point_id>', methods=['GET', 'POST'])
@login_required
def edit_point_route(point_id):
    point = get_point_by_id(point_id)
    if not point:
        flash('Point not found.', 'error')
        return redirect(url_for('points.list_points'))

    if request.method == 'POST':
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        owner_type = request.form.get('owner_type')
        forest_id = request.form.get('forest_id')
        farmer_id = request.form.get('farmer_id')
        district_id = request.form.get('district_id')

        # Validate required fields
        if not longitude or not latitude or not owner_type:
            flash('Longitude, latitude, and owner type are required.', 'error')
            return render_template('points/edit.html', point=point)

        # Validate and process forest_id and farmer_id based on owner_type
        if owner_type == 'forest':
            if forest_id:
                forest_id = int(forest_id)
                forest = Forest.query.get(forest_id)
                if not forest:
                    flash('Invalid Forest ID.', 'error')
                    return render_template('points/edit.html', point=point)
            else:
                forest_id = None
            farmer_id = None
        elif owner_type == 'farmer':
            farmer_id = int(farmer_id) if farmer_id else None
            forest_id = None
        else:
            flash('Invalid owner type.', 'error')
            return render_template('points/edit.html', point=point)

        try:
            update_point(point_id, longitude, latitude, owner_type, district_id, forest_id, farmer_id, )
            flash('Point updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating point: {e}', 'error')

        return redirect(url_for('points.list_points'))

    districts = District.query.all()
    forests = Forest.query.all()
    farms = Farm.query.all()
    return render_template('points/edit.html', point=point, districts=districts, forests=forests, farms=farms)

@bp.route('/points/delete/<int:point_id>', methods=['POST'])
@login_required
def delete_point_route(point_id):
    try:
        delete_point(point_id)
        flash('Point deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting point: {e}', 'error')
    
    return redirect(url_for('points.list_points'))

def validate_csv_columns(file_path, required_columns):
    data = pd.read_csv(file_path)
    missing_columns = [col for col in required_columns if col not in data.columns]
    return missing_columns

@bp.route('/points/upload', methods=['GET', 'POST'])
@login_required
def upload_points_route():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.csv'):
            # Ensure the uploads directory exists
            upload_folder = Config.UPLOAD_FOLDER
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            # Validate the CSV columns
            required_columns = ['longitude', 'latitude', 'owner_type', 'forest_id', 'farmer_id', 'district_id']
            missing_columns = validate_csv_columns(file_path, required_columns)

            if missing_columns:
                flash(f'Missing required columns: {", ".join(missing_columns)}', 'error')
                return render_template('points/upload.html')

            # Read and process the CSV data
            data = pd.read_csv(file_path)
            for index, row in data.iterrows():
                try:
                    point = Point(
                        longitude=row['longitude'],
                        latitude=row['latitude'],
                        owner_type=row['owner_type'],
                        forest_id=row['forest_id'] if not pd.isna(row['forest_id']) else None,
                        farmer_id=row['farmer_id'] if not pd.isna(row['farmer_id']) else None,
                        district_id=row['district_id']
                    )
                    db.session.add(point)
                except Exception as e:
                    flash(f'Error processing row {index}: {e}', 'error')
            try:
                db.session.commit()
                flash('Points uploaded and created successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error uploading points: {e}', 'error')
        else:
            flash('Invalid file format. Please upload a CSV file.', 'error')
    
    return render_template('points/upload.html')
