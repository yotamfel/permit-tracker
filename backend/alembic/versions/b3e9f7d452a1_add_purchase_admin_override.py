"""add admin override fields to purchases

Revision ID: b3e9f7d452a1
Revises: a8f4c721e0d6
Create Date: 2026-09-02

"""
from alembic import op
import sqlalchemy as sa

revision = "b3e9f7d452a1"
down_revision = "a8f4c721e0d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("purchases", sa.Column("admin_override_until", sa.DateTime(timezone=True), nullable=True))
    op.add_column("purchases", sa.Column("admin_override_note", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("purchases", "admin_override_note")
    op.drop_column("purchases", "admin_override_until")
