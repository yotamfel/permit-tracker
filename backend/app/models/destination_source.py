import uuid

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class DestinationSource(UUIDPKMixin, TimestampMixin, Base):
    """One source consulted while researching a destination - admin-only,
    never shown to end users. Replaces the old free-text research_notes blob
    with a proper list so each source is its own row instead of one long
    wall of text."""

    __tablename__ = "destination_sources"

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Nullable - not every source is a URL (e.g. "the original research
    # spreadsheet note", a phone call, a PDF with no stable link).
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
