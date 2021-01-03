"""Calendar related tasks"""
from datetime import datetime

from celery.utils.log import get_task_logger

from sync_calendars import celery, db
from sync_calendars.integrations import O365Client
from sync_calendars.models import Calendar, SyncFlow, EventMap

logger = get_task_logger(__name__)

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
        logger.info('Subscription already exists for calendar %s', obj_cal.id)
        expiry_date = obj_cal.change_subscrition['expirationDateTime']
        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M:%S.%fZ')
        now_date = datetime.utcnow()
        
        if expiry_date < now_date:
            # 1.3. Renew subscription
            return True

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
        logger.error('Failed to subscribe. ', extra=subscription['error'])
        return False
    
    # 2.1. Save in DB
    obj_cal.subscription_id = subscription['id']
    obj_cal.change_subscrition = subscription
    obj_cal.last_update_at = datetime.utcnow()

    db.session.commit()

    # 3. Set schedule to renew?

    o365_client.close()
    return True

@celery.task()
def handle_change_notification(notification):
    """Process individual notification from O365"""

    subscription_id = notification['subscriptionId']
    change_type = notification['changeType'].lower()
    event_id = notification['resourceData']['id']
    
    # 1. Find Calendar of this subscription
    this_cal = Calendar.query.filter_by(subscription_id=subscription_id).first()
    if this_cal is None:
        logger.warn('No calendar found for subscription id %s', subscription_id)
        return True

    # TODO: Verify client state

    source_o365_token = {
        'token_type': 'bearer',
        'access_token': this_cal.access_token,
        'refresh_token': this_cal.refresh_token,
        'expires_at': this_cal.expires_at.timestamp()
    }
    source_o365_client = O365Client(token=source_o365_token)
    
    # 2. Get all destinations for this Calendar
    sync_destinations = SyncFlow.query.with_entities(SyncFlow.destination).filter_by(source=this_cal.id)

    # 3. Replicate the change to all destinations
    
    # 3.3 Delete
    if change_type == 'deleted':        
        return handle_event_delete(event_id, sync_destinations)

    # Get Event
    event_resp = source_o365_client.get_calendar_event(event_id)
    o365_event = event_resp.json()

    if event_resp.status_code == 404:
        # Event has been deleted
        return handle_event_delete(event_id, sync_destinations)
    
    if event_resp.status_code is not 200:
        logger.error('Error getting calendar event details: %s', o365_event['error']['code'])
        return False

    # 3.1 Create
    if change_type == 'created':        
        # Create a copy in all destinations
        return handle_event_created(this_cal, o365_event, sync_destinations)        

    # 3.2 Update
    if change_type == 'updated':
        # Update all events with new details
        return True

    
    # Unknown event
    return True
    
    
def handle_event_delete(event_id, destinations):
    """Handle event deleted notification"""
    # Find all duplicated events
    # Delete them all
    
    return False

def handle_event_created(source_cal, event, destinations):
    """Handle event created notification"""
    for record in destinations:
        dest_cal = record.destination
        try:
            copy_event = {
                'subject': f"Sync Calendar :: {event['subject']}",
                'start': event['start'],
                'end': event['end'],
                'body': {
                    'contentType': "html",
                    'content': f'Event copied by Sync Calendars app. Source Calendar: {source_cal.email}'
                }
            }
            dest_o365_client = O365Client(calendar=dest_cal)

            event_resp = dest_o365_client.create_calendar_event(copy_event)
            dest_event = event_resp.json()
            
            if 'id' not in dest_event:
                # We failed :(
                logger.error('Failed to create o365 event. ', extra=dest_event['error'])
                continue

            # Save in DB
            event_map = EventMap(
                source_cal=source_cal,
                source_event=event['id'],
                dest_cal=dest_cal,
                dest_event=dest_event['id'],
            )

            db.session.add(event_map)

        except Exception as ex:
            logger.exception('Error creating duplicate event', exc_info=ex)
            return False

    db.session.commit()
    return True
        