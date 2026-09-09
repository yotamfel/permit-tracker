"""add recurring_lottery mechanism_type value

Revision ID: d2f8e6a91c53
Revises: d2c5e91a3f8d27
Create Date: 2026-09-09 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'd2f8e6a91c53'
down_revision: Union[str, None] = 'c5e91a3f8d27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE mechanism_type ADD VALUE IF NOT EXISTS 'recurring_lottery'")


def downgrade() -> None:
    # Postgres doesn't support removing enum values directly - additive only.
    pass
