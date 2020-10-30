"""Database models."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID

from sync_calendars import db

user_cal_association = db.Table('user_calendar',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE')),
    db.Column('calendar_id', UUID(as_uuid=True), db.ForeignKey('calendars.id', ondelete='CASCADE'))
)

@dataclass
class User(UserMixin, db.Model):
    """User account model."""
    id: str
    email: str

    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    calendars = db.relationship('Calendar',
        secondary=user_cal_association,
        back_populates='users')

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

    __tablename__ = 'calendars'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    type = db.Column(db.Enum(CalendarEnum))
    email = db.Column(db.String(40), unique=True, nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_update_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User',
        secondary=user_cal_association,
        back_populates='calendars')

    def __repr__(self):
        return '<Calendar {}>'.format(self.email)

@dataclass
class SyncFlow(db.Model):
    """SyncFlow model"""
    id: str
    source: str
    destination: str
    user: str

    __tablename__ = 'sync_flows'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    source = db.Column(UUID(as_uuid=True), db.ForeignKey(Calendar.id, ondelete='CASCADE'))
    destination = db.Column(UUID(as_uuid=True), db.ForeignKey(Calendar.id, ondelete='CASCADE'))
    user = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id, ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<SyncFlow {}>'.format(self.id)