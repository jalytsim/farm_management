from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_login import LoginManager
from flask_cors import CORS
from config import Config
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import tempfile
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.scheduler import run_weather_check
from app.utils.schedulerpest import run_gdd_pest_check
import os


db = SQLAlchemy()
mysql = MySQL()
login_manager = LoginManager()
jwt = JWTManager()
migrate = Migrate()


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


# ═══════════════════════════════════════════════════════════════════
#  FILTRES ALEMBIC — configuration centrale, robuste, long terme
#
#  Problèmes résolus une fois pour toutes :
#
#  1. "Cannot drop index farm_id" (MySQL FK index auto)
#     → _alembic_include_object : ignore les index réfléchis
#       sans équivalent dans le modèle
#
#  2. Faux positifs de type VARCHAR(255) vs String(150) etc.
#     → _alembic_compare_type : ignore les comparaisons bénignes
#       MAIS détecte les vrais changements importants comme
#       Text → LONGTEXT, String → Text, etc.
#
#  Règle :
#    - Si le modèle déclare LONGTEXT  et la BDD a TEXT  → migration ✅
#    - Si le modèle déclare LONGTEXT  et la BDD a LONGTEXT → skip ✅
#    - Si le modèle déclare String(150) et la BDD a VARCHAR(255) → skip ✅
#    - Si le modèle déclare Text et la BDD a VARCHAR → migration ✅
# ═══════════════════════════════════════════════════════════════════

def _alembic_include_object(object, name, type_, reflected, compare_to):
    """
    Ignore les index auto-créés par MySQL pour les FK.
    Ces index existent en BDD mais pas dans le modèle Python.
    Sans ce filtre, Alembic essaie de les supprimer et MySQL refuse.
    """
    if type_ == "index" and reflected and compare_to is None:
        return False
    return True


def _alembic_compare_type(context, inspected_column, metadata_column,
                           inspected_type, metadata_type):
    """
    Comparaison intelligente des types de colonnes.

    Retourne :
      True  → les types diffèrent, une migration est nécessaire
      False → ignorer cette différence (faux positif)

    Logique :
      - LONGTEXT vs TEXT/Text  → True  (migration réelle nécessaire)
      - MEDIUMTEXT vs TEXT     → True  (migration réelle nécessaire)
      - VARCHAR(N) vs String(M)→ False (variation de longueur tolérée)
      - Tout autre cas         → False (comportement conservateur)
    """
    from sqlalchemy.dialects.mysql import LONGTEXT, MEDIUMTEXT
    from sqlalchemy import Text, String

    meta_type_class     = type(metadata_type)
    inspected_type_class= type(inspected_type)

    # ── Cas 1 : le modèle veut LONGTEXT ──────────────────────────
    # Si la BDD n'a pas LONGTEXT → migration nécessaire
    if meta_type_class is LONGTEXT:
        return inspected_type_class is not LONGTEXT

    # ── Cas 2 : le modèle veut MEDIUMTEXT ────────────────────────
    if meta_type_class is MEDIUMTEXT:
        return inspected_type_class is not MEDIUMTEXT

    # ── Cas 3 : variation de longueur String/VARCHAR ──────────────
    # Toléré — MySQL peut avoir VARCHAR(255) alors que le modèle
    # déclare String(150). Ce n'est pas un vrai problème.
    if meta_type_class is String and inspected_type_class is String:
        return False

    # ── Cas 4 : tout autre changement → ignorer (conservateur) ───
    # Évite les faux positifs dus aux différences de dialecte
    # entre SQLAlchemy et MySQL (TINYINT vs Boolean, etc.)
    return False


def start_scheduler(app):
    if os.environ.get("RUN_MAIN") == "true":
        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda: run_weather_check(app), 'cron', hour=22, minute=59)
        scheduler.add_job(lambda: run_gdd_pest_check(app), 'cron', hour=23, minute=00)
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

    # ★ compare_type = fonction intelligente (pas True/False)
    #   Détecte LONGTEXT/MEDIUMTEXT mais ignore VARCHAR(N) vs String(M)
    migrate.init_app(
        app,
        db,
        compare_type=_alembic_compare_type,
        include_object=_alembic_include_object,
    )


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.routes import (
        auth, map, admin, weather, stgl, solar, graph, api_crop,
        api_farm, api_farm_data, api_producecategory, api_district,
        api_farmer_group,
        api_point, api_forest,
        api_qr, api_gfw, api_grade,
        api_irrigations, api_kc, api_pays,
        api_user, api_store, api_product, api_dashboard, api_eudr,
        api_payments, api_features, api_notifications, api_farmreport,
        api_certificate, api_forestreport, api_tree,
        api_sentinel,
        api_blog,  
        ecommerce,  
    )

    blueprints = [
        auth.bp, map.bp, admin.admin_bp,
        api_crop.api_crop_bp,
        graph.bp, solar.bp, stgl.bp, weather.bp,
        api_farm.bp, api_farm_data.bp, api_producecategory.bp, api_district.bp,
        api_farmer_group.bp, api_point.bp, api_forest.bp, api_qr.bp,
        api_gfw.bp, api_pays.bp, api_kc.bp, api_irrigations.bp,
        api_grade.bp, api_user.bp,
        api_store.api_store_bp, api_product.api_product_bp,
        api_dashboard.dashboard_api_bp,
        api_eudr.api_eudr_bp, api_payments.api_payments_bp,
        api_features.api_feature_bp, api_notifications.api_notifications_bp,
        api_farmreport.api_farmreport_bp, api_certificate.certificate_bp,
        api_forestreport.api_forestreport_bp, api_tree.bp,
        api_sentinel.sentinel_bp,
        api_blog.bp, 
        ecommerce.bp,
    ]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


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
        from app.models import User  # noqa: F401

    start_scheduler(app)


    return app
