from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
mysql = MySQL()
login_manager = LoginManager()
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mysql.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    migrate.init_app(app, db)

    with app.app_context():
        from app.models import User  # Ensure models are imported after app context is set up

    from app.routes import auth, farm, qr, map, main, forest, point, admin, farmdata
    from app.routes import crop
    from app.routes import farmergroup  
    from app.routes import producecategory
    from app.routes import district
    app.register_blueprint(auth.bp)
    app.register_blueprint(farm.bp)
    app.register_blueprint(qr.bp)
    app.register_blueprint(map.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(forest.bp)
    app.register_blueprint(point.bp)
    app.register_blueprint(admin.admin_bp)
    app.register_blueprint(farmdata.bp)
    app.register_blueprint(crop.crop_bp)
    app.register_blueprint(farmergroup.bp)
    app.register_blueprint(producecategory.bp)
    app.register_blueprint(district.bp)
    
    from app.routes.testDb import test
    app.register_blueprint(test)

    @app.template_filter('remove_gfw')
    def remove_gfw(text):
        if text:
            # Remplace 'gfw' et 'umd' par une chaîne vide
            return text.replace('gfw', '').replace('umd', '')
        return text

    app.jinja_env.filters['remove_gfw'] = remove_gfw


    return app
