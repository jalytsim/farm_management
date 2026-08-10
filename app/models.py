from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT
from flask_login import UserMixin
from datetime import datetime
from base64 import b64encode, b64decode
from app import db
from decimal import Decimal
from datetime import timedelta


# ── Helpers partagés ─────────────────────────────────────────────────────────

def _f(value):
    """Numeric -> float pour la sérialisation JSON."""
    return float(value) if value is not None else None


ZERO = Decimal('0')

# Modes de vente
#   'unit'   : article compté à la pièce (sachet 250 g)     -> unit='bag'
#   'weight' : vrac vendu au poids avec minimum et pas      -> unit='kg'
#   'lot'    : un lot indivisible, tout ou rien             -> unit='kg'
SALE_MODES = ('unit', 'weight', 'lot')

# Modes d'accès à une vente aux enchères
#   'open'     : tout compte connecté peut enchérir
#   'deposit'  : caution remboursable à payer d'abord
#   'approval' : validation manuelle par un admin
ACCESS_MODES = ('open', 'deposit', 'approval')
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
    # ★ CORRIGÉ — unique + index : indispensable, deux FK pointent dessus
    #   (FarmData.farm_id et EcoProduct.farm_id)
    farm_id = db.Column(db.String(50), nullable=False, unique=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    subcounty = db.Column(db.String(255), nullable=False)
    farmergroup_id = db.Column(db.Integer, db.ForeignKey('farmergroup.id'), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=False)
    geolocation = db.Column(db.String(255), nullable=False)   # centroïde "lat, lon"
    phonenumber = db.Column(db.String(20), nullable=True)
    phonenumber2 = db.Column(db.String(20), nullable=True)
    cin = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    government_id = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    farm_data = db.relationship('FarmData', backref='farm', lazy=True)
    farm_report = db.relationship('FarmReport', backref='farm', uselist=False, lazy=True)

    def __repr__(self):
        return f"<Farm(id={self.id}, farm_id={self.farm_id})>"

    def to_dict(self):
        """Expose les DEUX identifiants — le front a besoin de farm_id."""
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'name': self.name,
            'subcounty': self.subcounty,
            'country': self.country,
            'district_id': self.district_id,
            'farmergroup_id': self.farmergroup_id,
            'geolocation': self.geolocation,
            'gender': self.gender,
            'cin': self.cin,
            'government_id': self.government_id,
            'phonenumber': self.phonenumber,
            'phonenumber2': self.phonenumber2,
        }


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

    @property
    def data_dict(self):
        """Décode data_base64 -> dict JSON. Retourne {} si absent/invalide."""
        import json
        if not self.data_base64:
            return {}
        try:
            return json.loads(b64decode(self.data_base64.encode('utf-8')).decode('utf-8'))
        except Exception:
            return {}

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


class GuestSentinelCache(db.Model):
    __tablename__ = 'guestsentinelcache'
    id                  = db.Column(db.Integer, primary_key=True)
    guest_phone_number  = db.Column(db.String(20), nullable=False, index=True)
    polygon_hash        = db.Column(db.String(32), nullable=False, index=True)
    history_json        = db.Column(LONGTEXT, nullable=True)
    forecast_json       = db.Column(LONGTEXT, nullable=True)
    ltv_json            = db.Column(db.Text, nullable=True)
    period_from         = db.Column(db.String(20), nullable=True)
    period_to           = db.Column(db.String(20), nullable=True)
    stale_after         = db.Column(db.DateTime, nullable=True)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('guest_phone_number', 'polygon_hash', name='uq_guest_phone_polygon'),
    )

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
        return f'<GuestSentinelCache phone={self.guest_phone_number} hash={self.polygon_hash[:8]} stale={self.is_stale()}>'


crop_hscode = db.Table(
    'crop_hscode',
    db.Column('crop_id', db.Integer, db.ForeignKey('crop.id'), primary_key=True),
    db.Column('hscode_id', db.Integer, db.ForeignKey('hscode.id'), primary_key=True),
)


class HSCode(db.Model):
    __tablename__ = 'hscode'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False, unique=True)       # ex: "1801", "ex 4101"
    description = db.Column(db.String(500), nullable=False)
    eudr_commodity = db.Column(db.String(50), nullable=False)          # Cattle, Cocoa, Coffee, Oil palm, Rubber, Soya, Wood
    is_ex_code = db.Column(db.Boolean, default=False)                  # True si "ex" (couverture partielle du code)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    crops = db.relationship('Crop', secondary=crop_hscode, backref=db.backref('hs_codes', lazy=True))

    def __repr__(self):
        return f"<HSCode(code={self.code}, commodity={self.eudr_commodity})>"

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'eudr_commodity': self.eudr_commodity,
            'is_ex_code': self.is_ex_code,
        }


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
 
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(255), nullable=False)
    slug        = db.Column(db.String(191), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('productcategory.id'), nullable=False)
 
    # ── Prix ─────────────────────────────────────────────────────────────────
    # `price` est TOUJOURS un prix par `unit`. En mode 'lot' et 'weight',
    # unit='kg', donc price = prix au kg — exactement comme sur une enchère.
    price            = db.Column(db.Numeric(12, 2), nullable=False)
    compare_at_price = db.Column(db.Numeric(12, 2), nullable=True)
    currency         = db.Column(db.String(10), default='USD')
    unit             = db.Column(db.String(20), default='kg')
 
    # ── Mode de vente & stock ────────────────────────────────────────────────
    # stock_qty est exprimé en `unit`. Numeric(12,3) et pas Integer : on doit
    # pouvoir vendre 12.500 kg. Le millième suffit largement pour du café.
    sale_mode           = db.Column(db.String(10), nullable=False, default='unit')
    stock_qty           = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    min_order_qty       = db.Column(db.Numeric(12, 3), nullable=False, default=1)
    order_step          = db.Column(db.Numeric(12, 3), nullable=False, default=1)
    low_stock_threshold = db.Column(db.Numeric(12, 3), default=5)
 
    # Produit réservé aux enchères : n'apparaît pas dans la grille boutique.
    is_auction_only = db.Column(db.Boolean, default=False)
 
    sku = db.Column(db.String(100), unique=True, nullable=True)
 
    # ── Traçabilité — le lien qui manquait ───────────────────────────────────
    # Rattache le produit à une parcelle réelle. C'est ce qui permet d'afficher
    # la géolocalisation, le couvert forestier 2020 et le statut EUDR sur la
    # fiche produit, au lieu d'une simple promesse marketing.
    farm_id               = db.Column(db.String(50), db.ForeignKey('farm.farm_id'), nullable=True)
    origin_country        = db.Column(db.String(100), nullable=True)
    is_deforestation_free = db.Column(db.Boolean, default=False)
    certification_labels  = db.Column(db.JSON, default=list)
 
    # ── Storytelling ─────────────────────────────────────────────────────────
    # origin_story reste pour la compatibilité, mais story_blocks est le nouveau
    # format : [{"type": "text"|"quote"|"image"|"stat", "content": "...",
    #            "caption": "...", "author": "..."}]
    origin_story   = db.Column(db.Text, nullable=True)
    story_blocks   = db.Column(db.JSON, default=list)
    farmer_name    = db.Column(db.String(150), nullable=True)
    harvest_year   = db.Column(db.Integer, nullable=True)
 
    # Fiche technique — le vocabulaire attendu par un acheteur de spécialité.
    altitude_m     = db.Column(db.Integer, nullable=True)
    varietal       = db.Column(db.String(120), nullable=True)   # SL28, Trinitario…
    process_method = db.Column(db.String(80), nullable=True)    # Washed, Natural…
    tasting_notes  = db.Column(db.JSON, default=list)
    cupping_score  = db.Column(db.Float, nullable=True)
 
    is_active    = db.Column(db.Boolean, default=True)
    is_featured  = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
 
    category = db.relationship('ProductCategory', backref='products')
    images   = db.relationship('EcoProductImage', backref='product', lazy=True,
                               cascade='all, delete-orphan',
                               order_by='EcoProductImage.position')
    farm     = db.relationship('Farm', foreign_keys=[farm_id],
                               primaryjoin='EcoProduct.farm_id == Farm.farm_id',
                               uselist=False, viewonly=True)
 
    # ── Règles métier ────────────────────────────────────────────────────────
 
    @property
    def is_lot(self):
        return self.sale_mode == 'lot'
 
    @property
    def total_price(self):
        """Prix du lot entier — n'a de sens qu'en mode 'lot'."""
        if not self.is_lot or self.price is None or self.stock_qty is None:
            return None
        return self.price * self.stock_qty
 
    def is_valid_quantity(self, qty):
        """Une quantité est valide si elle respecte min, pas et stock disponible.
 
        Mode 'lot' : min = pas = stock_qty, donc la seule quantité acceptée est
        le lot entier. La règle est la même pour les trois modes, c'est la
        configuration qui change — pas le code.
        """
        qty = Decimal(str(qty))
        if qty <= ZERO or qty > self.stock_qty:
            return False
        if qty < self.min_order_qty:
            return False
        step = self.order_step or Decimal('1')
        if step > ZERO and ((qty - self.min_order_qty) % step) != ZERO:
            return False
        return True
 
    def stock_status(self):
        if self.stock_qty is None or self.stock_qty <= ZERO:
            return 'out'
        if self.low_stock_threshold and self.stock_qty <= self.low_stock_threshold:
            return 'low'
        return 'ok'
 
    def to_dict(self, with_traceability=False):
        data = {
            'id': self.id, 'name': self.name, 'slug': self.slug,
            'description': self.description,
            'category_id': self.category_id,
            'category': self.category.name if self.category else None,
 
            'price': _f(self.price),
            'compare_at_price': _f(self.compare_at_price),
            'currency': self.currency,
            'unit': self.unit,
 
            'sale_mode': self.sale_mode,
            'stock_qty': _f(self.stock_qty),
            'min_order_qty': _f(self.min_order_qty),
            'order_step': _f(self.order_step),
            'low_stock_threshold': _f(self.low_stock_threshold),
            'stock_status': self.stock_status(),
            'total_price': _f(self.total_price),
            'is_auction_only': self.is_auction_only,
 
            'sku': self.sku,
            'origin_country': self.origin_country,
            'is_deforestation_free': self.is_deforestation_free,
            'certification_labels': self.certification_labels or [],
            'images': [img.public_url for img in self.images],
            'images_detail': [{'key': img.storage_key, 'url': img.public_url}
                              for img in self.images],
            'origin_story': self.origin_story,
            'story_blocks': self.story_blocks or [],
            'farmer_name': self.farmer_name,
            'harvest_year': self.harvest_year,
            'farm_id': self.farm_id,
 
            'altitude_m': self.altitude_m,
            'varietal': self.varietal,
            'process_method': self.process_method,
            'tasting_notes': self.tasting_notes or [],
            'cupping_score': self.cupping_score,
 
            'is_active': self.is_active,
            'is_featured': self.is_featured,
        }
        if with_traceability:
            data['traceability'] = self.traceability_dict()
        return data
 
    def traceability_dict(self):
        """Les preuves réelles tirées de la base Nkusu, pas des affirmations.
 
        Retourne None si le produit n'est rattaché à aucune parcelle — dans ce
        cas le front n'affiche simplement pas le panneau de preuve.
        """
        from app.models import FarmReport, Farm  # import local : évite le cycle
 
        farm = Farm.query.filter_by(farm_id=self.farm_id).first() if self.farm_id else None
        if not farm:
            return None
 
        report = FarmReport.query.filter_by(farm_id=farm.id) \
                                 .order_by(FarmReport.date_created.desc()).first()
        return {
            'farm_id': farm.farm_id,
            'farm_name': farm.name,
            'subcounty': farm.subcounty,
            'country': farm.country,
            'geolocation': farm.geolocation,
            'forest_cover_2020': report.forest_cover_2020 if report else None,
            'tree_cover_loss': report.tree_cover_loss if report else None,
            'radd_alert': report.radd_alert if report else None,
            'protected_area_status': report.protected_area_status if report else None,
            'eudr_compliance_assessment': report.eudr_compliance_assessment if report else None,
            'assessed_on': report.date_created.isoformat() if report and report.date_created else None,
        }

class EcoProductImage(db.Model):
    __tablename__ = 'ecoproductimage'
    id          = db.Column(db.Integer, primary_key=True)
    product_id  = db.Column(db.Integer, db.ForeignKey('ecoproduct.id'), nullable=False)
    # La clé de stockage : "products/ab12cd.jpg". C'est elle qui fait foi.
    storage_key = db.Column(db.String(500), nullable=True)
    # `url` reste pour les lignes antérieures à la migration 02. nullable=True
    # est indispensable : les nouvelles images ne renseignent que storage_key.
    url         = db.Column(db.String(500), nullable=True)
    is_primary  = db.Column(db.Boolean, default=False)
    position    = db.Column(db.Integer, default=0)

    @property
    def public_url(self):
        """L'URL est construite à la demande, jamais stockée. Migrer vers S3
        ne demandera alors aucune réécriture de la base."""
        if self.storage_key:
            from app.utils.storage import get_storage
            return get_storage().url(self.storage_key)
        return self.url


class EcoOrder(db.Model):
    __tablename__ = 'ecoorder'
    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    guest_email       = db.Column(db.String(255), nullable=True)
    guest_name        = db.Column(db.String(255), nullable=True)
    guest_phone       = db.Column(db.String(20), nullable=True)
    shipping_address  = db.Column(db.Text, nullable=True)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency          = db.Column(db.String(10), default='UGX')
    status            = db.Column(db.String(50), default='pending')  # pending, paid, shipped, delivered, cancelled, refunded
    payment_method    = db.Column(db.String(50), default='dpo')
    dpo_trans_token   = db.Column(db.String(100), nullable=True, unique=True)
    dpo_trans_ref     = db.Column(db.String(100), nullable=True)
    date_created      = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # ★ NOUVEAU

    items = db.relationship('EcoOrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    user  = db.relationship('User', foreign_keys=[user_id])  # ★ NOUVEAU — pour afficher le nom du compte si connecté

    def to_dict(self):
        # Nom/contact affiché à l'admin : priorité au compte utilisateur si présent, sinon aux infos invité
        customer_name  = self.guest_name or (self.user.username if self.user else None)
        customer_email = self.guest_email or (self.user.email if self.user else None)

        return {
            'id': self.id,
            'user_id': self.user_id,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'guest_phone': self.guest_phone,
            'shipping_address': self.shipping_address,
            'status': self.status,
            'total_amount': _f(self.total_amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'dpo_trans_ref': self.dpo_trans_ref,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_updated': self.date_updated.isoformat() if self.date_updated else None,
            'items': [i.to_dict() for i in self.items],
            'item_count': _f(sum(i.quantity for i in self.items)),        }


 
class EcoOrderItem(db.Model):
    __tablename__ = 'ecoorderitem'
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('ecoorder.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('ecoproduct.id'), nullable=False)
    quantity   = db.Column(db.Numeric(12, 3), nullable=False)   # en `unit` (kg le plus souvent)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)   # gelé au moment de l'achat
    unit       = db.Column(db.String(20), nullable=True)        # gelé aussi : 'kg', 'bag'…
 
    # Renseigné si la ligne provient d'une enchère gagnée.
    auction_lot_id = db.Column(db.Integer, db.ForeignKey('auctionlot.id'), nullable=True)
 
    product = db.relationship('EcoProduct')
 
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Produit supprimé',
            'product_image': (self.product.images[0].public_url
                              if self.product and self.product.images else None),
            'quantity': _f(self.quantity),
            'unit': self.unit or (self.product.unit if self.product else None),
            'unit_price': _f(self.unit_price),
            'line_total': _f(self.quantity * self.unit_price),
            'auction_lot_id': self.auction_lot_id,
        }


class StockMovement(db.Model):
    __tablename__ = 'stockmovement'
    id              = db.Column(db.Integer, primary_key=True)
    product_id      = db.Column(db.Integer, db.ForeignKey('ecoproduct.id'), nullable=False)
    order_id        = db.Column(db.Integer, db.ForeignKey('ecoorder.id'), nullable=True)
    quantity_change = db.Column(db.Numeric(12, 3), nullable=False)
    stock_before    = db.Column(db.Numeric(12, 3), nullable=False)
    stock_after     = db.Column(db.Numeric(12, 3), nullable=False)
    # 'sale', 'initial', 'manual_adjustment', 'restock', 'damage', 'return', 'auction_sale'
    reason          = db.Column(db.String(30), nullable=False)
    note            = db.Column(db.String(255), nullable=True)
    created_by      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date_created    = db.Column(db.DateTime, default=datetime.utcnow)
 
    product = db.relationship(
        'EcoProduct',
        backref=db.backref('stock_movements', lazy=True,
                           order_by='StockMovement.date_created.desc()')
    )
 
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'order_id': self.order_id,
            'quantity_change': _f(self.quantity_change),
            'stock_before': _f(self.stock_before),
            'stock_after': _f(self.stock_after),
            'reason': self.reason,
            'note': self.note,
            'created_by': self.created_by,
            'date_created': self.date_created.isoformat() if self.date_created else None,
        }
# =============================================================================
#  ENCHÈRES
# =============================================================================
 
class Auction(db.Model):
    """Une vente aux enchères : une fenêtre de temps, plusieurs lots."""
    __tablename__ = 'auction'
 
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(255), nullable=False)
    slug          = db.Column(db.String(191), unique=True, nullable=False)
    subtitle      = db.Column(db.String(255), nullable=True)
    description   = db.Column(db.Text, nullable=True)
    cover_image   = db.Column(db.String(500), nullable=True)
 
    starts_at     = db.Column(db.DateTime, nullable=False)
    ends_at       = db.Column(db.DateTime, nullable=False)
 
    # Anti-sniping : toute enchère posée dans les N dernières minutes repousse
    # la fin du lot d'autant. Sans ça, un script rafle tous les lots à la
    # dernière seconde et les vrais acheteurs abandonnent.
    anti_snipe_minutes = db.Column(db.Integer, default=3)
 
    currency      = db.Column(db.String(10), default='USD')
    # draft -> scheduled -> live -> closed
    status        = db.Column(db.String(20), nullable=False, default='draft')
    is_published  = db.Column(db.Boolean, default=False)
    # ── Accès et garantie de paiement ────────────────────────────────────────
    access_mode            = db.Column(db.String(20), nullable=False, default='open')
    deposit_amount         = db.Column(db.Numeric(12, 2), nullable=True)
    # Plafond accordé = caution × multiplicateur. 10 est le réglage courant
    # dans les ventes de café : 500 de caution ouvrent 5 000 d'exposition.
    deposit_multiplier     = db.Column(db.Integer, default=10)
    payment_deadline_hours = db.Column(db.Integer, default=72)
 
    date_created  = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
 
    lots = db.relationship('AuctionLot', backref='auction', lazy=True,
                           cascade='all, delete-orphan',
                           order_by='AuctionLot.lot_number')
 
    @property
    def is_live(self):
        now = datetime.utcnow()
        return self.status == 'live' and self.starts_at <= now < self.ends_at
 
    def stats(self):
        """Les quatre chiffres de l'en-tête : nombre d'enchères, valeur totale,
        moyenne pondérée au kg, prix du lot le plus cher."""
        total_bids = sum(l.bid_count or 0 for l in self.lots)
        total_value = sum((l.current_price_per_kg or ZERO) * l.weight_kg
                          for l in self.lots if l.bid_count)
        total_weight = sum(l.weight_kg for l in self.lots if l.bid_count)
        highest = max((l.current_price_per_kg or ZERO for l in self.lots), default=ZERO)
        return {
            'total_bids': total_bids,
            'total_value': _f(total_value),
            'weighted_average_per_kg': _f(total_value / total_weight) if total_weight else 0.0,
            'highest_lot_price_per_kg': _f(highest),
            'lot_count': len(self.lots),
        }
 
    def to_dict(self, with_lots=False):
        data = {
            'id': self.id, 'name': self.name, 'slug': self.slug,
            'subtitle': self.subtitle, 'description': self.description,
            'cover_image': self.cover_image,
            'starts_at': self.starts_at.isoformat() if self.starts_at else None,
            'ends_at': self.ends_at.isoformat() if self.ends_at else None,
            'anti_snipe_minutes': self.anti_snipe_minutes,
            'currency': self.currency,
            'status': self.status,
            'is_live': self.is_live,
            'is_published': self.is_published,
            'stats': self.stats(),
            'access_mode': self.access_mode,
            'deposit_amount': _f(self.deposit_amount),
            'deposit_multiplier': self.deposit_multiplier,
            'payment_deadline_hours': self.payment_deadline_hours,
        }
        if with_lots:
            data['lots'] = [l.to_dict() for l in self.lots]
        return data
 
 
class AuctionLot(db.Model):
    """Un lot mis aux enchères.
 
    Pointe obligatoirement vers un EcoProduct : c'est lui qui porte le nom, les
    images, l'histoire et la traçabilité. Le lot ne porte que l'état de
    l'enchère. Aucune duplication de contenu.
    """
    __tablename__ = 'auctionlot'
 
    id         = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('ecoproduct.id'), nullable=False)
    lot_number = db.Column(db.Integer, nullable=False)
 
    weight_kg             = db.Column(db.Numeric(12, 3), nullable=False)
    starting_price_per_kg = db.Column(db.Numeric(12, 2), nullable=False)
    min_increment         = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal('0.50'))
    # Prix de réserve : en dessous, le lot n'est pas adjugé. Jamais exposé au public.
    reserve_price_per_kg  = db.Column(db.Numeric(12, 2), nullable=True)
 
    current_price_per_kg  = db.Column(db.Numeric(12, 2), nullable=True)
    bid_count             = db.Column(db.Integer, default=0)
    winner_user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
 
    # Fin propre au lot : décalée par l'anti-sniping, indépendamment des autres.
    ends_at = db.Column(db.DateTime, nullable=True)
 
# scheduled -> live -> awaiting_payment -> sold | unsold | cancelled    
    status   = db.Column(db.String(20), nullable=False, default='scheduled')
    order_id = db.Column(db.Integer, db.ForeignKey('ecoorder.id'), nullable=True)
    # Échéance de paiement du lot adjugé. Passé ce délai, la caution est
    # saisie et le lot repart au second enchérisseur.
    payment_due_at = db.Column(db.DateTime, nullable=True)
    default_count  = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
 
    product = db.relationship('EcoProduct')
    bids    = db.relationship('Bid', backref='lot', lazy=True,
                              cascade='all, delete-orphan',
                              order_by='Bid.date_created.desc()')
 
    __table_args__ = (
        db.UniqueConstraint('auction_id', 'lot_number', name='uq_auction_lot_number'),
    )
 
    @property
    def next_min_bid(self):
        """Le montant minimum acceptable pour la prochaine enchère."""
        if self.current_price_per_kg is None:
            return self.starting_price_per_kg
        return self.current_price_per_kg + self.min_increment
 
    @property
    def effective_ends_at(self):
        return self.ends_at or (self.auction.ends_at if self.auction else None)
 
    @property
    def is_open(self):
        end = self.effective_ends_at
        return (self.status == 'live'
                and end is not None
                and datetime.utcnow() < end)
 
    def extend_for_anti_snipe(self):
        """Repousse la fin du lot si l'enchère arrive dans la fenêtre critique.
        Retourne True si une prolongation a eu lieu."""
        window = timedelta(minutes=self.auction.anti_snipe_minutes or 0)
        if not window:
            return False
        end = self.effective_ends_at
        now = datetime.utcnow()
        if end and (end - now) < window:
            self.ends_at = now + window
            return True
        return False
 
    def to_dict(self, include_product=True, for_admin=False):
        data = {
            'id': self.id,
            'auction_id': self.auction_id,
            'product_id': self.product_id,
            'lot_number': self.lot_number,
            'weight_kg': _f(self.weight_kg),
            'starting_price_per_kg': _f(self.starting_price_per_kg),
            'min_increment': _f(self.min_increment),
            'current_price_per_kg': _f(self.current_price_per_kg),
            'next_min_bid': _f(self.next_min_bid),
            'current_total': _f((self.current_price_per_kg or self.starting_price_per_kg) * self.weight_kg),
            'bid_count': self.bid_count or 0,
            'status': self.status,
            'is_open': self.is_open,
            'ends_at': self.effective_ends_at.isoformat() if self.effective_ends_at else None,
            'currency': self.auction.currency if self.auction else 'USD',
            'auction_slug': self.auction.slug if self.auction else None,
        }
        if include_product and self.product:
            data['name'] = self.product.name
            data['image'] = self.product.images[0].public_url if self.product.images else None
            data['origin_country'] = self.product.origin_country
            data['process_method'] = self.product.process_method
            data['varietal'] = self.product.varietal
            data['is_deforestation_free'] = self.product.is_deforestation_free
        if for_admin:
            data['reserve_price_per_kg'] = _f(self.reserve_price_per_kg)
            data['winner_user_id'] = self.winner_user_id
            data['order_id'] = self.order_id
        return data
 
 
class Bid(db.Model):
    """Une enchère posée. Table en append-only : on n'édite ni ne supprime
    jamais une ligne — c'est l'historique qui fait foi en cas de litige."""
    __tablename__ = 'bid'
 
    id            = db.Column(db.Integer, primary_key=True)
    lot_id        = db.Column(db.Integer, db.ForeignKey('auctionlot.id'), nullable=False)
    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount_per_kg = db.Column(db.Numeric(12, 2), nullable=False)
    is_auto       = db.Column(db.Boolean, default=False)  # posée par le proxy bidding
    date_created  = db.Column(db.DateTime, default=datetime.utcnow, index=True)
 
    user = db.relationship('User', foreign_keys=[user_id])
 
    def to_dict(self, mask_identity=True):
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'bidder': (f"Enchérisseur #{self.user_id}" if mask_identity
                       else (self.user.username if self.user else None)),
            'user_id': None if mask_identity else self.user_id,
            'amount_per_kg': _f(self.amount_per_kg),
            'is_auto': self.is_auto,
            'date_created': self.date_created.isoformat() if self.date_created else None,
        }
 
 
class AutoBid(db.Model):
    """Enchère automatique (proxy bidding) : l'utilisateur fixe son maximum,
    le système enchérit pour lui au minimum nécessaire pour rester en tête.
 
    Un seul AutoBid actif par (lot, utilisateur) — relever son maximum met à
    jour la ligne existante.
    """
    __tablename__ = 'autobid'
 
    id                = db.Column(db.Integer, primary_key=True)
    lot_id            = db.Column(db.Integer, db.ForeignKey('auctionlot.id'), nullable=False)
    user_id           = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    max_amount_per_kg = db.Column(db.Numeric(12, 2), nullable=False)
    is_active         = db.Column(db.Boolean, default=True)
    date_created      = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
 
    lot  = db.relationship('AuctionLot')
    user = db.relationship('User', foreign_keys=[user_id])
 
    __table_args__ = (
        db.UniqueConstraint('lot_id', 'user_id', name='uq_autobid_lot_user'),
    )
 
    def to_dict(self):
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'max_amount_per_kg': _f(self.max_amount_per_kg),
            'is_active': self.is_active,
        }
class AuctionRegistration(db.Model):
    """L'inscription d'un enchérisseur à une vente.
 
    Une ligne par (vente, utilisateur). C'est elle qui porte le droit
    d'enchérir, le plafond, et l'état de la caution.
    """
    __tablename__ = 'auctionregistration'
 
    id         = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
 
    # pending -> deposit_pending -> approved
    #                            -> rejected
    #         approved -> defaulted   (n'a pas payé un lot remporté)
    status = db.Column(db.String(20), nullable=False, default='pending')
 
    # Exposition maximale autorisée, toutes enchères menées confondues.
    bid_limit = db.Column(db.Numeric(12, 2), nullable=True)
 
    # ── Caution ──────────────────────────────────────────────────────────────
    # none | held | forfeited | refunded
    deposit_status   = db.Column(db.String(20), nullable=False, default='none')
    deposit_amount   = db.Column(db.Numeric(12, 2), nullable=True)
    deposit_currency = db.Column(db.String(10), nullable=True)
    deposit_paid_at  = db.Column(db.DateTime, nullable=True)
    # La caution n'est pas une commande : aucun produit, aucun stock, aucune
    # livraison. Elle porte donc ses propres références DPO plutôt que de
    # détourner EcoOrder.
    dpo_trans_token  = db.Column(db.String(100), nullable=True, unique=True)
    dpo_trans_ref    = db.Column(db.String(100), nullable=True)
 
    # ── Identité commerciale, demandée à l'inscription ───────────────────────
    company_name     = db.Column(db.String(255), nullable=True)
    contact_phone    = db.Column(db.String(20), nullable=True)
    contact_email    = db.Column(db.String(255), nullable=True)
    shipping_country = db.Column(db.String(100), nullable=True)
 
    approved_at  = db.Column(db.DateTime, nullable=True)
    approved_by  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    admin_note   = db.Column(db.String(500), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
 
    auction = db.relationship('Auction', backref=db.backref('registrations', lazy=True))
    user    = db.relationship('User', foreign_keys=[user_id])
 
    __table_args__ = (
        db.UniqueConstraint('auction_id', 'user_id', name='uq_registration_auction_user'),
    )
 
    @property
    def can_bid(self):
        return self.status == 'approved'
 
    def committed_exposure(self):
        """Somme de ce que l'utilisateur mène actuellement sur cette vente.
 
        On ne compte que les lots où il est en tête et encore engageants : un
        lot déjà payé ne pèse plus sur son plafond, un lot où il a été dépassé
        non plus.
        """
        from app.models import AuctionLot
        lots = AuctionLot.query.filter(
            AuctionLot.auction_id == self.auction_id,
            AuctionLot.winner_user_id == self.user_id,
            AuctionLot.status.in_(('live', 'awaiting_payment')),
        ).all()
        return sum(((l.current_price_per_kg or ZERO) * l.weight_kg for l in lots), ZERO)
 
    def remaining_limit(self):
        if self.bid_limit is None:
            return None            # aucun plafond configuré
        return self.bid_limit - self.committed_exposure()
 
    def to_dict(self, for_admin=False):
        data = {
            'id': self.id,
            'auction_id': self.auction_id,
            'status': self.status,
            'can_bid': self.can_bid,
            'bid_limit': _f(self.bid_limit),
            'committed_exposure': _f(self.committed_exposure()),
            'remaining_limit': _f(self.remaining_limit()),
            'deposit_status': self.deposit_status,
            'deposit_amount': _f(self.deposit_amount),
            'deposit_currency': self.deposit_currency,
            'company_name': self.company_name,
        }
        if for_admin:
            data.update({
                'user_id': self.user_id,
                'username': self.user.username if self.user else None,
                'contact_phone': self.contact_phone,
                'contact_email': self.contact_email,
                'shipping_country': self.shipping_country,
                'deposit_paid_at': self.deposit_paid_at.isoformat() if self.deposit_paid_at else None,
                'dpo_trans_ref': self.dpo_trans_ref,
                'admin_note': self.admin_note,
                'date_created': self.date_created.isoformat() if self.date_created else None,
            })
        return data
 
 
class BidderSanction(db.Model):
    """Trace des défauts de paiement.
 
    Une maison de vente qui ne garde pas cette mémoire réinvite l'année
    suivante celui qui n'a pas payé. La sanction porte sur l'utilisateur, pas
    sur la vente : elle bloque l'inscription aux ventes futures.
    """
    __tablename__ = 'biddersanction'
 
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=True)
    lot_id     = db.Column(db.Integer, db.ForeignKey('auctionlot.id'), nullable=True)
 
    # payment_default | manipulation | admin_block
    reason        = db.Column(db.String(30), nullable=False)
    amount_lost   = db.Column(db.Numeric(12, 2), nullable=True)   # caution saisie
    note          = db.Column(db.String(500), nullable=True)
    # Blocage à durée déterminée. NULL = définitif.
    blocked_until = db.Column(db.DateTime, nullable=True)
    is_active     = db.Column(db.Boolean, default=True)
 
    created_by   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
 
    user = db.relationship('User', foreign_keys=[user_id])
 
    @staticmethod
    def is_blocked(user_id):
        """True si l'utilisateur a une sanction active et non expirée."""
        now = datetime.utcnow()
        q = BidderSanction.query.filter(
            BidderSanction.user_id == user_id,
            BidderSanction.is_active.is_(True),
        )
        for sanction in q.all():
            if sanction.blocked_until is None or sanction.blocked_until > now:
                return True
        return False
 
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'auction_id': self.auction_id,
            'lot_id': self.lot_id,
            'reason': self.reason,
            'amount_lost': _f(self.amount_lost),
            'note': self.note,
            'blocked_until': self.blocked_until.isoformat() if self.blocked_until else None,
            'is_active': self.is_active,
            'date_created': self.date_created.isoformat() if self.date_created else None,
        }
 