# app/utils/crop_utils.py
from datetime import datetime
from flask_login import current_user
from app import db
from app.models import Crop


def create_crop(name, weight, category_id):
    new_crop = Crop(
        name=name,
        weight=weight,
        category_id=category_id,
        created_by=current_user.id,  # Set creator
        modified_by=current_user.id,  # Set modifier
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )
    db.session.add(new_crop)
    db.session.commit()
    return new_crop


def update_crop(crop_id, name, weight, category_id):
    crop = Crop.query.get(crop_id)
    if not crop:
        raise ValueError(f"Crop ID {crop_id} does not exist.")

    crop.name = name
    crop.weight = weight
    crop.category_id = category_id
    crop.modified_by = current_user.id  # Set modifier
    crop.date_updated = datetime.utcnow()
    db.session.commit()
    return crop


def delete_crop(crop_id):
    crop = Crop.query.get(crop_id)
    if crop:
        db.session.delete(crop)
        db.session.commit()
    else:
        raise ValueError(f"Crop ID {crop_id} does not exist.")
