"""add contact_messages.destination_id (urgent, destination-linked messages)

Revision ID: a1c4e8f92b56
Revises: f18b6d92a4c7
Create Date: 2026-09-02 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a1c4e8f92b56'
down_revision: Union[str, None] = 'f18b6d92a4c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'contact_messages',
        sa.Column('destination_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('destinations.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index('ix_contact_messages_destination_id', 'contact_messages', ['destination_id'])


def downgrade() -> None:
    op.drop_index('ix_contact_messages_destination_id', table_name='contact_messages')
    op.drop_column('contact_messages', 'destination_id')
