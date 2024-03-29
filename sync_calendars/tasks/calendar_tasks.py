"""Calendar related tasks"""
from datetime import datetime, timedelta

from celery.utils.log import get_task_logger

from sync_calendars.extensions import celery, db
from sync_calendars.integrations import O365Client
from sync_calendars.models import Calendar, SyncFlow, EventMap

logger = get_task_logger(__name__)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
        Schedule periodic tasks
    """
    # Resubsribe to notifications about to expire
    sender.add_periodic_task(timedelta(hours=12), resubscribe_calendars.s(), name='Resubscribe calendar change notification every 12hrs')


@celery.task()
def initial_load(source_cal, destination_cal):
    """Do initial sync of copying all future events from source to destination"""
    return True

@celery.task()
def subscribe_to_calendar(calendar):
    """Subscribe to changes on O365 Calendar"""

    logger.info('START:: task execution subscribe_to_calendar(%s)', calendar['id'])

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
    # TODO: Set future task to renew subscription

    o365_client.close()

    logger.info('END:: task execution subscribe_to_calendar(%s)', calendar['id'])

    return True

@celery.task()
def resubscribe_calendars():
    expected_expiry = datetime.utcnow() + timedelta(hours=13)
    # Get All Calendar Subscriptions
    all_calendars = Calendar.query.filter(Calendar.subscription_id.isnot(None)).all()

    for calendar in all_calendars:
        expiry_date = calendar.change_subscrition['expirationDateTime']
        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M:%S.%fZ')

        if expiry_date < expected_expiry:
            logger.info("Calendar subscription expiring soon. Going to renew.")
            return True
        else:
            logger.info('Calendar expiry in future. No need to renew')

@celery.task()
def handle_change_notification(notification):
    """Process individual notification from O365"""

    subscription_id = notification['subscriptionId']
    change_type = notification['changeType'].lower()
    event_id = notification['resourceData']['id']

    # 1. Find Calendar of this subscription
    this_cal = Calendar.query.filter_by(
        subscription_id=subscription_id).first()
    if this_cal is None:
        logger.warning('No calendar found for subscription id %s',
                    subscription_id)
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
    sync_destinations = SyncFlow.query.with_entities(SyncFlow.destination) \
        .filter_by(source=this_cal.id)

    # 3. Replicate the change to all destinations

    # 3.3 Delete
    if change_type == 'deleted':
        return handle_event_delete(event_id)

    # Get Event
    event_resp = source_o365_client.get_calendar_event(event_id)
    o365_event = event_resp.json()

    if event_resp.status_code == 404:
        # Event has been deleted
        return handle_event_delete(event_id)

    if event_resp.status_code != 200:
        logger.error('Error getting calendar event details: %s',
                     o365_event['error']['code'])
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


def handle_event_delete(event_id):
    """Handle event deleted notification"""
    # Find all duplicated events
    # Delete them all

    copied_events = EventMap.query.filter_by(source_event=event_id)

    for record in copied_events:
        dest_cal = record.dest_cal
        try:
            dest_o365_client = O365Client(calendar=dest_cal)

            event_resp = dest_o365_client.delete_calendar_event(
                record.dest_event)
            if event_resp.status_code != 204:
                # Event deletion failed
                logger.error('Failed to delete o365 event. ',
                             extra=event_resp['error'])
                continue

            record.is_deleted = True
        except Exception as ex:
            logger.exception(
                'Error propagating delete notification', exc_info=ex)
            continue

    db.session.commit()
    return True


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
                    'content': f'Event copied by Sync Calendars app. Source Calendar: {source_cal.email}'   # pylint: disable=line-too-long
                }
            }
            dest_o365_client = O365Client(calendar=dest_cal)

            event_resp = dest_o365_client.create_calendar_event(copy_event)
            dest_event = event_resp.json()

            if 'id' not in dest_event:
                # We failed :(
                logger.error('Failed to create o365 event. ',
                             extra=dest_event['error'])
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
            continue

    db.session.commit()
    return True


def handle_event_updated(source_cal, event):
    """Handle event created notification"""
    copied_events = EventMap.query.filter_by(source_event=event['id'])

    for record in copied_events:
        dest_cal = record.dest_cal
        try:
            dest_o365_client = O365Client(calendar=dest_cal)

            copy_event = {
                'subject': f"Sync Calendar :: {event['subject']}",
                'start': event['start'],
                'end': event['end'],
                'body': {
                    'contentType': "html",
                    'content': f'Event copied by Sync Calendars app. Source Calendar: {source_cal.email}'   # pylint: disable=line-too-long
                }
            }

            event_resp = dest_o365_client.update_calendar_event(
                event_id=record.dest_event,
                event_obj=copy_event
            )
            dest_event = event_resp.json()

            if 'id' not in dest_event:
                # We failed :(
                logger.error('Failed to create o365 event. ',
                             extra=dest_event['error'])

        except Exception as ex:
            logger.exception('Error updating duplicate event', exc_info=ex)
            continue

    db.session.commit()
    return True
