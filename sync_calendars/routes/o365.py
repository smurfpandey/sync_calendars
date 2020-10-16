"""Routes for handling O365 connectivity"""
from datetime import datetime, timedelta
from werkzeug.exceptions import BadRequest

from flask import redirect, request, Blueprint, url_for, current_app, session

from sync_calendars import db, oauth
from sync_calendars.models import O365Token

# Blueprint Configuration
o365_bp = Blueprint(
    'o365_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

o365_app = oauth.register(
    'o365'
)

@o365_bp.route("/o365/connect")
def connect():
    """Initiate authentication request with Microsoft Office 365"""

    connect_type = request.args.get('type')
    connect_email = request.args.get('email')
    connect_scope = "offline_access User.Read"
    if connect_type == "SOURCE":
        connect_scope = connect_scope + " Calendars.Read"
    else:
        connect_scope = connect_scope + " Calendars.ReadWrite"

    if not connect_email:
        raise BadRequest()

    session['o365_connect_email'] = connect_email
    session['o365_connect_scope'] = connect_scope # MS requires scope for exchanging auth code for tokens

    redirect_uri = url_for('o365_bp.callback', _external=True)

    return o365_app.authorize_redirect(redirect_uri, scope=connect_scope, response_type='code')

@o365_bp.route("/o365/callback")
def callback():
    """Handle callback from O365"""

    session_scope = session['o365_connect_scope']
    token = o365_app.authorize_access_token(scope=session_scope)
    print(token)
    # Make sure authentication user email matches
    user_info = o365_app.get('me').json()
    connect_email = session['o365_connect_email']

    if not user_info['userPrincipalName'] == connect_email:
        raise BadRequest()

    # save auth tokens in DB for later use
    # Q: What if user does not save the sync flow?
    o365_token = O365Token(
        email=connect_email,
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        expires_at = datetime.fromtimestamp(token['expires_at'])
    )

    existing_token = O365Token.query.filter_by(email=connect_email).first()
    if existing_token is None:
        db.session.add(o365_token)
    else:
        existing_token.access_token = o365_token.access_token
        existing_token.refresh_token = o365_token.refresh_token
        existing_token.expires_at = o365_token.expires_at
        existing_token.last_update_at = datetime.utcnow()

    db.session.commit()

    return "Ok"
