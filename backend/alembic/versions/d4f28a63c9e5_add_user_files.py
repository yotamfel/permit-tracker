"""add user_files table

Revision ID: d4f28a63c9e5
Revises: c9a1d4f83b27
Create Date: 2026-09-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "d4f28a63c9e5"
down_revision = "c9a1d4f83b27"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("checklist_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("checklist_items.id", ondelete="CASCADE"), nullable=True),
        sa.Column("user_checklist_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_checklist_items.id", ondelete="CASCADE"), nullable=True),
    )
    op.create_index("ix_user_files_user_id", "user_files", ["user_id"])
    op.create_index("ix_user_files_checklist_item_id", "user_files", ["checklist_item_id"])
    op.create_index("ix_user_files_user_checklist_item_id", "user_files", ["user_checklist_item_id"])


def downgrade() -> None:
    op.drop_index("ix_user_files_user_checklist_item_id", table_name="user_files")
    op.drop_index("ix_user_files_checklist_item_id", table_name="user_files")
    op.drop_index("ix_user_files_user_id", table_name="user_files")
    op.drop_table("user_files")
