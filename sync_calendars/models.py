"""Database models."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from sync_calendars import db

@dataclass
class User(UserMixin, db.Model):
    """User account model."""

    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    calendars = relationship('Calendar', back_populates='user')

    def __repr__(self):
        return '<User {}>'.format(self.username)

@dataclass
class CalendarEnum(str, Enum):
    """Enum defining what calendars app supports"""
    O365 = 'o365'

    def __hash__(self):
        return hash(self.value)

@dataclass
class Calendar(db.Model):
    """Email account model."""
    id: str
    email: str
    type: str
    user_id: str

    __tablename__ = 'calendars'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    type = db.Column(db.Enum(CalendarEnum))
    email = db.Column(db.String(40), unique=True, nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_update_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    user = relationship('User', back_populates='calendars')

    def __repr__(self):
        return '<Calendar {}>'.format(self.email)
