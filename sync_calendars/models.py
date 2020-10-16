"""Database models."""
from datetime import datetime
from uuid import uuid4

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID

from sync_calendars import db

class User(UserMixin, db.Model):
    """User account model."""

    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class O365Token(db.Model):
    """O365 tokens model."""

    __tablename__ = 'o365_tokens'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_update_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
