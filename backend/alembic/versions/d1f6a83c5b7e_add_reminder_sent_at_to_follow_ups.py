"""add reminder_sent_at to admin_follow_ups

Revision ID: d1f6a83c5b7e
Revises: c7e29b4f1a63
Create Date: 2026-08-31 23:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1f6a83c5b7e'
down_revision: Union[str, None] = 'c7e29b4f1a63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('admin_follow_ups', sa.Column('reminder_sent_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('admin_follow_ups', 'reminder_sent_at')
