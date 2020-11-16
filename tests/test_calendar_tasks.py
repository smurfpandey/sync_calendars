"""Tests for calendar_tasks methods"""

from unittest.mock import patch

from sync_calendars.tasks.calendar_tasks import subscribe_to_calendar

# @patch('sync_calendars.tasks.calendar_tasks.O365Client.create_change_subscription')  # < patching Product in module above
def test_success():
    calendar = {
        'id': 'ABC'
    }
    subscribe_to_calendar(calendar)
    assert True == True
