"""Routes for API"""
from flask import Blueprint, jsonify, make_response, request
from flask_login import current_user, login_required

from sync_calendars.extensions import db
from sync_calendars.models import Calendar, User, SyncFlow
from sync_calendars.tasks import calendar_tasks

# Blueprint Configuration
api_bp = Blueprint(
    'api_bp', __name__,
    url_prefix='/api'
)


def custom_error(message, status_code):
    """Method to throw RESTful errors"""
    return make_response(jsonify(message), status_code)


@api_bp.route('/emails/<email>', methods=['GET'])
@login_required
def get_email_for_user(email):
    """Get email if mapped to this user"""
    email = email.lower()
    cal = Calendar.query.join(Calendar.users).filter(
        Calendar.email == email,
        User.id == current_user.id
    ).first()

    if cal is None:
        return custom_error("", 404)

    req_type = request.args.get('type')
    if req_type == 'check':
        return make_response('', 204)

    return jsonify(cal), 200


@ api_bp.route('/syncs', methods=['POST'])
@ login_required
def save_sync_for_user():
    """Create a new sync flow for the user"""
    req_data = request.json

    # 1. Make sure this user has authorised access to source & email
    source_email = req_data['source_cal']
    dest_email = req_data['dest_cal']

    source_cal = Calendar.query.join(Calendar.users).filter(
        Calendar.email == source_email,
        User.id == current_user.id
    ).first()

    dest_cal = Calendar.query.join(Calendar.users).filter(
        Calendar.email == dest_email,
        User.id == current_user.id
    ).first()

    if source_cal is None:
        return custom_error({
            'status': 'SOURCE_NONE',
            'message': "Authorisation missing for source calendar"}, 400)

    if dest_cal is None:
        return custom_error({
            'status': 'DEST_NONE',
            'message': "Authorisation not done for destination calendar"}, 400)

    # 2. Save the Sync Flow
    sync_flow = SyncFlow(
        source=source_cal.id,
        destination=dest_cal.id,
        user=current_user.id
    )

    # 2.1 Make sure this sync is not a duplicate
    existing_flow = SyncFlow.query.filter_by(
        source=source_cal.id, destination=dest_cal.id, user=current_user.id
    ).first()
    if existing_flow is not None:
        return custom_error({
            'status': 'SYNC_DUPLICATE',
            'message': "It seems you already have a sync with same configuration"}, 400)

    db.session.add(sync_flow)
    db.session.commit()

    # 3. Create "work": Start Sync
    # 3.1. Subscribe to get notifications from source calendar
    calendar_tasks.subscribe_to_calendar.delay(source_cal.to_simple_obj())
    # 3.2. Update destination with all future events from source
    calendar_tasks.initial_load.delay(
        source_cal.to_simple_obj(), dest_cal.to_simple_obj())

    # 4. Tada!
    return make_response('Ok', 201)
