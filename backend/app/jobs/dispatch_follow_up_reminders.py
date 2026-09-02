"""
Daily job: emails admins a digest of admin_follow_ups due today (see the
Follow-ups admin tab / app/models/admin_follow_up.py). Sends once per
follow-up (reminder_sent_at), not repeated daily if left undone - matches
"an email that arrives on the day it's due", not a nag.

Run via: python -m app.jobs.dispatch_follow_up_reminders
"""
import logging
from datetime import datetime, timezone

from app.db import SessionLocal
import app.models  # noqa: F401 - registers every model so cross-model relationships (e.g. Destination.sources) resolve
from app.models.admin_follow_up import AdminFollowUp
from app.models.admin_user import AdminUser
from app.models.destination import Destination
from app.services.email_service import send_follow_up_reminder_email

logger = logging.getLogger(__name__)


def run() -> None:
    db = SessionLocal()
    try:
        today = datetime.now(timezone.utc).date()
        due = (
            db.query(AdminFollowUp)
            .filter(AdminFollowUp.due_date == today, AdminFollowUp.reminder_sent_at.is_(None))
            .all()
        )
        if not due:
            return

        items = []
        for f in due:
            d = db.get(Destination, f.destination_id)
            items.append({"destination_name": d.name if d else "(deleted destination)", "title": f.title, "notes": f.notes})

        admin_emails = [a.email for a in db.query(AdminUser).all()]
        try:
            send_follow_up_reminder_email(admin_emails, items)
        except Exception:
            logger.exception("Failed to send follow-up reminder digest")
            return

        for f in due:
            f.reminder_sent_at = datetime.now(timezone.utc)
            db.add(f)
        db.commit()
        logger.info("Sent follow-up reminder digest for %d item(s)", len(due))
    finally:
        db.close()


if __name__ == "__main__":
    from app.core.monitoring import init_sentry

    init_sentry()
    logging.basicConfig(level=logging.INFO)
    run()
