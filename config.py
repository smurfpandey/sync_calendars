"""Flask app configuration."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    """Set Flask configuration from environment variables."""
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')
    SECRET_KEY = environ.get('SECRET_KEY')

    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Static Assets
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    # Auth0
    AUTH0_CLIENT_ID = environ.get('AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = environ.get('AUTH0_CLIENT_SECRET')
    AUTH0_API_BASE_URL = environ.get('AUTH0_API_BASE_URL')
    AUTH0_ACCESS_TOKEN_URL = AUTH0_API_BASE_URL + "/oauth/token"
    AUTH0_AUTHORIZE_URL = AUTH0_API_BASE_URL + "/authorize"

    # O365
    O365_CLIENT_ID = environ.get('O365_CLIENT_ID')
    O365_CLIENT_SECRET = environ.get('O365_CLIENT_SECRET')
    O365_AUTHORITY = "https://login.microsoftonline.com/common"
    O365_AUTHORIZE_URL = O365_AUTHORITY + "/oauth2/v2.0/authorize"
    O365_ACCESS_TOKEN_URL = O365_AUTHORITY + "/oauth2/v2.0/token"
    O365_API_BASE_URL = "https://graph.microsoft.com/v1.0/"

    # Celery
    broker_url = environ.get('CELERY_BROKER_URL')
    result_backend = environ.get('CELERY_RESULT_BACKEND')
