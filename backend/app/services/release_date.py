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
