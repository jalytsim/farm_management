# app/utils/crop_utils.py
from app import db
from app.models import Crop

def create_crop(name, weight, category_id):
    new_crop = Crop(name=name, weight=weight, category_id=category_id)
    db.session.add(new_crop)
    db.session.commit()
    return new_crop

def update_crop(crop, name, weight, category_id):
    crop.name = name
    crop.weight = weight
    crop.category_id = category_id
    db.session.commit()
    return crop

def delete_crop(crop):
    db.session.delete(crop)
    db.session.commit()
