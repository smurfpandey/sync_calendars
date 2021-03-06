"""empty message

Revision ID: 605af032c328
Revises: 
Create Date: 2021-05-16 17:09:44.853004

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '605af032c328'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('calendars',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('type', sa.Enum('O365', name='calendarenum'), nullable=True),
    sa.Column('email', sa.String(length=40), nullable=False),
    sa.Column('access_token', sa.Text(), nullable=False),
    sa.Column('refresh_token', sa.Text(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('last_update_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('subscription_id', sa.String(length=40), nullable=True),
    sa.Column('change_subscrition', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('subscription_id'),
    sa.UniqueConstraint('subscription_id')
    )
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=40), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('email')
    )
    op.create_table('event_map',
    sa.Column('source_cal', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('source_event', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('dest_cal', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('dest_event', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['dest_cal'], ['calendars.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['source_cal'], ['calendars.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('source_event', 'dest_event')
    )
    op.create_table('sync_flows',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('source', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('destination', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('user', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['destination'], ['calendars.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['source'], ['calendars.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_calendar',
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('calendar_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['calendar_id'], ['calendars.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_calendar')
    op.drop_table('sync_flows')
    op.drop_table('event_map')
    op.drop_table('users')
    op.drop_table('calendars')
    # ### end Alembic commands ###
