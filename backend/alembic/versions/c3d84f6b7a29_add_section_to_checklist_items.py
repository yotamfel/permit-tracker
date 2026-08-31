"""add section to checklist_items

Revision ID: c3d84f6b7a29
Revises: b7f21c9a4e13
Create Date: 2026-08-31 20:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d84f6b7a29'
down_revision: Union[str, None] = 'b7f21c9a4e13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    checklist_item_section = sa.Enum('specific', 'good_to_know', name='checklist_item_section')
    checklist_item_section.create(op.get_bind())
    op.add_column(
        'checklist_items',
        sa.Column('section', checklist_item_section, nullable=False, server_default='specific'),
    )


def downgrade() -> None:
    op.drop_column('checklist_items', 'section')
    sa.Enum(name='checklist_item_section').drop(op.get_bind())
