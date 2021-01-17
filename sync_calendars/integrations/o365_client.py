"""Client for accessing O365"""
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from authlib.integrations.requests_client import OAuth2Session
from flask import current_app

from sync_calendars.extensions import db, oauth
from sync_calendars.models import Calendar, CalendarEnum


class O365Client:
    """ O365 client class"""

    def __init__(self, token=None, email=None, calendar=None):
        """Contstructor"""
        if token is not None:
            self.app = self.__init_with_token(token)
        elif email is not None:
            self.__init_with_email(email)
        elif calendar is not None:
            self.__init_with_calendar(calendar)
        else:
            self.app = oauth.register(
                'o365',
                update_token=self.__update_token
            )

    def __init_with_token(self, token):
        client_id = current_app.config['O365_CLIENT_ID']
        client_secret = current_app.config['O365_CLIENT_SECRET']
        token_endpoint = current_app.config['O365_ACCESS_TOKEN_URL']
        self.api_base_url = current_app.config['O365_API_BASE_URL']

        return OAuth2Session(client_id=client_id,
                             client_secret=client_secret,
                             token_endpoint=token_endpoint,
                             token=token,
                             update_token=self.__update_token)

    def __init_with_email(self, email):
        """Initialize O365 client by finding tokens in DB"""
        cal = Calendar.query.filter_by(email=email).first()

        if cal is None:
            return

        token = {
            'access_token': cal.access_token,
            'refresh_token': cal.refresh_token,
            'token_type': 'bearer',
            'expires_at': cal.expires_at.timestamp()
        }
        self.app = self.__init_with_token(token)

    def __init_with_calendar(self, cal_id):
        """Initialize O365 client by finding tokens in DB"""
        cal = Calendar.query.get(cal_id)

        if cal is None:
            return

        token = {
            'access_token': cal.access_token,
            'refresh_token': cal.refresh_token,
            'token_type': 'bearer',
            'expires_at': cal.expires_at.timestamp()
        }
        self.app = self.__init_with_token(token)

    def __update_token(name, token, refresh_token=None, access_token=None):
        """Method to update token in db on refresh"""
        if refresh_token:
            # TODO: Find a better way to handle multiple calendar types
            item = Calendar.query.filter_by(
                type=CalendarEnum.O365, refresh_token=refresh_token).first()
        elif access_token:
            # TODO: Find a better way to handle multiple calendar types
            item = Calendar.query.filter_by(
                type=CalendarEnum.O365, access_token=access_token).first()
        else:
            return

        if item is None:
            return

        # update token
        item.access_token = token['access_token']
        item.refresh_token = token['refresh_token']
        item.expires_at = datetime.fromtimestamp(
            token['expires_at'], timezone.utc)
        item.last_update_at = datetime.utcnow()

        db.session.commit()

    def close(self):
        """Method to close a oauth2session object"""
        self.app.close()

    def create_change_subscription(self):
        """Method to create change subscription"""
        notification_url = current_app.config['APP_HOSTNAME'] + '/o365/change'
        expiration = datetime.utcnow() + timedelta(minutes=4230)
        req_data = {
            'changeType': 'created,updated,deleted',
            'notificationUrl': notification_url,
            'lifecycleNotificationUrl': notification_url,
            'resource': 'me/events',
            'expirationDateTime': expiration.isoformat() + "Z",
            'clientState': str(uuid4())
        }
        req_headers = {
            'Prefer': 'IdType="ImmutableId"'
        }
        req_url = self.api_base_url + 'subscriptions'
        return self.app.post(req_url, json=req_data, headers=req_headers)

    def get_calendar_event(self, event_id):
        """Method to retrieve event details"""

        req_url = self.api_base_url + f'me/events/{event_id}'
        req_headers = {
            'Prefer': 'IdType="ImmutableId"'
        }
        return self.app.get(req_url, headers=req_headers)

    def create_calendar_event(self, event):
        """Method to create a new calendar event"""

        req_url = self.api_base_url + 'me/events'
        req_headers = {
            'Prefer': 'IdType="ImmutableId"'
        }
        return self.app.post(req_url, json=event, headers=req_headers)

    def delete_calendar_event(self, event_id):
        """Method to delete a calendar event"""

        req_url = self.api_base_url + f'me/events/{event_id}'
        return self.app.delete(req_url)

    def update_calendar_event(self, event_id, event_obj):
        """Method for updating a calendar event"""

        req_url = self.api_base_url + f'me/events/{event_id}'
        req_headers = {
            'Prefer': 'IdType="ImmutableId"'
        }
        return self.app.patch(req_url, json=event_obj, headers=req_headers)
