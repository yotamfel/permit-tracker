import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import RequirementType
from app.models.mixins import TimestampMixin, UUIDPKMixin


class GeneralRequirement(UUIDPKMixin, TimestampMixin, Base):
    """
    Spec addendum §2.1 - a reusable requirement definition not tied to any single
    destination (e.g. "passport valid 6+ months"). Localized text is looked up via
    the translations table using entity_type="general_requirement.title" /
    "general_requirement.description" and entity_id=this row's id - title_key /
    description_key below are human-readable labels only, following the same
    convention as ChecklistItem.text_key.
    """

    __tablename__ = "general_requirements"

    requirement_type: Mapped[RequirementType] = mapped_column(
        Enum(RequirementType, name="requirement_type"), nullable=False
    )
    title_key: Mapped[str] = mapped_column(String, nullable=False)
    description_key: Mapped[str] = mapped_column(String, nullable=False)
    is_general_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class DestinationRequirement(UUIDPKMixin, TimestampMixin, Base):
    """Spec addendum §2.2 - links a destination to a general requirement."""

    __tablename__ = "destination_requirements"

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    general_requirement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("general_requirements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    destination_specific_note_key: Mapped[str | None] = mapped_column(String, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # The exact official page for this specific step (e.g. a visa application
    # form), not just the destination's general source_url - shown as a link
    # next to this item, same idea as ChecklistItem.link_url.
    action_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    general_requirement: Mapped["GeneralRequirement"] = relationship()
