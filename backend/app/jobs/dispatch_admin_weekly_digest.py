"""
Weekly job: emails admins a single digest of everything that currently needs
manual attention - pending Monitoring diffs, destinations whose source URL
the weekly monitor can't reach, admin_follow_ups due within the next 7 days
(or overdue), and any open contact messages. Urgency is derived from real
data (how long a source has been failing, whether a follow-up is overdue),
not a guessed/AI-scored priority.

Run via: python -m app.jobs.dispatch_admin_weekly_digest
"""
import logging
from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
import app.models  # noqa: F401 - registers every model so cross-model relationships resolve
from app.models.admin_follow_up import AdminFollowUp
from app.models.admin_user import AdminUser
from app.models.contact_message import ContactMessage
from app.models.destination import Destination
from app.models.enums import ContactMessageStatus, ReviewStatus
from app.models.monitoring import MonitoringDiff
from app.services.email_service import send_admin_weekly_digest_email

logger = logging.getLogger(__name__)

# A diff whose diff_summary is this exact placeholder carries no information
# to act on - our own diff algorithm couldn't compute a readable comparison,
# so it needs a manual look at the source page rather than a read of the diff.
_UNREADABLE_DIFF_SUMMARY = "Content hash changed but no line-level diff computed."


def _source_failure_urgency(days_failing: int | None) -> str:
    if days_failing is None or days_failing < 3:
        return "low"
    if days_failing < 14:
        return "medium"
    return "high"


def run() -> None:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        today = now.date()

        pending_diff_rows = db.query(MonitoringDiff).filter(MonitoringDiff.review_status == ReviewStatus.pending).all()
        dest_ids = {d.destination_id for d in pending_diff_rows}
        dest_ids |= {f.destination_id for f in db.query(AdminFollowUp).filter(AdminFollowUp.is_done.is_(False)).all()}
        destinations = {d.id: d for d in db.query(Destination).filter(Destination.id.in_(dest_ids)).all()} if dest_ids else {}

        pending_diffs = [
            {
                "destination_id": d.destination_id,
                "destination_name": destinations[d.destination_id].name if d.destination_id in destinations else "(deleted destination)",
                "unreadable": d.diff_summary.strip() == _UNREADABLE_DIFF_SUMMARY,
            }
            for d in pending_diff_rows
        ]

        failing = db.query(Destination).filter(Destination.source_fetch_failing.is_(True)).all()
        failing_sources = []
        for d in failing:
            days_failing = (now - d.source_fetch_failing_since).days if d.source_fetch_failing_since else None
            failing_sources.append(
                {
                    "destination_id": d.id,
                    "destination_name": d.name,
                    "days_failing": days_failing if days_failing is not None else 0,
                    "urgency": _source_failure_urgency(days_failing),
                }
            )
        # Most urgent (longest-failing) first.
        failing_sources.sort(key=lambda s: s["days_failing"], reverse=True)

        week_out = today + timedelta(days=7)
        upcoming_follow_ups = (
            db.query(AdminFollowUp)
            .filter(AdminFollowUp.is_done.is_(False), AdminFollowUp.due_date <= week_out)
            .order_by(AdminFollowUp.due_date)
            .all()
        )
        follow_ups = [
            {
                "destination_id": f.destination_id,
                "destination_name": destinations[f.destination_id].name if f.destination_id in destinations else "(deleted destination)",
                "title": f.title,
                "notes": f.notes,
                "due_str": f.due_date.strftime("%b %d"),
                "overdue": f.due_date < today,
            }
            for f in upcoming_follow_ups
        ]

        open_inquiries_count = (
            db.query(ContactMessage).filter(ContactMessage.status != ContactMessageStatus.resolved).count()
        )

        if not (pending_diffs or failing_sources or follow_ups or open_inquiries_count):
            logger.info("Nothing for the weekly admin digest - skipping send")
            return

        admin_emails = [a.email for a in db.query(AdminUser).all()]
        send_admin_weekly_digest_email(admin_emails, pending_diffs, failing_sources, follow_ups, open_inquiries_count)
        logger.info(
            "Sent weekly admin digest: %d diff(s), %d failing source(s), %d follow-up(s), %d open inquiry(ies)",
            len(pending_diffs),
            len(failing_sources),
            len(follow_ups),
            open_inquiries_count,
        )
    finally:
        db.close()


if __name__ == "__main__":
    from app.core.monitoring import init_sentry

    init_sentry()
    logging.basicConfig(level=logging.INFO)
    run()
