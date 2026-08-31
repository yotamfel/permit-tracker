import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import ReviewStatus
from app.models.mixins import TimestampMixin, UUIDPKMixin


class MonitoringSnapshot(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "monitoring_snapshots"

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_text_excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class MonitoringDiff(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "monitoring_diffs"

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    previous_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("monitoring_snapshots.id", ondelete="SET NULL"), nullable=True
    )
    new_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("monitoring_snapshots.id", ondelete="CASCADE"), nullable=False
    )
    diff_summary: Mapped[str] = mapped_column(Text, nullable=False)
    review_status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="review_status"), nullable=False, default=ReviewStatus.pending
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
