"""add watchlist_items table

Revision ID: e3f7a8b2c9d1
Revises: c1a9d4e6f2b8
Create Date: 2026-09-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'e3f7a8b2c9d1'
down_revision: Union[str, None] = 'c1a9d4e6f2b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'watchlist_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('destination_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'destination_id', name='uq_watchlist_items_user_destination'),
    )
    op.create_index('ix_watchlist_items_user_id', 'watchlist_items', ['user_id'])
    op.create_index('ix_watchlist_items_destination_id', 'watchlist_items', ['destination_id'])


def downgrade() -> None:
    op.drop_index('ix_watchlist_items_destination_id', table_name='watchlist_items')
    op.drop_index('ix_watchlist_items_user_id', table_name='watchlist_items')
    op.drop_table('watchlist_items')
