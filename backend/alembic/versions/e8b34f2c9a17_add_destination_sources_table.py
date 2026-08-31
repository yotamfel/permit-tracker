"""add destination_sources table, migrate and drop research_notes

Revision ID: e8b34f2c9a17
Revises: d1f6a83c5b7e
Create Date: 2026-08-31 23:35:00.000000

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'e8b34f2c9a17'
down_revision: Union[str, None] = 'd1f6a83c5b7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'destination_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            'destination_id', postgresql.UUID(as_uuid=True),
            sa.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False,
        ),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
    )
    op.create_index('ix_destination_sources_destination_id', 'destination_sources', ['destination_id'])

    # Best-effort migration: any existing research_notes blob becomes a single
    # source row (whole blob as note, no url) rather than losing the content -
    # admins can split it into proper separate rows afterward as needed.
    connection = op.get_bind()
    rows = connection.execute(
        sa.text("SELECT id, research_notes FROM destinations WHERE research_notes IS NOT NULL")
    ).fetchall()
    for destination_id, research_notes in rows:
        connection.execute(
            sa.text(
                "INSERT INTO destination_sources (id, destination_id, order_index, url, note, created_at, updated_at) "
                "VALUES (:id, :destination_id, 0, NULL, :note, now(), now())"
            ),
            {"id": str(uuid.uuid4()), "destination_id": destination_id, "note": research_notes},
        )

    op.drop_column('destinations', 'research_notes')


def downgrade() -> None:
    op.add_column('destinations', sa.Column('research_notes', sa.Text(), nullable=True))
    op.drop_table('destination_sources')
