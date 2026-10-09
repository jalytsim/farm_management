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


def _alembic_include_object(object, name, type_, reflected, compare_to):
    if type_ == "index" and reflected and compare_to is None:
        return False
    return True


def _alembic_compare_type(context, inspected_column, metadata_column,
                           inspected_type, metadata_type):
    from sqlalchemy.dialects.mysql import LONGTEXT, MEDIUMTEXT
    from sqlalchemy import String

    meta_type_class = type(metadata_type)
    inspected_type_class = type(inspected_type)

    if meta_type_class is LONGTEXT:
        return inspected_type_class is not LONGTEXT

    if meta_type_class is MEDIUMTEXT:
        return inspected_type_class is not MEDIUMTEXT

    if meta_type_class is String and inspected_type_class is String:
        return False

    return False


def start_scheduler(app):
    if os.environ.get("RUN_MAIN") == "true":
        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda: run_weather_check(app), 'cron', hour=22, minute=59)
        scheduler.add_job(lambda: run_gdd_pest_check(app), 'cron', hour=23, minute=00)
        scheduler.start()
        print("[OK] Scheduler lance dans le process principal.")
    else:
        print("[i] Ce n'est pas le process principal, scheduler ignore.")


def init_extensions(app):
    """Initialize Flask extensions."""
    db.init_app(app)
    mysql.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)

    # ★ CORS restreint aux origines de confiance (config via CORS_ORIGINS dans .env)
    #   Une route de paiement ne doit jamais accepter "*" en production.
    CORS(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=True)

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
        api_blog, api_hscode,
        ecommerce, ecommerce_customers,
        auction, api_tree_co2,ecommerce_stats,api_crop_variety, 
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
        api_blog.bp, api_hscode.bp,
        ecommerce.bp, ecommerce_customers.bp,
        auction.bp, api_tree_co2.bp,ecommerce_stats.bp,api_crop_variety.bp, 
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


BINARY_TRANSPORT_HEADER = 'X-Binary-Transport'


def register_binary_transport(app):
    """
    Les gestionnaires de téléchargement (IDM, XDM...) interceptent toute réponse
    binaire (PDF, CSV, XLSX, images) même en XHR : le frontend recevait alors un
    corps vide → "Échec de chargement du document PDF". Quand le client envoie
    `X-Binary-Transport: base64` (axiosInstance le fait pour chaque requête
    responseType 'blob'), on renvoie le fichier dans du JSON :
        {"__binary__": true, "mimetype", "filename", "data": <base64>}
    que ces outils ne capturent jamais ; l'intercepteur axios reconstruit le Blob.
    Les réponses JSON (erreurs comprises) sont laissées telles quelles.
    """
    import base64
    import json
    import re
    from flask import request

    @app.after_request
    def _binary_as_base64(response):
        if request.headers.get(BINARY_TRANSPORT_HEADER, '').lower() != 'base64':
            return response
        if response.mimetype == 'application/json' or response.status_code >= 300:
            return response

        response.direct_passthrough = False  # send_file → corps lisible
        payload = response.get_data()
        disposition = response.headers.get('Content-Disposition', '')
        match = re.search(r"filename\*=UTF-8''([^;]+)|filename=\"?([^\";]+)\"?", disposition)
        filename = None
        if match:
            from urllib.parse import unquote
            filename = unquote(match.group(1)) if match.group(1) else match.group(2)

        mimetype = response.mimetype or 'application/octet-stream'
        if mimetype == 'application/octet-stream' and (
                payload[:4] == b'%PDF' or (filename or '').lower().endswith('.pdf')):
            mimetype = 'application/pdf'

        response.set_data(json.dumps({
            '__binary__': True,
            'mimetype':   mimetype,
            'filename':   filename,
            'data':       base64.b64encode(payload).decode('ascii'),
        }))
        response.mimetype = 'application/json'
        response.headers.pop('Content-Disposition', None)
        response.headers.pop('Content-Length', None)
        response.headers['Content-Length'] = str(len(response.get_data()))
        response.headers['Cache-Control'] = 'no-store'
        return response


def create_app():
    lock_path = os.path.join(tempfile.gettempdir(), "farm_scheduler.lock")
    if os.path.exists(lock_path):
        os.remove(lock_path)

    app = Flask(__name__)
    app.config.from_object(Config)

    # 🔒 Les valeurs par défaut de SECRET_KEY / JWT_SECRET_KEY sont dans le code
    # (donc sur GitHub) : sans variables d'environnement, n'importe qui pourrait
    # signer un JWT admin ou un lien de rapport. On le signale très visiblement.
    for key in ('SECRET_KEY', 'JWT_SECRET_KEY'):
        if not os.getenv(key):
            app.logger.critical(
                "[SECURITY] %s n'est pas défini dans l'environnement : la valeur par défaut "
                "publique du code est utilisée. Définissez-le dans .env avant la mise en prod.", key)

    init_extensions(app)
    register_blueprints(app)
    register_filters(app)
    register_binary_transport(app)

    with app.app_context():
        from app.models import User  # noqa: F401

    start_scheduler(app)

    return app