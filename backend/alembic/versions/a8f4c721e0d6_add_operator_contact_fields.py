"""add phone/email contact fields to destination_operators

Revision ID: a8f4c721e0d6
Revises: c3f8a26d5e91
Create Date: 2026-09-02

"""
from alembic import op
import sqlalchemy as sa

revision = "a8f4c721e0d6"
down_revision = "c3f8a26d5e91"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("destination_operators", sa.Column("phone", sa.String(), nullable=True))
    op.add_column("destination_operators", sa.Column("email", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("destination_operators", "email")
    op.drop_column("destination_operators", "phone")
