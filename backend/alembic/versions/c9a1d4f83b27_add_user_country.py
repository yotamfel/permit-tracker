"""add country to users

Revision ID: c9a1d4f83b27
Revises: b3e9f7d452a1
Create Date: 2026-09-02

"""
from alembic import op
import sqlalchemy as sa

revision = "c9a1d4f83b27"
down_revision = "b3e9f7d452a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("country", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "country")
