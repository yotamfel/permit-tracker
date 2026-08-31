"""add source fetch failure tracking to destinations

Revision ID: f4a8d2e6c951
Revises: e2f5b9c1d374
Create Date: 2026-08-31 21:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f4a8d2e6c951'
down_revision: Union[str, None] = 'e2f5b9c1d374'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'destinations',
        sa.Column('source_fetch_failing', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column('destinations', sa.Column('source_fetch_error', sa.Text(), nullable=True))
    op.add_column('destinations', sa.Column('source_fetch_failing_since', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('destinations', 'source_fetch_failing_since')
    op.drop_column('destinations', 'source_fetch_error')
    op.drop_column('destinations', 'source_fetch_failing')
