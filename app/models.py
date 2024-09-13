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
    farm_data = db.relationship('FarmData', backref='farm', lazy=True)

    def __repr__(self):
        return f"<Farm(id={self.id}, farm_id={self.farm_id})>"

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
    owner_id = db.Column(db.String, nullable=True)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"<Point(id={self.id}, longitude={self.longitude}, latitude={self.latitude}, owner_type={self.owner_type}, owner_id={self.owner_id})>"



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



class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    air_temperature = db.Column(db.Float, nullable=True)
    air_temperature_80m = db.Column(db.Float, nullable=True)
    air_temperature_100m = db.Column(db.Float, nullable=True)
    air_temperature_1000hpa = db.Column(db.Float, nullable=True)
    air_temperature_800hpa = db.Column(db.Float, nullable=True)
    air_temperature_500hpa = db.Column(db.Float, nullable=True)
    air_temperature_200hpa = db.Column(db.Float, nullable=True)
    pressure = db.Column(db.Float, nullable=True)
    cloud_cover = db.Column(db.Float, nullable=True)
    current_direction = db.Column(db.Float, nullable=True)
    current_speed = db.Column(db.Float, nullable=True)
    gust = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    ice_cover = db.Column(db.Float, nullable=True)
    precipitation = db.Column(db.Float, nullable=True)
    snow_depth = db.Column(db.Float, nullable=True)
    sea_level = db.Column(db.Float, nullable=True)
    swell_direction = db.Column(db.Float, nullable=True)
    swell_height = db.Column(db.Float, nullable=True)
    swell_period = db.Column(db.Float, nullable=True)
    secondary_swell_direction = db.Column(db.Float, nullable=True)
    secondary_swell_height = db.Column(db.Float, nullable=True)
    secondary_swell_period = db.Column(db.Float, nullable=True)
    visibility = db.Column(db.Float, nullable=True)
    water_temperature = db.Column(db.Float, nullable=True)
    wave_direction = db.Column(db.Float, nullable=True)
    wave_height = db.Column(db.Float, nullable=True)
    wave_period = db.Column(db.Float, nullable=True)
    wind_wave_direction = db.Column(db.Float, nullable=True)
    wind_wave_height = db.Column(db.Float, nullable=True)
    wind_wave_period = db.Column(db.Float, nullable=True)
    wind_direction = db.Column(db.Float, nullable=True)
    wind_direction_20m = db.Column(db.Float, nullable=True)
    wind_direction_30m = db.Column(db.Float, nullable=True)
    wind_direction_40m = db.Column(db.Float, nullable=True)
    wind_direction_50m = db.Column(db.Float, nullable=True)
    wind_direction_80m = db.Column(db.Float, nullable=True)
    wind_direction_100m = db.Column(db.Float, nullable=True)
    wind_direction_1000hpa = db.Column(db.Float, nullable=True)
    wind_direction_800hpa = db.Column(db.Float, nullable=True)
    wind_direction_500hpa = db.Column(db.Float, nullable=True)
    wind_direction_200hpa = db.Column(db.Float, nullable=True)
    wind_speed = db.Column(db.Float, nullable=True)
    wind_speed_20m = db.Column(db.Float, nullable=True)
    wind_speed_30m = db.Column(db.Float, nullable=True)
    wind_speed_40m = db.Column(db.Float, nullable=True)
    wind_speed_50m = db.Column(db.Float, nullable=True)
    wind_speed_80m = db.Column(db.Float, nullable=True)
    wind_speed_100m = db.Column(db.Float, nullable=True)
    wind_speed_1000hpa = db.Column(db.Float, nullable=True)
    wind_speed_800hpa = db.Column(db.Float, nullable=True)
    wind_speed_500hpa = db.Column(db.Float, nullable=True)
    wind_speed_200hpa = db.Column(db.Float, nullable=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_updated = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Weather {self.id}>'


class Solar(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)  # Timestamp in UTC
    uv_index = db.Column(db.Float, nullable=True)  # Ultraviolet radiation (W/m²)
    downward_short_wave_radiation_flux = db.Column(db.Float, nullable=True)  # Downward short-wave radiation flux (W/m²)
    source = db.Column(db.String(100), nullable=True)  # Source of data, e.g., 'noaa' or 'mercator'
    start_time = db.Column(db.DateTime, nullable=True)  # Start timestamp for forecast (if needed)
    end_time = db.Column(db.DateTime, nullable=True)  # End timestamp for forecast (if needed)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_updated = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Solar {self.id}>'

class ProduceCategory(db.Model):
    __tablename__ = 'producecategory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    crops = db.relationship('Crop', backref='category', lazy=True)
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
    grades = db.relationship('Grade', backref='crop', lazy=True)  # Relation avec les grades
    kc_values = db.relationship('CropCoefficient', backref='crop', lazy=True)  # Relation avec Kc
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"<Crop(id={self.id}, name={self.name})>"
    
class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    grade_value = db.Column(db.String(50), nullable=False)  # Grade, ex : A, B, C
    description = db.Column(db.Text, nullable=True)  # Description facultative
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"<Grade(crop_id={self.crop_id}, grade_value={self.grade_value})>"


# Modèle pour les coefficients Kc des cultures
class CropCoefficient(db.Model):
    __tablename__ = 'cropcoefficient'
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    stage = db.Column(db.String(50), nullable=False)  # Stage de croissance ex : initial, mid-season, late-season
    kc_value = db.Column(db.Float, nullable=False)  # Valeur Kc pour ce stage
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"<CropCoefficient(stage={self.stage}, kc_value={self.kc_value})>"


# Modèle pour les données d'irrigation
class Irrigation(db.Model):
    __tablename__ = 'irrigation'
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)
    irrigation_date = db.Column(db.Date, nullable=False)
    water_applied = db.Column(db.Float, nullable=False)  # Quantité d'eau en mm
    method = db.Column(db.String(100), nullable=False)  # Méthode d'irrigation ex: drip, sprinkler
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)