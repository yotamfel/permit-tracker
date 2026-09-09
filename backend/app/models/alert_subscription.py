import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class AlertSubscription(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "alert_subscriptions"
    # One alert per user per destination - re-submitting "Set alert" (e.g. a
    # double-submit race) updates the existing row instead of creating a
    # duplicate. See app/api/subscriptions.py's upsert logic.
    __table_args__ = (UniqueConstraint("user_id", "destination_id", name="uq_alert_subscriptions_user_destination"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Minutes rather than days, so short lead times (e.g. 30 minutes before an
    # exact release time) are representable. Presets: 20160 (2wk), 10080 (1wk),
    # 4320 (3d), 1440 (1d), 30 (30min) - see app/api/subscriptions.py.
    lead_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=10080)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # For mechanism types with no computable release date (guided_tour_only,
    # first_come_first_served): the user supplies their intended travel date,
    # and the alert is computed relative to that instead of a fixed release window.
    travel_date: Mapped[date | None] = mapped_column(Date, nullable=True)
