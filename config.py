import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'brian')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'brian')
    MYSQL_DB = os.getenv('MYSQL_DB', 'qrcode')
    SQLALCHEMY_DATABASE_URI = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEOJSON_FILE_PATH = os.path.join(os.path.dirname(__file__), 'app', 'static','geoBoundaries-UGA-ADM3.geojson')
