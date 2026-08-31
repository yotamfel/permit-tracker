import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import ChecklistItemSection, ChecklistItemType
from app.models.mixins import TimestampMixin, UUIDPKMixin


class ChecklistItem(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "checklist_items"

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False
    )
    item_type: Mapped[ChecklistItemType] = mapped_column(
        Enum(ChecklistItemType, name="checklist_item_type"), nullable=False
    )
    # "specific" (required for the permit itself) vs "good_to_know" (worth
    # knowing - country-entry bureaucracy, health/safety tips, etc. - but not
    # required for the application). Defaults to "specific" so pre-existing
    # rows keep their current meaning.
    section: Mapped[ChecklistItemSection] = mapped_column(
        Enum(ChecklistItemSection, name="checklist_item_section"),
        nullable=False,
        default=ChecklistItemSection.specific,
        server_default=ChecklistItemSection.specific.value,
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    text_key: Mapped[str] = mapped_column(String, nullable=False)

    destination: Mapped["Destination"] = relationship(back_populates="checklist_items")
