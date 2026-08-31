"""
Alert dispatch job. For each active alert_subscription, computes whether "now" falls
within lead_time_days of the destination's next known release/open date and, if so,
sends the alert email once and logs it to notification_log.

- fixed_annual_date / weekly_release / lottery: release date computed directly from
  mechanism_config (see app/services/release_date.py).
- rolling_window: booking opens `days_before_travel_date` days before the user's
  travel_date (required on the subscription for this mechanism type).
- guided_tour_only / first_come_first_served / single_operator_annual_quota /
  fixed_daily_quota: no fixed release date exists at all - the "trigger" is just the
  user's travel_date minus lead_time_days, and the email is a generic "book as early
  as possible for your travel date" reminder rather than an exact release-time alert.

Run via: python -m app.jobs.dispatch_alerts (intended to run daily).

Simplification: dedupe is done by checking whether a notification was already sent
for this subscription within the last `lead_time_days` days, rather than tracking an
explicit per-cycle key. This is correct for annual/weekly cycles that are longer than
typical lead times, but could under-fire on a second event happening inside that
window - acceptable for MVP, flagged here for anyone extending this job.
"""
import logging
from datetime import date, datetime, timedelta, timezone

from app.db import SessionLocal
from app.models.alert_subscription import AlertSubscription
from app.models.destination import Destination
from app.models.enums import MechanismType, NotificationStatus
from app.models.notification_log import NotificationLog
from app.models.user import User
from app.services.email_service import send_alert_email
from app.services.release_date import compute_next_release, compute_rolling_window_open_date

logger = logging.getLogger(__name__)

NO_FIXED_DATE_TYPES = {
    MechanismType.guided_tour_only,
    MechanismType.first_come_first_served,
    MechanismType.single_operator_annual_quota,
    MechanismType.fixed_daily_quota,
}


def _already_notified_recently(db, subscription_id, lead_time_days: int) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(days=max(lead_time_days, 1))
    return (
        db.query(NotificationLog)
        .filter(NotificationLog.subscription_id == subscription_id, NotificationLog.sent_at >= cutoff)
        .first()
        is not None
    )


def _compute_trigger_date(d: Destination, sub: AlertSubscription) -> date | None:
    if d.mechanism_type == MechanismType.rolling_window:
        if sub.travel_date is None:
            return None
        return compute_rolling_window_open_date(d.mechanism_config["days_before_travel_date"], sub.travel_date)

    if d.mechanism_type in NO_FIXED_DATE_TYPES:
        if sub.travel_date is None:
            return None
        return sub.travel_date - timedelta(days=sub.lead_time_days)

    next_release = compute_next_release(d.mechanism_type.value, d.mechanism_config)
    if next_release is None:
        return None
    return (next_release - timedelta(days=sub.lead_time_days)).date()


def run() -> None:
    db = SessionLocal()
    try:
        today = datetime.now(timezone.utc).date()
        subs = db.query(AlertSubscription).filter(AlertSubscription.is_active.is_(True)).all()

        for sub in subs:
            d = db.get(Destination, sub.destination_id)
            user = db.get(User, sub.user_id)
            if d is None or user is None or not d.is_published:
                continue

            trigger_date = _compute_trigger_date(d, sub)
            if trigger_date is None or trigger_date > today:
                continue

            if _already_notified_recently(db, sub.id, sub.lead_time_days):
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
                    f"(around {trigger_date + timedelta(days=sub.lead_time_days)}). "
                    f"You asked to be notified {sub.lead_time_days} day(s) in advance.</p>"
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
