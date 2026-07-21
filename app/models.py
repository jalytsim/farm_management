from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT
from flask_login import UserMixin
from datetime import datetime
from base64 import b64encode, b64decode
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(150), unique=True, nullable=False)
    email           = db.Column(db.String(150), unique=True, nullable=False)
    password        = db.Column(db.String(150), nullable=False)
    phonenumber     = db.Column(db.String(20), nullable=True)
    company_name    = db.Column(db.String(255), nullable=True)
    user_type       = db.Column(db.String(50), nullable=False)
    is_admin        = db.Column(db.Boolean, default=False)
    has_access_wbii = db.Column(db.Boolean, default=False)
    permissions     = db.Column(db.JSON, default=dict)           # ✅ permissions modulaires
    date_created    = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    id_start        = db.Column(db.String(10), nullable=True)

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
    cin = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    # ★ NOUVEAU — pays de la ferme (Option B)
    country = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    farm_data = db.relationship('FarmData', backref='farm', lazy=True)
    farm_report = db.relationship('FarmReport', backref='farm', uselist=False, lazy=True)

    def __repr__(self):
        return f"<Farm(id={self.id}, farm_id={self.farm_id})>"


class FarmReport(db.Model):
    __tablename__ = 'farmreport'
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)
    project_area = db.Column(db.String(255), nullable=True)
    country_deforestation_risk_level = db.Column(db.String(255), nullable=True)
    radd_alert = db.Column(db.String(255), nullable=True)
    tree_cover_loss = db.Column(db.String(255), nullable=True)
    forest_cover_2020 = db.Column(db.String(255), nullable=True)
    eudr_compliance_assessment = db.Column(db.String(255), nullable=True)
    protected_area_status = db.Column(db.String(255), nullable=True)
    cover_extent_summary_b64 = db.Column(LONGTEXT, nullable=True)
    tree_cover_drivers = db.Column(db.String(255), nullable=True)
    cover_extent_area = db.Column(db.String(255), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_cover_extent_summary(self, summary_text: str):
        if summary_text:
            self.cover_extent_summary_b64 = b64encode(summary_text.encode('utf-8')).decode('utf-8')

    def get_cover_extent_summary(self) -> str:
        if self.cover_extent_summary_b64:
            return b64decode(self.cover_extent_summary_b64.encode('utf-8')).decode('utf-8')
        return None


class ForestReport(db.Model):
    __tablename__ = 'forestreport'
    id = db.Column(db.Integer, primary_key=True)
    forest_id = db.Column(db.Integer, db.ForeignKey('forest.id'), nullable=False)
    project_area = db.Column(db.String(255), nullable=True)
    country_deforestation_risk_level = db.Column(db.String(255), nullable=True)
    radd_alert = db.Column(db.String(255), nullable=True)
    tree_cover_loss = db.Column(db.String(255), nullable=True)
    forest_cover_2020 = db.Column(db.String(255), nullable=True)
    eudr_compliance_assessment = db.Column(db.String(255), nullable=True)
    protected_area_status = db.Column(db.String(255), nullable=True)
    cover_extent_summary_b64 = db.Column(LONGTEXT, nullable=True)
    tree_cover_drivers = db.Column(db.String(255), nullable=True)
    cover_extent_area = db.Column(db.String(255), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    forest = db.relationship('Forest', backref=db.backref('forest_reports', lazy=True))

    def set_cover_extent_summary(self, summary_text: str):
        if summary_text:
            self.cover_extent_summary_b64 = b64encode(summary_text.encode('utf-8')).decode('utf-8')

    def get_cover_extent_summary(self) -> str:
        if self.cover_extent_summary_b64:
            return b64decode(self.cover_extent_summary_b64.encode('utf-8')).decode('utf-8')
        return None

    def __repr__(self):
        return f'<ForestReport {self.id} - Forest {self.forest_id}>'


class FarmData(db.Model):
    __tablename__ = 'farmdata'
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.String(50), db.ForeignKey('farm.farm_id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    land_type = db.Column(db.String(255), nullable=True)
    tilled_land_size = db.Column(db.Float, nullable=True)
    planting_date = db.Column(db.Date, nullable=True)
    season = db.Column(db.Integer, nullable=True)
    quality = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    harvest_date = db.Column(db.Date, nullable=True)
    expected_yield = db.Column(db.Float, nullable=True)
    actual_yield = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    channel_partner = db.Column(db.String(255), nullable=True)
    destination_country = db.Column(db.String(255), nullable=True)
    customer_name = db.Column(db.String(255), nullable=True)
    number_of_tree = db.Column(db.Integer, nullable=True)
    hs_code = db.Column(db.String(10), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class Forest(db.Model):
    __tablename__ = 'forest'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    tree_type = db.Column(db.String(255), nullable=False)
    # ★ NOUVEAU — pays de la forêt (Option B)
    country = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class Point(db.Model):
    __tablename__ = 'point'
    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.Numeric(12, 8), nullable=False)
    latitude = db.Column(db.Numeric(12, 8), nullable=False)
    owner_type = db.Column(db.Enum('forest', 'farmer', 'tree'), nullable=False)
    owner_id = db.Column(db.String(100), nullable=True)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return (f"<Point(id={self.id}, longitude={self.longitude}, "
                f"latitude={self.latitude}, owner_type={self.owner_type}, "
                f"owner_id={self.owner_id})>")


class Tree(db.Model):
    __tablename__ = 'tree'
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
    date_updated = db.Column(db.DateTime, default=db.func.current_timestamp(),
                             onupdate=db.func.current_timestamp())
    type = db.Column(db.String(50), nullable=True)


class Weather(db.Model):
    __tablename__ = 'weather'
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
    date_updated = db.Column(db.DateTime, default=db.func.current_timestamp(),
                             onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Weather {self.id}>'


class Solar(db.Model):
    __tablename__ = 'solar'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    uv_index = db.Column(db.Float, nullable=True)
    downward_short_wave_radiation_flux = db.Column(db.Float, nullable=True)
    source = db.Column(db.String(100), nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_updated = db.Column(db.DateTime, default=db.func.current_timestamp(),
                             onupdate=db.func.current_timestamp())

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
    grades = db.relationship('Grade', backref='crop', lazy=True)
    kc_values = db.relationship('CropCoefficient', backref='crop', lazy=True)
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
    grade_value = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"<Grade(crop_id={self.crop_id}, grade_value={self.grade_value})>"


class CropCoefficient(db.Model):
    __tablename__ = 'cropcoefficient'
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    stage = db.Column(db.String(50), nullable=False)
    kc_value = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"<CropCoefficient(stage={self.stage}, kc_value={self.kc_value})>"


class Irrigation(db.Model):
    __tablename__ = 'irrigation'
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)
    irrigation_date = db.Column(db.Date, nullable=False)
    water_applied = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class Pays(db.Model):
    __tablename__ = 'pays'
    id = db.Column(db.SmallInteger, primary_key=True)
    code = db.Column(db.Integer, nullable=False, unique=True)
    alpha2 = db.Column(db.String(2), nullable=False, unique=True)
    alpha3 = db.Column(db.String(3), nullable=False, unique=True)
    nom_en_gb = db.Column(db.String(45), nullable=False)
    nom_fr_fr = db.Column(db.String(45), nullable=False)

    def __repr__(self):
        return (f"<Pays(id={self.id}, code={self.code}, "
                f"alpha2={self.alpha2}, alpha3={self.alpha3})>")


class Store(db.Model):
    __tablename__ = 'store'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    district = db.Column(db.String(255), nullable=False)
    store_type = db.Column(db.String(50), nullable=False, default="agricultural")
    status = db.Column(db.Boolean, default=True)
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=True)
    inventory_count = db.Column(db.Integer, default=0)
    sales_count = db.Column(db.Integer, default=0)
    revenue = db.Column(db.Float, default=0.0)
    last_stock_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"<Store {self.name}, {self.district}, {self.country}>"


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)

    def __repr__(self):
        return f"<Product {self.name} - Store {self.store_id}>"


class PaidFeatureAccess(db.Model):
    __tablename__ = 'paidfeatureaccess'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    guest_phone_number = db.Column(db.String(20), nullable=True)
    feature_name = db.Column(db.String(100), nullable=False)
    txn_id = db.Column(db.String(100), nullable=False, unique=True)
    payment_status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    access_expires_at = db.Column(db.DateTime, nullable=True)
    usage_left = db.Column(db.Integer, nullable=True)
    payment_method = db.Column(db.String(50), default='mobile_money')
    dpo_trans_token = db.Column(db.String(100), nullable=True, unique=True)
    dpo_trans_ref = db.Column(db.String(100), nullable=True)
    currency = db.Column(db.String(10), default='UGX')
    amount = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<PaidFeatureAccess {self.feature_name} - {self.payment_status}>'


class FeaturePrice(db.Model):
    __tablename__ = 'featureprice'
    id = db.Column(db.Integer, primary_key=True)
    feature_name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=True)
    usage_limit = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<FeaturePrice {self.feature_name} - {self.price}>'


class EUDRStatement(db.Model):
    __tablename__ = 'eudr_statements'
    id = db.Column(db.Integer, primary_key=True)
    internal_reference_number = db.Column(db.String(255), nullable=False)
    dds_identifier = db.Column(db.String(255), unique=True, nullable=True)
    activity_type = db.Column(db.String(50), nullable=True)
    border_cross_country = db.Column(db.String(10), nullable=True)
    country_of_activity = db.Column(db.String(100), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    geo_location_confidential = db.Column(db.Boolean, default=False)
    operator_identifier_type = db.Column(db.String(100), nullable=True)
    operator_identifier_value = db.Column(db.String(255), nullable=True)
    operator_name = db.Column(db.String(255), nullable=True)
    operator_country = db.Column(db.String(100), nullable=True)
    operator_address = db.Column(db.String(255), nullable=True)
    operator_email = db.Column(db.String(255), nullable=True)
    operator_phone = db.Column(db.String(50), nullable=True)
    description_of_goods = db.Column(db.String(255), nullable=True)
    hs_heading = db.Column(db.String(50), nullable=True)
    scientific_name = db.Column(db.String(255), nullable=True)
    common_name = db.Column(db.String(255), nullable=True)
    volume = db.Column(db.Float, nullable=True)
    net_weight = db.Column(db.Float, nullable=True)
    supplementary_unit = db.Column(db.String(50), nullable=True)
    supplementary_unit_qualifier = db.Column(db.String(50), nullable=True)
    producers_json = db.Column(db.Text, nullable=True)
    last_response_code = db.Column(db.Integer, nullable=True)
    last_response_text = db.Column(db.Text, nullable=True)
    reference_number = db.Column(db.String(255), nullable=True)
    verification_code = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(100), nullable=True)
    status_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QRCode(db.Model):
    __tablename__ = 'qrcode'
    id = db.Column(db.Integer, primary_key=True)
    hash_md5 = db.Column(db.String(32), unique=True, nullable=False)
    data_base64 = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    qr_type = db.Column(db.String(50), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<QRCode(id={self.id}, hash={self.hash_md5}, user={self.created_by})>"


class Certificate(db.Model):
    __tablename__ = 'certificate'
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    certificate_type = db.Column(db.String(50), nullable=False)
    total_farms = db.Column(db.Integer, nullable=False)
    compliant_100_count = db.Column(db.Integer, default=0)
    likely_compliant_count = db.Column(db.Integer, default=0)
    not_compliant_count = db.Column(db.Integer, default=0)
    compliant_100_percent = db.Column(db.Float, default=0.0)
    likely_compliant_percent = db.Column(db.Float, default=0.0)
    not_compliant_percent = db.Column(db.Float, default=0.0)
    overall_compliance_rate = db.Column(db.Float, default=0.0)
    title = db.Column(db.String(255), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    pdf_data_base64 = db.Column(db.Text, nullable=True)
    qr_code_data = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='active')
    download_count = db.Column(db.Integer, default=0)
    last_downloaded = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], backref='certificates')

    def __repr__(self):
        return (f"<Certificate(id={self.certificate_id}, "
                f"user_id={self.user_id}, type={self.certificate_type})>")

    def to_dict(self):
        return {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'user_id': self.user_id,
            'certificate_type': self.certificate_type,
            'total_farms': self.total_farms,
            'compliance_status': {
                'compliant_100':    self.compliant_100_count,
                'likely_compliant': self.likely_compliant_count,
                'not_compliant':    self.not_compliant_count,
            },
            'compliance_percentages': {
                'compliant_100_percent':    self.compliant_100_percent,
                'likely_compliant_percent': self.likely_compliant_percent,
                'not_compliant_percent':    self.not_compliant_percent,
                'overall_rate':             self.overall_compliance_rate,
            },
            'title':          self.title,
            'issue_date':     self.issue_date.isoformat() if self.issue_date else None,
            'valid_until':    self.valid_until.isoformat() if self.valid_until else None,
            'status':         self.status,
            'download_count': self.download_count,
        }


class BlogPost(db.Model):
    __tablename__ = 'blogpost'
    id          = db.Column(db.Integer, primary_key=True)
    slug        = db.Column(db.String(200), unique=True, nullable=False)
    title       = db.Column(db.String(255), nullable=False)
    excerpt     = db.Column(db.Text, nullable=False)
    author      = db.Column(db.String(100), nullable=False)
    category    = db.Column(db.String(50), nullable=False)
    tags        = db.Column(db.JSON, default=list)
    read_time   = db.Column(db.String(20), nullable=True)
    cover_image = db.Column(db.String(500), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def to_dict(self):
        return {
            'id':          self.id,
            'slug':        self.slug,
            'title':       self.title,
            'excerpt':     self.excerpt,
            'author':      self.author,
            'category':    self.category,
            'tags':        self.tags or [],
            'read_time':   self.read_time,
            'cover_image': self.cover_image,
            'created_at':  self.created_at.isoformat(),
        }


class GFWLog(db.Model):
    __tablename__ = 'gfwlog'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    guest_phone = db.Column(db.String(20), nullable=True)
    action_type = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(20), nullable=True)
    entity_id   = db.Column(db.String(100), nullable=True)
    ip_address  = db.Column(db.String(50), nullable=True)
    user_agent  = db.Column(db.String(255), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


class SMSLog(db.Model):
    __tablename__ = 'smslog'
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    phone     = db.Column(db.String(20), nullable=False)
    message   = db.Column(db.Text, nullable=True)
    status    = db.Column(db.String(20), nullable=False, default='pending')
    http_code = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SentinelCache(db.Model):
    __tablename__ = 'sentinelcache'
    id            = db.Column(db.Integer, primary_key=True)
    farm_id       = db.Column(db.String(50), nullable=False, unique=True, index=True)
    history_json  = db.Column(LONGTEXT, nullable=True)
    forecast_json = db.Column(LONGTEXT, nullable=True)
    ltv_json      = db.Column(db.Text, nullable=True)
    period_from   = db.Column(db.String(20), nullable=True)
    period_to     = db.Column(db.String(20), nullable=True)
    stale_after   = db.Column(db.DateTime, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_stale(self):
        if not self.stale_after:
            return True
        return datetime.utcnow() > self.stale_after

    def get_history(self):
        import json
        return json.loads(self.history_json) if self.history_json else []

    def get_forecast(self):
        import json
        return json.loads(self.forecast_json) if self.forecast_json else {}

    def get_ltv(self):
        import json
        return json.loads(self.ltv_json) if self.ltv_json else None

    def __repr__(self):
        return f'<SentinelCache farm={self.farm_id} stale={self.is_stale()}>'
class ProductCategory(db.Model):
    __tablename__ = 'productcategory'
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False, unique=True)
    slug         = db.Column(db.String(100), unique=True, nullable=False)
    description  = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    created_by   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'slug': self.slug, 'description': self.description}


class EcoProduct(db.Model):
    __tablename__ = 'ecoproduct'
    id                     = db.Column(db.Integer, primary_key=True)
    name                   = db.Column(db.String(255), nullable=False)
    slug                   = db.Column(db.String(191), unique=True, nullable=False)
    description            = db.Column(db.Text, nullable=True)
    category_id            = db.Column(db.Integer, db.ForeignKey('productcategory.id'), nullable=False)

    price                  = db.Column(db.Float, nullable=False)
    compare_at_price       = db.Column(db.Float, nullable=True)
    currency               = db.Column(db.String(10), default='USD')
    unit                   = db.Column(db.String(20), default='kg')
    stock                  = db.Column(db.Integer, default=0)
    sku                    = db.Column(db.String(100), unique=True, nullable=True)

    origin_country         = db.Column(db.String(100), nullable=True)
    is_deforestation_free  = db.Column(db.Boolean, default=False)
    certification_labels   = db.Column(db.JSON, default=list)

    origin_story  = db.Column(db.Text, nullable=True)
    farmer_name   = db.Column(db.String(150), nullable=True)
    harvest_year  = db.Column(db.Integer, nullable=True)

    is_active              = db.Column(db.Boolean, default=True)
    is_featured            = db.Column(db.Boolean, default=False)
    date_created           = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by             = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    category = db.relationship('ProductCategory', backref='products')
    images   = db.relationship('EcoProductImage', backref='product', lazy=True,
                                cascade='all, delete-orphan', order_by='EcoProductImage.position')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'slug': self.slug,
            'description': self.description,
            'category_id': self.category_id,
            'category': self.category.name if self.category else None,
            'price': self.price, 'compare_at_price': self.compare_at_price,
            'currency': self.currency, 'unit': self.unit, 'stock': self.stock,
            'sku': self.sku,
            'origin_country': self.origin_country,
            'is_deforestation_free': self.is_deforestation_free,
            'certification_labels': self.certification_labels or [],
            'images': [img.url for img in self.images],
            'origin_story': self.origin_story,
            'farmer_name': self.farmer_name,
            'harvest_year': self.harvest_year,      
            'is_active': self.is_active,
            'is_featured': self.is_featured,
        }


class EcoProductImage(db.Model):
    __tablename__ = 'ecoproductimage'
    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('ecoproduct.id'), nullable=False)
    url        = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    position   = db.Column(db.Integer, default=0)


class EcoOrder(db.Model):
    __tablename__ = 'ecoorder'
    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    guest_email       = db.Column(db.String(255), nullable=True)
    guest_name        = db.Column(db.String(255), nullable=True)
    guest_phone       = db.Column(db.String(20), nullable=True)
    shipping_address  = db.Column(db.Text, nullable=True)
    total_amount      = db.Column(db.Float, nullable=False)
    currency          = db.Column(db.String(10), default='UGX')
    status            = db.Column(db.String(50), default='pending')  # pending, paid, shipped, cancelled
    payment_method    = db.Column(db.String(50), default='dpo')
    dpo_trans_token   = db.Column(db.String(100), nullable=True, unique=True)   # ★ AJOUT
    dpo_trans_ref     = db.Column(db.String(100), nullable=True)                # ★ AJOUT
    date_created      = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('EcoOrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'status': self.status, 'total_amount': self.total_amount,
            'currency': self.currency, 'payment_method': self.payment_method,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'items': [i.to_dict() for i in self.items],
        }

class EcoOrderItem(db.Model):
    __tablename__ = 'ecoorderitem'
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('ecoorder.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('ecoproduct.id'), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id, 'product_id': self.product_id,
            'quantity': self.quantity, 'unit_price': self.unit_price,
        }