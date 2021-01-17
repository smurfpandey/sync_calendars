"""Routes for user authentication."""
from datetime import datetime

from flask import redirect, Blueprint, url_for
from flask_login import current_user, login_user

from sync_calendars.models import User
from sync_calendars.extensions import db, login_manager, oauth

# Blueprint Configuration
auth_bp = Blueprint(
    'auth_bp', __name__
)

auth0 = oauth.register(
    'auth0',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

login_manager.login_view = "auth_bp.login"

@auth_bp.route('/login')
def login():
    """Initiate login with Auth0"""

    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home'))

    redirect_uri = url_for('auth_bp.callback', _external=True)

    return auth0.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/callback')
def callback():
    """Handle callback from Auth0"""

    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    user = auth0_to_app_user(resp.json())
    existing_user = User.query.filter_by(email=user.email).first()
    if existing_user is None:
        db.session.add(user)
    else:
        existing_user.last_login = datetime.utcnow()
        user = existing_user

    db.session.commit() # Save changes to database

    login_user(user)
    return redirect(url_for('main_bp.home'))



@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in upon page load."""
    if (user_id is not None) and (user_id != 'None'):
        return User.query.get(user_id)
    return None


def auth0_to_app_user(auth0_profile):
    """Extract relevant user properties from Auth0 profile"""
    print(auth0_profile)
    return User(
        name=auth0_profile['name'],
        email=auth0_profile['email']
    )
