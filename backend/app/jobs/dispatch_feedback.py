"""
Post-release feedback dispatch job (spec addendum: Post-Release Feedback +
Homepage Calendar, §1). For each active alert_subscription whose release
moment (see app/services/release_date.py:subscription_release_moment - same
computation dispatch_alerts.py uses) is 1+ day in the past, create a
post_release_feedback row (once per subscription+occurrence) and email the
subscriber asking whether they succeeded.

Run via: python -m app.jobs.dispatch_feedback. Daily cadence is enough - this
isn't time-sensitive the way the 30-minute alert preset is.
"""
import logging
import secrets
from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.db import SessionLocal
import app.models  # noqa: F401 - registers every model so cross-model relationships (e.g. Destination.sources) resolve
from app.models.alert_subscription import AlertSubscription
from app.models.destination import Destination
from app.models.post_release_feedback import PostReleaseFeedback
from app.models.user import User
from app.services.email_service import send_post_release_feedback_email
from app.services.release_date import subscription_release_moment

logger = logging.getLogger(__name__)
settings = get_settings()


def run() -> None:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        subs = db.query(AlertSubscription).filter(AlertSubscription.is_active.is_(True)).all()

        for sub in subs:
            d = db.get(Destination, sub.destination_id)
            user = db.get(User, sub.user_id)
            if d is None or user is None or not d.is_published:
                continue

            release_moment = subscription_release_moment(d, sub)
            if release_moment is None or release_moment > now - timedelta(days=1):
                continue

            occurrence_date = release_moment.date()
            existing = (
                db.query(PostReleaseFeedback)
                .filter(
                    PostReleaseFeedback.subscription_id == sub.id,
                    PostReleaseFeedback.release_occurrence_date == occurrence_date,
                )
                .first()
            )
            if existing is not None:
                continue

            feedback = PostReleaseFeedback(
                subscription_id=sub.id,
                user_id=user.id,
                destination_id=d.id,
                release_occurrence_date=occurrence_date,
                response_token=secrets.token_urlsafe(32),
            )
            db.add(feedback)
            db.flush()

            respond_url_base = f"{settings.backend_url}/api/feedback/{feedback.response_token}/answer"
            try:
                send_post_release_feedback_email(user.email, d.name, respond_url_base)
                feedback.email_sent_at = datetime.now(timezone.utc)
            except Exception:
                logger.exception("Failed to send post-release feedback email for subscription %s", sub.id)

            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
