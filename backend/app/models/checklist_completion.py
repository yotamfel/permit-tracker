import uuid
from datetime import datetime

from sqlalchemy import DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class ChecklistCompletion(UUIDPKMixin, TimestampMixin, Base):
    """
    Per-user "I did this" tracking for one row for the unified prep list
    (PrepItemOut.id - either a ChecklistItem.id or a DestinationRequirement.id,
    no FK since it's deliberately polymorphic across both source tables).
    """

    __tablename__ = "checklist_completions"
    __table_args__ = (UniqueConstraint("user_id", "prep_item_id", name="uq_completion_user_item"),)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    destination_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    prep_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
