"""
Computes the "next known release date" for a destination from its mechanism_config.

- rolling_window / fixed_annual_date: straightforward date math, computable without
  any user input.
- lottery / weekly_release: recurring windows taken directly from the config.
- guided_tour_only / first_come_first_served / single_operator_annual_quota:
  no fixed release date exists. These return None here; user-facing alerts for
  these types are instead computed relative to a user-supplied travel_date
  (see app/services/alerts.py).
"""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _next_month_day(today: date, month_day: str) -> date:
    month, day = (int(p) for p in month_day.split("-"))
    candidate = date(today.year, month, day)
    if candidate < today:
        candidate = date(today.year + 1, month, day)
    return candidate


def compute_next_release(mechanism_type: str, config: dict, now: datetime | None = None) -> datetime | None:
    now = now or datetime.now(ZoneInfo("UTC"))
    today = now.date()

    if mechanism_type == "fixed_annual_date":
        release_date = _next_month_day(today, config["typical_release_date"])
        tz = ZoneInfo(config["timezone"])
        hour, minute = (int(p) for p in config["release_time"].split(":"))
        return datetime.combine(release_date, time(hour, minute), tzinfo=tz)

    if mechanism_type == "weekly_release":
        tz = ZoneInfo(config["timezone"])
        target_weekday = WEEKDAYS[config["release_weekday"]]
        hour, minute = (int(p) for p in config["release_time"].split(":"))
        days_ahead = (target_weekday - today.weekday()) % 7
        next_date = today + timedelta(days=days_ahead)
        candidate = datetime.combine(next_date, time(hour, minute), tzinfo=tz)
        if candidate < now:
            candidate += timedelta(days=7)
        return candidate

    if mechanism_type == "lottery":
        window_start = config.get("registration_window", {}).get("start") if config.get("registration_window") else None
        window_start = window_start or config["application_window_start"]
        next_date = _next_month_day(today, window_start)
        return datetime.combine(next_date, time(0, 0), tzinfo=ZoneInfo("UTC"))

    if mechanism_type == "rolling_window":
        # No fixed calendar date - opens N days before whatever travel date the
        # user has in mind. Without a travel_date we can't compute an absolute date.
        return None

    # fixed_daily_quota, guided_tour_only, single_operator_annual_quota,
    # first_come_first_served: no computable fixed release date.
    return None


def compute_rolling_window_open_date(days_before_travel_date: int, travel_date: date) -> date:
    return travel_date - timedelta(days=days_before_travel_date)


def compute_release_dates_in_month(mechanism_type: str, config: dict, year: int, month: int) -> list[date]:
    """All occurrences of this destination's release date that fall within the
    given calendar month - for the homepage calendar (spec addendum §2), which
    needs every occurrence in the month (e.g. every weekly_release Tuesday),
    not just the single next one compute_next_release returns. Same set of
    computable types as compute_next_release; everything else returns [].
    """
    if mechanism_type == "fixed_annual_date":
        release_month, release_day = (int(p) for p in config["typical_release_date"].split("-"))
        if release_month == month:
            return [date(year, release_month, release_day)]
        return []

    if mechanism_type == "lottery":
        window_start = config.get("registration_window", {}).get("start") if config.get("registration_window") else None
        window_start = window_start or config["application_window_start"]
        release_month, release_day = (int(p) for p in window_start.split("-"))
        if release_month == month:
            return [date(year, release_month, release_day)]
        return []

    if mechanism_type == "weekly_release":
        target_weekday = WEEKDAYS[config["release_weekday"]]
        first_of_month = date(year, month, 1)
        days_ahead = (target_weekday - first_of_month.weekday()) % 7
        current = first_of_month + timedelta(days=days_ahead)
        dates = []
        while current.month == month:
            dates.append(current)
            current += timedelta(days=7)
        return dates

    # rolling_window / fixed_daily_quota / guided_tour_only /
    # single_operator_annual_quota / first_come_first_served: no destination-
    # wide date to show on a public calendar.
    return []


# Mechanism types with no destination-wide computable release date - the actual
# release/open moment only exists per-subscription, relative to that user's own
# travel_date (see subscription_release_moment below).
NO_FIXED_DATE_TYPES = {"guided_tour_only", "first_come_first_served", "single_operator_annual_quota", "fixed_daily_quota"}


def subscription_release_moment(destination, subscription) -> datetime | None:
    """The actual release/open moment a given alert_subscription is tracking -
    a destination-wide date for computable mechanism types, or a moment derived
    from that subscription's own travel_date for rolling_window/no-fixed-date
    types. Shared by dispatch_alerts.py and dispatch_feedback.py so both use the
    exact same notion of "when did/does this open" for a given subscription.
    """
    mechanism_type = destination.mechanism_type.value if hasattr(destination.mechanism_type, "value") else destination.mechanism_type

    if mechanism_type == "rolling_window":
        if subscription.travel_date is None:
            return None
        open_date = compute_rolling_window_open_date(
            destination.mechanism_config["days_before_travel_date"], subscription.travel_date
        )
        return datetime.combine(open_date, time.min, tzinfo=ZoneInfo("UTC"))

    if mechanism_type in NO_FIXED_DATE_TYPES:
        if subscription.travel_date is None:
            return None
        return datetime.combine(subscription.travel_date, time.min, tzinfo=ZoneInfo("UTC"))

    return compute_next_release(mechanism_type, destination.mechanism_config)
