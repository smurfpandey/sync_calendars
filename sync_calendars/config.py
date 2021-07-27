# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
from environs import Env

env = Env()
env.read_env()

FLASK_APP = env.str('FLASK_APP')
ENV = env.str('FLASK_ENV', default="production")
SECRET_KEY = env.str("SECRET_KEY")
APP_BASE_URL = env.str('APP_BASE_URL') # Base URL of the app
CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
LOG_LEVEL = env.str('LOG_LEVEL', default="INFO")

# Flask-SQLAlchemy
SQLALCHEMY_DATABASE_URI = env.str('DATABASE_URL')
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Static Assets
STATIC_FOLDER = '/static/dist'

# Auth0
AUTH0_CLIENT_ID = env.str('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = env.str('AUTH0_CLIENT_SECRET')
AUTH0_API_BASE_URL = env.str('AUTH0_API_BASE_URL')
AUTH0_ACCESS_TOKEN_URL = AUTH0_API_BASE_URL + "/oauth/token"
AUTH0_AUTHORIZE_URL = AUTH0_API_BASE_URL + "/authorize"

# O365
O365_CLIENT_ID = env.str('O365_CLIENT_ID')
O365_CLIENT_SECRET = env.str('O365_CLIENT_SECRET')
O365_AUTHORITY = "https://login.microsoftonline.com/common"
O365_AUTHORIZE_URL = O365_AUTHORITY + "/oauth2/v2.0/authorize"
O365_ACCESS_TOKEN_URL = O365_AUTHORITY + "/oauth2/v2.0/token"
O365_API_BASE_URL = "https://graph.microsoft.com/v1.0/"

# Celery
broker_url = env.str('CELERY_BROKER_URL')
# result_backend = env.str('CELERY_RESULT_BACKEND')
