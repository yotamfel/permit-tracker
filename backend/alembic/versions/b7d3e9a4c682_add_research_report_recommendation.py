"""add destination_research_reports.recommendation

Revision ID: b7d3e9a4c682
Revises: f2c6a91e5d38
Create Date: 2026-09-01 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7d3e9a4c682'
down_revision: Union[str, None] = 'f2c6a91e5d38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('destination_research_reports', sa.Column('recommendation', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('destination_research_reports', 'recommendation')
