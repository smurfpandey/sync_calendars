"""Routes for handling O365 connectivity"""
from datetime import datetime, timezone
from werkzeug.exceptions import BadRequest

from flask import request, Blueprint, url_for, session, make_response
from flask_login import current_user, login_required

from sync_calendars import db
from sync_calendars.integrations import O365Client
from sync_calendars.models import Calendar, CalendarEnum
from sync_calendars.tasks import calendar_tasks

# Blueprint Configuration
o365_bp = Blueprint(
    'o365_bp', __name__
)

o365_app = O365Client().app

@o365_bp.route('/o365/connect')
@login_required
def connect():
    """Initiate authentication request with Microsoft Office 365"""

    connect_type = request.args.get('type')
    connect_email = request.args.get('email')
    connect_scope = "offline_access User.Read"
    if connect_type.upper() == "SOURCE":
        connect_scope = connect_scope + " Calendars.Read"
    else:
        connect_scope = connect_scope + " Calendars.ReadWrite"

    if not connect_email:
        raise BadRequest()

    session['o365_connect_email'] = connect_email
    # MS needs scope for getting access tokens
    session['o365_connect_scope'] = connect_scope

    redirect_uri = url_for('o365_bp.callback', _external=True)

    return o365_app.authorize_redirect(
        redirect_uri,
        scope=connect_scope,
        prompt='select_account',
        login_hint=connect_email
    )


@o365_bp.route('/o365/callback')
@login_required
def callback():
    """Handle callback from O365"""

    session_scope = session['o365_connect_scope']
    token = o365_app.authorize_access_token(scope=session_scope)    
    # Make sure authentication user email matches
    user_info = o365_app.get('me').json()
    connect_email = session['o365_connect_email'].lower()

    if not user_info['userPrincipalName'].lower() == connect_email:
        print("Email mismatch")
        print(user_info)
        raise BadRequest()

    # save auth tokens in DB for later use
    # Q: What if user does not save the sync flow?
    o365_cal = Calendar(
        type=CalendarEnum.O365,
        email=connect_email,
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        expires_at=datetime.fromtimestamp(token['expires_at'], timezone.utc)
    )

    existing_cal = Calendar.query.filter_by(email=connect_email).first()
    if existing_cal is None:
        o365_cal.users.append(current_user)
        db.session.add(o365_cal)
    else:
        if not current_user in existing_cal.users:
            existing_cal.users.append(current_user)

        existing_cal.access_token = o365_cal.access_token
        existing_cal.refresh_token = o365_cal.refresh_token
        existing_cal.expires_at = o365_cal.expires_at
        existing_cal.last_update_at = datetime.utcnow()

    db.session.commit()

    return "Ok"

@o365_bp.route('/o365/change', methods=['POST'])
def change_notification():
    """Handle change notifications from O365"""
    validation_token = request.args.get('validationToken', '')
    if validation_token != '':
        return make_response(validation_token, 200)

    notification = request.get_json()
    
    for notif in notification['value']:
        calendar_tasks.handle_change_notification.delay(notif)

    return make_response('Ok', 202)
