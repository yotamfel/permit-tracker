import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class AgentReport(UUIDPKMixin, TimestampMixin, Base):
    """A report written by an orchestrated agent pass - shown in the admin
    "Reports" tab, grouped by agent_type. Written directly to the DB by the
    orchestrating session, not authored via a POST endpoint by the admin.

    agent_type is a free string (not a DB enum) so new agent types can be
    added without a migration - known values so far:
      - "destination_pipeline": the researcher+reviewer two-agent pass that
        fills in and verifies one destination. destination_id always set;
        summary = researcher's report, secondary_summary = reviewer's report.
      - "visitor_tester": an agent that role-plays an actual visitor trying
        to use a specific destination page. destination_id always set;
        secondary_summary unused (single-agent pass).
      - "ux_reviewer": a site-wide design/UX review, not tied to one
        destination. destination_id is null; title carries a short label
        instead (e.g. "Full-site UX review - 2026-09-02").
    """

    __tablename__ = "agent_reports"

    agent_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    destination_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    # Short label for reports with no destination to name themselves after
    # (e.g. a site-wide UX review). Optional even for destination-tied
    # reports - the destination's own name is usually enough.
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    secondary_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    escalations: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
