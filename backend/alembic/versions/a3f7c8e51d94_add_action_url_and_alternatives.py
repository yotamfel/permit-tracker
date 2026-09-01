"""add action_url to destination_requirements and destination_alternatives table

Revision ID: a3f7c8e51d94
Revises: e8b34f2c9a17
Create Date: 2026-09-01 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a3f7c8e51d94'
down_revision: Union[str, None] = 'e8b34f2c9a17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('destination_requirements', sa.Column('action_url', sa.Text(), nullable=True))

    op.create_table(
        'destination_alternatives',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            'destination_id', postgresql.UUID(as_uuid=True),
            sa.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False,
        ),
        sa.Column(
            'alternative_destination_id', postgresql.UUID(as_uuid=True),
            sa.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False,
        ),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('note', sa.String(), nullable=True),
    )
    op.create_index('ix_destination_alternatives_destination_id', 'destination_alternatives', ['destination_id'])
    op.create_index(
        'ix_destination_alternatives_alternative_destination_id',
        'destination_alternatives', ['alternative_destination_id'],
    )


def downgrade() -> None:
    op.drop_table('destination_alternatives')
    op.drop_column('destination_requirements', 'action_url')
