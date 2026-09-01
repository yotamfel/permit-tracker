"""add users.terms_accepted_at and terms_version

Revision ID: c94f1a7e3d05
Revises: b7d3e9a4c682
Create Date: 2026-09-01 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c94f1a7e3d05'
down_revision: Union[str, None] = 'b7d3e9a4c682'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('terms_accepted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('terms_version', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'terms_version')
    op.drop_column('users', 'terms_accepted_at')
