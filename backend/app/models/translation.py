import uuid

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Translation(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "translations"
    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", "locale", name="uq_translation_entity_locale"),
    )

    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    locale: Mapped[str] = mapped_column(String(8), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
