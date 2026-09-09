"""dedupe and add unique constraint on alert_subscriptions(user_id, destination_id)

A double-submit race on "Set alert" (first click sends only an OPTIONS
preflight with no follow-up POST, second click succeeds - documented by the
visitor-tester agent) could create two byte-identical subscription rows for
the same user+destination, e.g. Three Capes Track. This migration removes
existing duplicates (keeping the oldest row per user+destination) and adds a
unique constraint so it can't recur; the API now upserts instead of always
inserting.

Revision ID: b3f7a291c6d4
Revises: a9d2e7c14f68
Create Date: 2026-09-09 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b3f7a291c6d4'
down_revision: Union[str, None] = 'a9d2e7c14f68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM alert_subscriptions a
        USING alert_subscriptions b
        WHERE a.user_id = b.user_id
          AND a.destination_id = b.destination_id
          AND a.created_at > b.created_at
        """
    )
    op.create_unique_constraint(
        "uq_alert_subscriptions_user_destination", "alert_subscriptions", ["user_id", "destination_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_alert_subscriptions_user_destination", "alert_subscriptions", type_="unique")
