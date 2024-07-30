from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    phonenumber = db.Column(db.String(20), nullable=True)
    user_type = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    id_start = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'


class District(db.Model):
    __tablename__ = 'district'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class FarmerGroup(db.Model):
    __tablename__ = 'farmergroup'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    
class ProduceCategory(db.Model):
    __tablename__ = 'producecategory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    crops = db.relationship('Crop', backref='category', lazy=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class SoilData(db.Model):
    __tablename__ = 'soildata'
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
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Crop(db.Model):
    __tablename__ = 'crop'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('producecategory.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Farm(db.Model):
    __tablename__ = 'farm'
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    subcounty = db.Column(db.String(255), nullable=False)
    farmergroup_id = db.Column(db.Integer, db.ForeignKey('farmergroup.id'), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=False)
    geolocation = db.Column(db.String(255), nullable=False)
    phonenumber = db.Column(db.String(20), nullable=True)
    phonenumber2 = db.Column(db.String(20), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    farmer_group = db.relationship('FarmerGroup', backref='farms')
    district = db.relationship('District', backref='farms')
    farm_data = db.relationship('FarmData', backref='farm', lazy=True)

class FarmData(db.Model):
    __tablename__ = 'farmdata'
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.String(50), db.ForeignKey('farm.farm_id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    land_type = db.Column(db.String(255), nullable=False)
    tilled_land_size = db.Column(db.Float, nullable=False)
    planting_date = db.Column(db.Date, nullable=False)
    season = db.Column(db.Integer, nullable=False)
    quality = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    harvest_date = db.Column(db.Date, nullable=False)
    expected_yield = db.Column(db.Float, nullable=False)
    actual_yield = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    channel_partner = db.Column(db.String(255), nullable=False)
    destination_country = db.Column(db.String(255), nullable=False)
    customer_name = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Forest(db.Model):
    __tablename__ = 'forest'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    tree_type = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Point(db.Model):
    __tablename__ = 'point'
    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    owner_type = db.Column(db.Enum('forest', 'farmer', 'tree'), nullable=False)
    forest_id = db.Column(db.Integer, db.ForeignKey('forest.id'), nullable=True)
    farmer_id = db.Column(db.String(50), db.ForeignKey('farm.farm_id'), nullable=True)
    tree_id = db.Column(db.Integer, db.ForeignKey('tree.id'), nullable=True)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=False)
    __table_args__ = (
        db.CheckConstraint(
            "(owner_type = 'forest' AND forest_id IS NOT NULL AND farmer_id IS NULL AND tree_id IS NULL) OR "
            "(owner_type = 'farmer' AND farmer_id IS NOT NULL AND forest_id IS NULL AND tree_id IS NULL) OR "
            "(owner_type = 'tree' AND tree_id IS NOT NULL AND forest_id IS NULL AND farmer_id IS NULL)",
            name='check_owner_type'
        ),
    )
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)




class Tree(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    forest_id = db.Column(db.Integer, db.ForeignKey('forest.id'), nullable=False)
    point_id = db.Column(db.Integer, db.ForeignKey('point.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    height = db.Column(db.Float, nullable=False)
    diameter = db.Column(db.Float, nullable=False)
    date_planted = db.Column(db.Date, nullable=False)
    date_cut = db.Column(db.Date, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_updated = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    type = db.Column(db.String(50), nullable=True)
