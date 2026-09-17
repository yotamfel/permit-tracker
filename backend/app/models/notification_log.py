import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import NotificationStatus
from app.models.mixins import TimestampMixin, UUIDPKMixin


class NotificationLog(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "notification_log"

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alert_subscriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False, default="email")
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, name="notification_status"), nullable=False
    )
    # Which of the subscription's (possibly several) lead times this specific
    # notification was for - null on rows logged before multi-lead-time
    # support existed. Lets dispatch_alerts.py dedupe per lead time instead of
    # per subscription, now that one subscription can fire more than once
    # against the same release moment.
    lead_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
