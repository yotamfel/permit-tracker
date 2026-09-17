"""alert_subscriptions: support multiple lead times per alert

Revision ID: a1b2c3d4e5f6
Revises: f4a1c8e7b3d2
Create Date: 2026-09-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f4a1c8e7b3d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'alert_subscriptions',
        sa.Column('lead_time_minutes_list', postgresql.ARRAY(sa.Integer()), nullable=True),
    )
    # Backfill: wrap each existing single value into a one-element array so
    # nobody's existing alert silently stops firing.
    op.execute(
        "UPDATE alert_subscriptions SET lead_time_minutes_list = ARRAY[lead_time_minutes] "
        "WHERE lead_time_minutes_list IS NULL"
    )
    op.alter_column('alert_subscriptions', 'lead_time_minutes_list', nullable=False)
    op.drop_column('alert_subscriptions', 'lead_time_minutes')

    # Dispatch needs to dedupe per (subscription, lead_time) now that one
    # subscription can fire several alerts against the same release moment -
    # nullable since historical rows predate this and can be left ambiguous.
    op.add_column('notification_log', sa.Column('lead_time_minutes', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('notification_log', 'lead_time_minutes')

    op.add_column('alert_subscriptions', sa.Column('lead_time_minutes', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE alert_subscriptions SET lead_time_minutes = lead_time_minutes_list[1] "
        "WHERE lead_time_minutes IS NULL"
    )
    op.alter_column('alert_subscriptions', 'lead_time_minutes', nullable=False)
    op.drop_column('alert_subscriptions', 'lead_time_minutes_list')
