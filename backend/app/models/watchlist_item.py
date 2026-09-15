import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class WatchlistItem(UUIDPKMixin, TimestampMixin, Base):
    """A destination a logged-in user wants to keep an eye on without having
    bought it - a free, no-account-perk-required bookmark (unlike
    AlertSubscription, which is a paid-unlock feature). No notification is
    sent when anything changes yet - this is just a saved list for now."""

    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("user_id", "destination_id", name="uq_watchlist_items_user_destination"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
