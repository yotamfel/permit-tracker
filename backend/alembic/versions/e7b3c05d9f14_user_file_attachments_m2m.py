"""replace user_files direct attachment FKs with a many-to-many table

Revision ID: e7b3c05d9f14
Revises: d4f28a63c9e5
Create Date: 2026-09-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "e7b3c05d9f14"
down_revision = "d4f28a63c9e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_file_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("file_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_files.id", ondelete="CASCADE"), nullable=False),
        sa.Column("checklist_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("checklist_items.id", ondelete="CASCADE"), nullable=True),
        sa.Column("user_checklist_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_checklist_items.id", ondelete="CASCADE"), nullable=True),
    )
    op.create_index("ix_user_file_attachments_file_id", "user_file_attachments", ["file_id"])
    op.create_index("ix_user_file_attachments_checklist_item_id", "user_file_attachments", ["checklist_item_id"])
    op.create_index("ix_user_file_attachments_user_checklist_item_id", "user_file_attachments", ["user_checklist_item_id"])

    # No production data yet in user_files at the time of this migration
    # (feature just shipped) - dropping these columns outright rather than
    # migrating rows into the new table.
    op.drop_index("ix_user_files_user_checklist_item_id", table_name="user_files")
    op.drop_index("ix_user_files_checklist_item_id", table_name="user_files")
    op.drop_column("user_files", "user_checklist_item_id")
    op.drop_column("user_files", "checklist_item_id")


def downgrade() -> None:
    op.add_column("user_files", sa.Column("checklist_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("checklist_items.id", ondelete="CASCADE"), nullable=True))
    op.add_column("user_files", sa.Column("user_checklist_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_checklist_items.id", ondelete="CASCADE"), nullable=True))
    op.create_index("ix_user_files_checklist_item_id", "user_files", ["checklist_item_id"])
    op.create_index("ix_user_files_user_checklist_item_id", "user_files", ["user_checklist_item_id"])
    op.drop_table("user_file_attachments")
