"""Calendar related tasks"""

from sync_calendars import celery
from sync_calendars.integrations import O365Client
from sync_calendars.models import Calendar

@celery.task()
def initial_load(source_cal, destination_cal):
    """Do initial sync of copying all future events from source to destination"""
    return True

@celery.task()
def subscribe_to_calendar(calendar):
    """Subscribe to changes on O365 Calendar"""
    # 1. Check if we have a subscription already
    obj_cal = Calendar.query.get(calendar['id'])

    # 1.1 If subscription exists
    if obj_cal.subscription_id is not None:
        # 1.2 If subscription has not expired
        return True

    # 2. If not, subscribe
    o365_token = {
        'token_type': 'bearer',
        'access_token': obj_cal.access_token,
        'refresh_token': obj_cal.refresh_token,
        'expires_at': obj_cal.expires_at.timestamp()
    }
    o365_client = O365Client(token=o365_token)
    subscription = o365_client.create_change_subscription().json()
    
    if 'id' not in subscription:
        # We failed :(
        return False

    print(subscription)    
    # 3. Set schedule to renew?
    return True