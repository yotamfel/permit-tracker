"""allow user file attachments to target a destination_requirement row

Revision ID: b8e4f27a91d6
Revises: d2f8e6a91c53
Create Date: 2026-09-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b8e4f27a91d6'
down_revision: Union[str, None] = 'd2f8e6a91c53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user_file_attachments',
        sa.Column('destination_requirement_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        'ix_user_file_attachments_destination_requirement_id',
        'user_file_attachments', ['destination_requirement_id'],
    )
    op.create_foreign_key(
        'fk_user_file_attachments_destination_requirement_id',
        'user_file_attachments', 'destination_requirements',
        ['destination_requirement_id'], ['id'], ondelete='CASCADE',
    )


def downgrade() -> None:
    op.drop_constraint('fk_user_file_attachments_destination_requirement_id', 'user_file_attachments', type_='foreignkey')
    op.drop_index('ix_user_file_attachments_destination_requirement_id', table_name='user_file_attachments')
    op.drop_column('user_file_attachments', 'destination_requirement_id')
