import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class DestinationResearchReport(UUIDPKMixin, TimestampMixin, Base):
    """One report per researcher-agent + reviewer-agent pass over a destination
    (the two-agent fill-in-and-verify workflow) - shown in the admin
    "Research Reports" tab. Written in Hebrew, per the admin's standing
    preference for Hebrew summaries."""

    __tablename__ = "destination_research_reports"

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    researcher_summary: Mapped[str] = mapped_column(Text, nullable=False)
    reviewer_summary: Mapped[str] = mapped_column(Text, nullable=False)
    escalations: Mapped[str | None] = mapped_column(Text, nullable=True)
