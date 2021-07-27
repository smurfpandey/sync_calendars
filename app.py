# -*- coding: utf-8 -*-
"""Application entry point."""
from sync_calendars.app import create_app, celery

app = create_app()
