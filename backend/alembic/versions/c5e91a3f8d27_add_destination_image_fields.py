"""add destinations image_url/image_credit_name/image_credit_url/image_license

Revision ID: c5e91a3f8d27
Revises: b3f7a291c6d4
Create Date: 2026-09-09 00:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c5e91a3f8d27'
down_revision: Union[str, None] = 'b3f7a291c6d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('destinations', sa.Column('image_url', sa.Text(), nullable=True))
    op.add_column('destinations', sa.Column('image_credit_name', sa.Text(), nullable=True))
    op.add_column('destinations', sa.Column('image_credit_url', sa.Text(), nullable=True))
    op.add_column('destinations', sa.Column('image_license', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('destinations', 'image_license')
    op.drop_column('destinations', 'image_credit_url')
    op.drop_column('destinations', 'image_credit_name')
    op.drop_column('destinations', 'image_url')
