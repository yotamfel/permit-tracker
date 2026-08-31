"""add endurance_event category value

Revision ID: d9e1a5c2f847
Revises: c3d84f6b7a29
Create Date: 2026-08-31 20:35:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'd9e1a5c2f847'
down_revision: Union[str, None] = 'c3d84f6b7a29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE cannot run inside a transaction block on some
    # Postgres versions/setups, so run it in its own autocommit block.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE category ADD VALUE IF NOT EXISTS 'endurance_event'")


def downgrade() -> None:
    # Postgres doesn't support removing enum values directly. Since this is
    # additive and downgrades of this project are not exercised in practice,
    # intentionally a no-op rather than the usual rebuild-the-type dance.
    pass
