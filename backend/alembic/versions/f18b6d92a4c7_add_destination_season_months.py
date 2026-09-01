"""add destinations.season_start_month / season_end_month

Revision ID: f18b6d92a4c7
Revises: e5a8c31f6b94
Create Date: 2026-09-01 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f18b6d92a4c7'
down_revision: Union[str, None] = 'e5a8c31f6b94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('destinations', sa.Column('season_start_month', sa.Integer(), nullable=True))
    op.add_column('destinations', sa.Column('season_end_month', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('destinations', 'season_end_month')
    op.drop_column('destinations', 'season_start_month')
