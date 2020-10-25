"""Routes for API"""
from flask import Blueprint, jsonify, make_response, request
from flask_login import current_user, login_required

from sync_calendars.models import Calendar

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
    cal = Calendar.query.filter_by(email=email, user_id=current_user.id).first()
    if cal is None:
        return custom_error("", 404)
    
    req_type = request.args.get('type')
    if req_type == 'check':
        return make_response('', 204)

    return jsonify(cal), 200
