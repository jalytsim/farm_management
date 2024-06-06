from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
mysql = MySQL()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # Import User model here to avoid circular import
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mysql.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Specify the login view
    login_manager.login_message_category = 'info'

    with app.app_context():
        from app.models import User  # Ensure models are imported for database creation

    from app.routes import auth, farm, qr, map, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(farm.bp)
    app.register_blueprint(qr.bp)
    app.register_blueprint(map.bp)
    app.register_blueprint(main.bp)
    
    from app.routes.testDb import test
    app.register_blueprint(test)

    return app
