"""switch payment provider from Stripe to Paddle

No real purchase has ever gone through Stripe (checkout was never
launched with it), so a straight column rename is safe - no data
migration needed. Also adds users.paddle_customer_id, a cache of each
user's Paddle customer id so checkout doesn't need a get-or-create-by-email
round trip to Paddle on every purchase.

Revision ID: c1a9d4e6f2b8
Revises: b8e4f27a91d6
Create Date: 2026-09-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1a9d4e6f2b8'
down_revision: Union[str, None] = 'b8e4f27a91d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'purchases', 'stripe_payment_intent_id', new_column_name='paddle_transaction_id',
    )
    op.add_column('users', sa.Column('paddle_customer_id', sa.String(), nullable=True))
    op.create_unique_constraint('uq_users_paddle_customer_id', 'users', ['paddle_customer_id'])


def downgrade() -> None:
    op.drop_constraint('uq_users_paddle_customer_id', 'users', type_='unique')
    op.drop_column('users', 'paddle_customer_id')
    op.alter_column(
        'purchases', 'paddle_transaction_id', new_column_name='stripe_payment_intent_id',
    )
