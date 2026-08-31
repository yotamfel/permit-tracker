"""add admin_follow_ups table

Revision ID: c7e29b4f1a63
Revises: b6c3f18a7d02
Create Date: 2026-08-31 22:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'c7e29b4f1a63'
down_revision: Union[str, None] = 'b6c3f18a7d02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'admin_follow_ups',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            'destination_id', postgresql.UUID(as_uuid=True),
            sa.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False,
        ),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_done', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index('ix_admin_follow_ups_destination_id', 'admin_follow_ups', ['destination_id'])
    op.create_index('ix_admin_follow_ups_due_date', 'admin_follow_ups', ['due_date'])


def downgrade() -> None:
    op.drop_table('admin_follow_ups')
