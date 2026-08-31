import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class AlertSubscription(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "alert_subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # For mechanism types with no computable release date (guided_tour_only,
    # first_come_first_served): the user supplies their intended travel date,
    # and the alert is computed relative to that instead of a fixed release window.
    travel_date: Mapped[date | None] = mapped_column(Date, nullable=True)
