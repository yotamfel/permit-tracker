"""
Determines whether a completed purchase still grants access, or whether its
application cycle has passed and the destination should lock again.

A purchase buys access to *one cycle* (the release/travel window that was
upcoming when it was made), not permanent access - see admin discussion,
2026-09-02. The cycle's anchor date is:

- For mechanism types with a computable destination-wide release date
  (fixed_annual_date, lottery, weekly_release): the occurrence that was next
  upcoming *as of the purchase*, recomputed live against the destination's
  current mechanism_config (so an admin editing the date later is reflected
  correctly, rather than freezing whatever was true at purchase time).
- For everything else (no fixed destination-wide date - rolling_window,
  guided_tour_only, first_come_first_served, single_operator_annual_quota,
  fixed_daily_quota): the user's own travel_date from their alert
  subscription for this destination, if they set one.
- If neither applies (no computable date and no travel_date on file): the
  purchase timestamp itself, so access still expires rather than lasting
  forever just because the user skipped setting an alert.

Access stays valid until CYCLE_BUFFER_DAYS after the anchor date, to leave
room for post-release admin/prep time rather than locking the instant the
date passes.
"""
from datetime import datetime, timedelta, timezone, time

from app.services.release_date import compute_next_release

CYCLE_BUFFER_DAYS = 60


def purchase_cycle_anchor(destination, purchase_created_at: datetime, travel_date=None) -> datetime:
    mechanism_type = destination.mechanism_type.value if hasattr(destination.mechanism_type, "value") else destination.mechanism_type
    computed = compute_next_release(mechanism_type, destination.mechanism_config, now=purchase_created_at)
    if computed is not None:
        return computed
    if travel_date is not None:
        return datetime.combine(travel_date, time.min, tzinfo=timezone.utc)
    return purchase_created_at


def purchase_active_until(destination, purchase_created_at: datetime, travel_date=None, admin_override_until: datetime | None = None) -> datetime:
    """The moment access actually lapses - the admin override if it's set
    and later than the normal cycle end, otherwise the normal cycle end."""
    cycle_end = purchase_cycle_anchor(destination, purchase_created_at, travel_date) + timedelta(days=CYCLE_BUFFER_DAYS)
    if admin_override_until is not None and admin_override_until > cycle_end:
        return admin_override_until
    return cycle_end


def purchase_still_active(
    destination,
    purchase_created_at: datetime,
    travel_date=None,
    now: datetime | None = None,
    admin_override_until: datetime | None = None,
) -> bool:
    now = now or datetime.now(timezone.utc)
    if admin_override_until is not None and now < admin_override_until:
        return True
    anchor = purchase_cycle_anchor(destination, purchase_created_at, travel_date)
    return now < anchor + timedelta(days=CYCLE_BUFFER_DAYS)
