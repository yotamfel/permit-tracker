import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import Platform, PurchaseStatus
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Purchase(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "purchases"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform: Mapped[Platform] = mapped_column(Enum(Platform, name="platform"), nullable=False, default=Platform.web)
    amount_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    status: Mapped[PurchaseStatus] = mapped_column(
        Enum(PurchaseStatus, name="purchase_status"), nullable=False, default=PurchaseStatus.pending
    )
    # Admin manual override (support/mistake fixes) - when set and in the
    # future, access stays unlocked regardless of the normal cycle-expiry
    # calculation. Set admin_override_until to null to clear it and fall
    # back to the normal cycle logic.
    admin_override_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    admin_override_note: Mapped[str | None] = mapped_column(String, nullable=True)
