"""add research_notes to destinations

Revision ID: b7f21c9a4e13
Revises: ae500aba0c3f
Create Date: 2026-08-31 19:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7f21c9a4e13'
down_revision: Union[str, None] = 'ae500aba0c3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('destinations', sa.Column('research_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('destinations', 'research_notes')
