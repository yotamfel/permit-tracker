"""add post_release_feedback table

Revision ID: e2f5b9c1d374
Revises: d9e1a5c2f847
Create Date: 2026-08-31 21:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'e2f5b9c1d374'
down_revision: Union[str, None] = 'd9e1a5c2f847'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'post_release_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            'subscription_id', postgresql.UUID(as_uuid=True),
            sa.ForeignKey('alert_subscriptions.id', ondelete='CASCADE'), nullable=False,
        ),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column(
            'destination_id', postgresql.UUID(as_uuid=True),
            sa.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False,
        ),
        sa.Column('release_occurrence_date', sa.Date(), nullable=False),
        sa.Column('succeeded', sa.Boolean(), nullable=True),
        sa.Column('found_site_helpful', sa.Boolean(), nullable=True),
        sa.Column('free_text_comment', sa.Text(), nullable=True),
        sa.Column('email_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('response_token', sa.String(), nullable=False),
    )
    op.create_index('ix_post_release_feedback_subscription_id', 'post_release_feedback', ['subscription_id'])
    op.create_index('ix_post_release_feedback_destination_id', 'post_release_feedback', ['destination_id'])
    op.create_index('ix_post_release_feedback_response_token', 'post_release_feedback', ['response_token'], unique=True)


def downgrade() -> None:
    op.drop_table('post_release_feedback')
