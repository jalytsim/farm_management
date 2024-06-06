from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(255), nullable=False)
    soils = db.relationship('SoilData', backref='district', lazy=True)
    points = db.relationship('Point', backref='district', lazy=True)
    farms = db.relationship('Farm', backref='district', lazy=True)

class FarmerGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    farms = db.relationship('Farm', backref='farmergroup', lazy=True)

class ProduceCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    crops = db.relationship('Crop', backref='category', lazy=True)

class SoilData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=False)
    internal_id = db.Column(db.Integer, nullable=False)
    device = db.Column(db.String(255), nullable=False)
    owner = db.Column(db.String(255), nullable=False)
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    conductivity = db.Column(db.Float, nullable=False)
    signal_level = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('produce_category.id'), nullable=False)
    farm_data = db.relationship('FarmData', backref='crop', lazy=True)

class Farm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    subcounty = db.Column(db.String(255), nullable=False)
    farmergroup_id = db.Column(db.Integer, db.ForeignKey('farmer_group.id'), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=False)
    geolocation = db.Column(db.String(255), nullable=False)
    farm_data = db.relationship('FarmData', backref='farm', lazy=True)
    points = db.relationship('Point', backref='farm', lazy=True)

class FarmData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    tilled_land_size = db.Column(db.Float, nullable=False)
    planting_date = db.Column(db.Date, nullable=False)
    season = db.Column(db.Integer, nullable=False)
    quality = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    harvest_date = db.Column(db.Date, nullable=False)
    expected_yield = db.Column(db.Float, nullable=False)
    actual_yield = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    channel_partner = db.Column(db.String(255), nullable=False)
    destination_country = db.Column(db.String(255), nullable=False)
    customer_name = db.Column(db.String(255), nullable=False)

class Forest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    points = db.relationship('Point', backref='forest', lazy=True)

class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    owner_type = db.Column(db.Enum('forest', 'farmer'), nullable=False)
    forest_id = db.Column(db.Integer, db.ForeignKey('forest.id'), nullable=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=True)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=False)
    __table_args__ = (
        db.CheckConstraint(
            "(owner_type = 'forest' AND forest_id IS NOT NULL AND farmer_id IS NULL) OR "
            "(owner_type = 'farmer' AND farmer_id IS NOT NULL AND forest_id IS NULL)",
            name='check_owner_type'
        ),
    )
