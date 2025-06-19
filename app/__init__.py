from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_login import LoginManager
from flask_cors import CORS
from config import Config
from flask_jwt_extended import JWTManager
import tempfile
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.scheduler import run_weather_check
from app.utils.schedulerpest import run_gdd_pest_check
import os

db = SQLAlchemy()
mysql = MySQL()
login_manager = LoginManager()
jwt = JWTManager()

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


def start_scheduler(app):
    # ✅ Lancer le scheduler uniquement dans le processus principal Gunicorn
    if os.environ.get("RUN_MAIN") == "true":
        scheduler = BackgroundScheduler()
        # scheduler.add_job(lambda: run_weather_check(app), 'cron', hour=11, minute=20)
        # scheduler.add_job(lambda: run_gdd_pest_check(app), 'cron', hour=11, minute=25)
        scheduler.start()
        print("✅ Scheduler lancé dans le process principal.")
    else:
        print("⚠️ Ce n'est pas le process principal, scheduler ignoré.")

def init_extensions(app):
    """Initialize Flask extensions."""
    db.init_app(app)
    mysql.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

def register_blueprints(app):
    """Register Flask blueprints."""
    from app.routes import (
        auth, farm, qr, map, main, forest, point, admin, 
        farmdata, tree, crop, farmergroup, producecategory, 
        district, weather, stgl, solar, graph, api_crop ,
          api_farm, api_farm_data,api_producecategory,api_district,
          api_farmer_group,
            api_point,api_forest,
            api_qr,api_qr,api_gfw,api_grade,
              api_irrigations,api_kc,api_pays,
              api_user, api_store, api_product, api_dashboard,api_eudr,api_payments,api_features,api_notifications,
    )
    
    blueprints = [
        auth.bp, farm.bp, qr.bp, map.bp, main.bp, forest.bp, 
        point.bp, admin.admin_bp, farmdata.bp, crop.crop_bp, 
        api_crop.api_crop_bp, farmergroup.bp, producecategory.bp, 
        district.bp, tree.bp, graph.bp, solar.bp, stgl.bp, weather.bp, 
        api_farm.bp, api_farm_data.bp,api_producecategory.bp,api_district.bp,
        api_farmer_group.bp,api_point.bp,api_forest.bp,api_qr.bp,api_gfw.bp,api_pays.bp,api_kc.bp,api_irrigations.bp,
        api_grade.bp,api_user.bp,api_store.api_store_bp, api_product.api_product_bp, api_dashboard.dashboard_api_bp,api_eudr.api_eudr_bp,
        api_payments.api_payments_bp,api_features.api_feature_bp,api_notifications.api_notifications_bp,

    ]
    
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    from app.routes.testDb import test
    app.register_blueprint(test)

def register_filters(app):
    """Register custom Jinja filters."""
    @app.template_filter('remove_gfw')
    def remove_gfw(text):
        if text:
            return text.replace('gfw', '').replace('umd', '')
        return text
    
    app.jinja_env.filters['remove_gfw'] = remove_gfw

def create_app():
    lock_path = os.path.join(tempfile.gettempdir(), "farm_scheduler.lock")
    if os.path.exists(lock_path):
        os.remove(lock_path)

    app = Flask(__name__)
    app.config.from_object(Config)
    
    init_extensions(app)
    register_blueprints(app)
    register_filters(app)
    
    with app.app_context():
        from app.models import User

    # ✅ Démarrer le scheduler ici
    start_scheduler(app)

    return app
