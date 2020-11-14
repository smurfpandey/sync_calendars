"""Initialize app."""
from os import environ
from werkzeug.exceptions import BadRequest

from celery import Celery
from flask import Flask, render_template
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from flask_sqlalchemy import SQLAlchemy

from sync_calendars.tasks import init_celery_app

celery = Celery(__name__)
db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()
sentry_sdk.init(
    environ.get('SENTRY_DSN'),
    integrations=[
        FlaskIntegration(),
        CeleryIntegration(),
        SqlalchemyIntegration()
    ]
)

def create_app():
    """Construct the core app object."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

     # config file has STATIC_FOLDER='/static/dist'
    app.static_url_path=app.config.get('STATIC_FOLDER')

    # set the absolute path to the static folder
    app.static_folder=app.root_path + app.static_url_path

    # Initialize Plugins
    init_celery_app(celery, app)
    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    with app.app_context():
        from sync_calendars.routes import auth, o365, views, api

        # Register Blueprints
        app.register_blueprint(views.main_bp)
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(o365.o365_bp)
        app.register_blueprint(api.api_bp)

        # Create Database Models
        db.create_all()

    # Handling error 400 and displaying relevant web page
    @app.errorhandler(400)
    def handle_bad_request(err):
        """Handle 400 BadRequest HTTP error"""
        return render_template('400.html'), 400

    # Handling error 404 and displaying relevant web page
    @app.errorhandler(404)
    def handle_not_found_request(err):
        """Handle 404 BadRequest HTTP error"""
        return render_template('404.html'), 404

    return app
