"""generalize destination_research_reports into agent_reports

Renames the table and several columns so it can hold reports from any
pipeline agent (destination researcher+reviewer, visitor/tester,
site-wide UX reviewer), not just the destination research pipeline.
Existing rows are preserved and backfilled with agent_type
'destination_pipeline'.

Revision ID: c3f8a26d5e91
Revises: b7e2f4a91d3c
Create Date: 2026-09-02 09:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3f8a26d5e91'
down_revision: Union[str, None] = 'b7e2f4a91d3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('destination_research_reports', 'agent_reports')

    op.add_column('agent_reports', sa.Column('agent_type', sa.String(), nullable=True))
    op.execute("UPDATE agent_reports SET agent_type = 'destination_pipeline'")
    op.alter_column('agent_reports', 'agent_type', nullable=False)

    op.add_column('agent_reports', sa.Column('title', sa.String(), nullable=True))

    op.alter_column('agent_reports', 'destination_id', nullable=True)

    op.alter_column('agent_reports', 'researcher_summary', new_column_name='summary')
    op.alter_column('agent_reports', 'reviewer_summary', new_column_name='secondary_summary', nullable=True)

    op.drop_index('ix_destination_research_reports_destination_id', table_name='agent_reports')
    op.create_index('ix_agent_reports_destination_id', 'agent_reports', ['destination_id'])
    op.create_index('ix_agent_reports_agent_type', 'agent_reports', ['agent_type'])


def downgrade() -> None:
    op.drop_index('ix_agent_reports_agent_type', table_name='agent_reports')
    op.drop_index('ix_agent_reports_destination_id', table_name='agent_reports')
    op.create_index('ix_destination_research_reports_destination_id', 'agent_reports', ['destination_id'])

    op.alter_column('agent_reports', 'secondary_summary', new_column_name='reviewer_summary', nullable=False)
    op.alter_column('agent_reports', 'summary', new_column_name='researcher_summary')

    op.alter_column('agent_reports', 'destination_id', nullable=False)

    op.drop_column('agent_reports', 'title')
    op.drop_column('agent_reports', 'agent_type')

    op.rename_table('agent_reports', 'destination_research_reports')
