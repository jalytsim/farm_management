import os
from dotenv import load_dotenv

# Doit être appelé AVANT toute lecture de os.getenv() ci-dessous.
# config.py est importé en premier par app/__init__.py, donc c'est
# ici et nulle part ailleurs que le .env doit être chargé.
load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 's9z#q4L!f7mJw2N8d*BvP3eH1x@k$0ZrT6yV9uF5oCnXgA&LQjW*M7bDzPlKs')

    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'brian')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'brian')
    MYSQL_DB = os.getenv('MYSQL_DB', 'qrcode')
    SQLALCHEMY_DATABASE_URI = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GEOJSON_FILE_PATH = os.path.join(os.path.dirname(__file__), 'app', 'static', 'geoBoundaries-UGA-ADM3.geojson')
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    SENTINEL_CLIENT_ID = os.getenv('SENTINEL_CLIENT_ID', '0bfcba08-1240-451e-bf8f-93aa71eff6c1')
    SENTINEL_CLIENT_SECRET = os.getenv('SENTINEL_CLIENT_SECRET', '2iJGb9PNYtCABXZOXHhWAxICOmTs4D9X')

    # ── Stockage des médias ──────────────────────────────────────────────────
    STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'local')
    MEDIA_ROOT = os.getenv(
        'MEDIA_ROOT',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')
    )
    S3_BUCKET = os.getenv('S3_BUCKET')
    S3_REGION = os.getenv('S3_REGION', 'auto')
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
    S3_PUBLIC_BASE_URL = os.getenv('S3_PUBLIC_BASE_URL')

    # ── Paiements : Mobile Money (Nkusu IoT) ─────────────────────────────────
    MOBILE_MONEY_API_URL = os.getenv(
        'MOBILE_MONEY_API_URL',
        'https://188.166.125.28/nkusu-iot/api/nkusu-iot/payments'
    )
    MOBILE_MONEY_STATUS_URL = os.getenv(
        'MOBILE_MONEY_STATUS_URL',
        'https://188.166.125.28/nkusu-iot/api/nkusu-iot/payments'
    )
    MOBILE_MONEY_VERIFY_SSL = os.getenv('MOBILE_MONEY_VERIFY_SSL', 'false').lower() == 'true'

    # ── Paiements : DPO Pay ───────────────────────────────────────────────────
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://www.nkusu.com')
    DPO_REDIRECT_URL = os.getenv('DPO_REDIRECT_URL', 'https://www.nkusu.com/api/payments/payment/success')
    DPO_BACK_URL = os.getenv('DPO_BACK_URL', 'https://www.nkusu.com/api/payments/payment/cancelled')
    DPO_COMPANY_TOKEN = os.getenv('DPO_COMPANY_TOKEN')
    DPO_SERVICE_TYPE = os.getenv('DPO_SERVICE_TYPE')

    # ── Devises ───────────────────────────────────────────────────────────────
    SUPPORTED_CURRENCIES = [
        c.strip().upper()
        for c in os.getenv('SUPPORTED_CURRENCIES', 'UGX,USD,KES,TZS,ZAR').split(',')
        if c.strip()
    ]
    DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'UGX')

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS = [
        o.strip()
        for o in os.getenv('CORS_ORIGINS', 'https://www.nkusu.com').split(',')
        if o.strip()
    ]