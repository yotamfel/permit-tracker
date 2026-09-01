import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class DestinationAlternative(UUIDPKMixin, TimestampMixin, Base):
    """Spec addendum: Pre-Purchase Trust Signals + Post-Purchase Tool Features
    §2.4 - "If you don't get in" backup suggestions. Admin-managed, one row per
    (destination, suggested alternative) pair; only published alternatives are
    ever shown to users."""

    __tablename__ = "destination_alternatives"

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alternative_destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Free-text note explaining why it's a good alternative (e.g. "Similar
    # trek, far less competitive") - plain text, not translation-keyed, since
    # the site is English-only for now.
    note: Mapped[str | None] = mapped_column(String, nullable=True)
