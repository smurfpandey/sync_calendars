"""Calendar related tasks"""

from sync_calendars import celery

@celery.task()
def initial_load(source_cal, destination_cal):
    """Do initial sync of copying all future events from source to destination"""
    return True

@celery.task()
def subscribe_to_calendar(calendar):
    """Subscribe to changes on O365 Calendar"""
    # 1. Check if we have a subscription already
    # 2. If not, subscribe
    # 3. Set schedule to renew?
    return True