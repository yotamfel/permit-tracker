import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class AdminFollowUp(UUIDPKMixin, TimestampMixin, Base):
    """A scheduled reminder to manually re-check something about a destination
    on a given date - e.g. "official 2026/27 prices publish in October, go
    check and update the page." Admin-only, shown on a follow-up calendar.
    The same destination can have several of these on different dates."""

    __tablename__ = "admin_follow_ups"

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    # What to check, where to check it, and any other context (e.g. specific
    # URLs, what changed last time, what "good" looks like).
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Set once the due-date reminder email has gone out, so the daily job
    # sends it exactly once per follow-up rather than re-notifying every day
    # it stays undone.
    reminder_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
