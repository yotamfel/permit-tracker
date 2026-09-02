"""
Alert dispatch job. For each active alert_subscription, computes whether "now" is
past (trigger moment = release moment - lead_time_minutes) and, if so, sends the
alert email once and logs it to notification_log.

- fixed_annual_date / weekly_release / lottery: release date+time computed directly
  from mechanism_config (see app/services/release_date.py).
- rolling_window: booking opens `days_before_travel_date` days before the user's
  travel_date (required on the subscription for this mechanism type).
- guided_tour_only / first_come_first_served / single_operator_annual_quota /
  fixed_daily_quota: no fixed release date exists at all - the "trigger" is just the
  user's travel_date minus lead_time_minutes, and the email is a generic "book as
  early as possible for your travel date" reminder rather than an exact-time alert.

Run via: python -m app.jobs.dispatch_alerts. Because the shortest lead-time preset is
30 minutes, this needs to run frequently (every 10-15 minutes) to be timely - see
SETUP_GUIDE.md for the Railway cron schedule. A less frequent schedule still works
correctly (the trigger check is "has the moment passed", not "is it exactly now"),
just with less precise timing for the short presets.

Simplification: dedupe is done by checking whether a notification was already sent
for this subscription within the last `lead_time_minutes`, rather than tracking an
explicit per-cycle key. This is correct for annual/weekly cycles that are much longer
than any lead-time preset, but could under-fire on a second event happening inside
that window - acceptable for MVP, flagged here for anyone extending this job.
"""
import logging
from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
import app.models  # noqa: F401 - registers every model so cross-model relationships (e.g. Destination.sources) resolve
from app.models.alert_subscription import AlertSubscription
from app.models.destination import Destination
from app.models.enums import MechanismType, NotificationStatus
from app.models.notification_log import NotificationLog
from app.models.user import User
from app.services.email_service import send_alert_email
from app.services.release_date import NO_FIXED_DATE_TYPES as _NO_FIXED_DATE_TYPE_VALUES
from app.services.release_date import subscription_release_moment

logger = logging.getLogger(__name__)

NO_FIXED_DATE_TYPES = {MechanismType(v) for v in _NO_FIXED_DATE_TYPE_VALUES}


def _already_notified_recently(db, subscription_id, lead_time_minutes: int) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=max(lead_time_minutes, 1))
    return (
        db.query(NotificationLog)
        .filter(NotificationLog.subscription_id == subscription_id, NotificationLog.sent_at >= cutoff)
        .first()
        is not None
    )


def _release_moment(d: Destination, sub: AlertSubscription) -> datetime | None:
    """The actual release/open moment this subscription is alerting on (before
    subtracting lead time) - used both to compute the trigger and for the email
    copy. Delegates to the shared implementation in release_date.py, also used
    by dispatch_feedback.py."""
    return subscription_release_moment(d, sub)


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

            release_moment = _release_moment(d, sub)
            if release_moment is None:
                continue
            trigger_moment = release_moment - timedelta(minutes=sub.lead_time_minutes)
            if trigger_moment > now:
                continue

            if _already_notified_recently(db, sub.id, sub.lead_time_minutes):
                continue

            is_book_early = d.mechanism_type in NO_FIXED_DATE_TYPES | {MechanismType.rolling_window}
            if is_book_early:
                body = (
                    f"<p>Reminder: book <strong>{d.name}</strong> as early as possible for your "
                    f"upcoming travel date ({sub.travel_date}). This destination has no fixed "
                    f"release window, so availability can close well in advance.</p>"
                )
            else:
                body = (
                    f"<p>The application/release window for <strong>{d.name}</strong> opens soon "
                    f"(around {release_moment.strftime('%Y-%m-%d %H:%M %Z')}). "
                    f"You asked to be notified {_format_lead_time(sub.lead_time_minutes)} in advance.</p>"
                )

            status = NotificationStatus.sent
            try:
                send_alert_email(user.email, d.name, body)
            except Exception:
                logger.exception("Failed to send alert email for subscription %s", sub.id)
                status = NotificationStatus.failed

            db.add(
                NotificationLog(
                    subscription_id=sub.id,
                    sent_at=datetime.now(timezone.utc),
                    channel="email",
                    status=status,
                )
            )
            db.commit()
    finally:
        db.close()


def _format_lead_time(minutes: int) -> str:
    if minutes % 1440 == 0:
        days = minutes // 1440
        return f"{days} day{'s' if days != 1 else ''}"
    if minutes % 60 == 0:
        hours = minutes // 60
        return f"{hours} hour{'s' if hours != 1 else ''}"
    return f"{minutes} minutes"


if __name__ == "__main__":
    from app.core.monitoring import init_sentry

    init_sentry()
    logging.basicConfig(level=logging.INFO)
    run()
