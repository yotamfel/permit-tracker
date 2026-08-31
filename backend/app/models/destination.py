import uuid
from datetime import datetime

from sqlalchemy import Boolean, Enum, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import Category, CompetitivenessLevel, IssuingAuthority, MechanismType
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Destination(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "destinations"

    country: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[Category] = mapped_column(Enum(Category, name="category"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    mechanism_type: Mapped[MechanismType] = mapped_column(
        Enum(MechanismType, name="mechanism_type"), nullable=False
    )
    mechanism_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    issuing_authority: Mapped[IssuingAuthority] = mapped_column(
        Enum(IssuingAuthority, name="issuing_authority"), nullable=False
    )
    competitiveness_level: Mapped[CompetitivenessLevel] = mapped_column(
        Enum(CompetitivenessLevel, name="competitiveness_level"), nullable=False
    )
    # Nullable to allow unpublished stub rows (§10) that don't have a verified
    # source yet; a destination must have a source_url before an admin publishes it.
    # Not shown to end users (admin/monitoring only) - see application_url below
    # for the public-facing "go apply here" link.
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # The actual booking/application portal - shown to users who've unlocked
    # this destination as the "Apply here" call to action. Often the same URL
    # as source_url in practice, but conceptually distinct (where the research
    # came from vs. where the user takes action) and admin-editable separately.
    application_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    price_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=4.99)

    checklist_items: Mapped[list["ChecklistItem"]] = relationship(
        back_populates="destination", cascade="all, delete-orphan", order_by="ChecklistItem.order_index"
    )
