import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class PostReleaseFeedback(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "post_release_feedback"

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alert_subscriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Denormalized (subscription_id already implies these) purely for easy
    # querying/aggregation without a join - per spec addendum.
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Which specific release cycle this feedback relates to - a destination's
    # release can recur (annually/weekly), so this disambiguates occurrences.
    release_occurrence_date: Mapped[date] = mapped_column(Date, nullable=False)
    succeeded: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    found_site_helpful: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    free_text_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Unguessable token for the no-login "click to respond" email links -
    # same pattern as User.password_reset_token.
    response_token: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
