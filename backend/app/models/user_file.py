import uuid

from sqlalchemy import ForeignKey, Integer, LargeBinary, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
ALLOWED_CONTENT_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/heic", "application/pdf",
}


class UserFile(UUIDPKMixin, TimestampMixin, Base):
    """A personal document/photo a user uploaded (e.g. passport scan, permit
    confirmation PDF) - stored as bytes directly in Postgres. Modest expected
    volume (a handful of personal documents per user) makes this simpler than
    standing up a separate object-storage provider; revisit if that changes.

    Always visible in the user's general "My files" library, independent of
    whether it's linked to any checklist row - see UserFileAttachment for
    that (a many-to-many relationship: one file, e.g. a passport scan, can
    usefully attach to several checklist rows across different destinations)."""

    __tablename__ = "user_files"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)


class UserFileAttachment(UUIDPKMixin, TimestampMixin, Base):
    """Links one UserFile to one checklist row (admin-authored or the user's
    own custom item - exactly one of the two FKs is set). A file can have
    any number of these (including zero, if it just sits in the library)."""

    __tablename__ = "user_file_attachments"

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_files.id", ondelete="CASCADE"), nullable=False, index=True
    )
    checklist_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("checklist_items.id", ondelete="CASCADE"), nullable=True, index=True
    )
    user_checklist_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_checklist_items.id", ondelete="CASCADE"), nullable=True, index=True
    )
