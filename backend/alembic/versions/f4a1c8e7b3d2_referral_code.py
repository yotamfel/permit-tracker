"""add referral_code and referral_discount_id to users

Revision ID: f4a1c8e7b3d2
Revises: e3f7a8b2c9d1
Create Date: 2026-09-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f4a1c8e7b3d2'
down_revision: Union[str, None] = 'e3f7a8b2c9d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('referral_code', sa.String(), nullable=True))
    op.add_column('users', sa.Column('referral_discount_id', sa.String(), nullable=True))
    op.create_unique_constraint('uq_users_referral_code', 'users', ['referral_code'])


def downgrade() -> None:
    op.drop_constraint('uq_users_referral_code', 'users', type_='unique')
    op.drop_column('users', 'referral_discount_id')
    op.drop_column('users', 'referral_code')
