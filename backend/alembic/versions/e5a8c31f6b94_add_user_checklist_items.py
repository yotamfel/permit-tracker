"""add user_checklist_items table

Revision ID: e5a8c31f6b94
Revises: c94f1a7e3d05
Create Date: 2026-09-01 18:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'e5a8c31f6b94'
down_revision: Union[str, None] = 'c94f1a7e3d05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_checklist_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'destination_id', postgresql.UUID(as_uuid=True),
            sa.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False,
        ),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_user_checklist_items_user_id', 'user_checklist_items', ['user_id'])
    op.create_index('ix_user_checklist_items_destination_id', 'user_checklist_items', ['destination_id'])


def downgrade() -> None:
    op.drop_table('user_checklist_items')
