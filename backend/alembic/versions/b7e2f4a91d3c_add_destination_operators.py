"""add destination_operators table

Revision ID: b7e2f4a91d3c
Revises: a1c4e8f92b56
Create Date: 2026-09-02 09:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b7e2f4a91d3c'
down_revision: Union[str, None] = 'a1c4e8f92b56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'destination_operators',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            'destination_id', postgresql.UUID(as_uuid=True),
            sa.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False,
        ),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_destination_operators_destination_id', 'destination_operators', ['destination_id'])


def downgrade() -> None:
    op.drop_table('destination_operators')
