"""add destination_research_reports table

Revision ID: f2c6a91e5d38
Revises: a3f7c8e51d94
Create Date: 2026-09-01 09:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'f2c6a91e5d38'
down_revision: Union[str, None] = 'a3f7c8e51d94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'destination_research_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            'destination_id', postgresql.UUID(as_uuid=True),
            sa.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False,
        ),
        sa.Column('researcher_summary', sa.Text(), nullable=False),
        sa.Column('reviewer_summary', sa.Text(), nullable=False),
        sa.Column('escalations', sa.Text(), nullable=True),
    )
    op.create_index('ix_destination_research_reports_destination_id', 'destination_research_reports', ['destination_id'])


def downgrade() -> None:
    op.drop_table('destination_research_reports')
