import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import ContactMessageStatus
from app.models.mixins import TimestampMixin, UUIDPKMixin


class ContactMessage(UUIDPKMixin, TimestampMixin, Base):
    """A message submitted through the public contact form (no login required).
    Also doubles as the per-destination "something's wrong / missing here"
    form on the destination detail page - when destination_id is set, the
    admin panel treats it as urgent (someone hit a real problem on a live
    page), no separate flag needed."""

    __tablename__ = "contact_messages"

    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    # Set when submitted by a logged-in user, so the admin can cross-reference
    # their account/purchases - nullable since the form doesn't require login.
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    # Set when submitted from a specific destination's page (vs. the general
    # Contact page) - presence of this is what makes a message "urgent" in
    # the admin Inquiries tab.
    destination_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[ContactMessageStatus] = mapped_column(
        Enum(ContactMessageStatus, name="contact_message_status"),
        nullable=False,
        default=ContactMessageStatus.new,
    )
    # The admin's reply, emailed directly to `email` above - stored so the
    # admin panel shows what was already sent.
    admin_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    replied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
