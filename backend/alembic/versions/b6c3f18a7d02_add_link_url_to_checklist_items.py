"""add link_url to checklist_items

Revision ID: b6c3f18a7d02
Revises: f4a8d2e6c951
Create Date: 2026-08-31 22:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b6c3f18a7d02'
down_revision: Union[str, None] = 'f4a8d2e6c951'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('checklist_items', sa.Column('link_url', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('checklist_items', 'link_url')
