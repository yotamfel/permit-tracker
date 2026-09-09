"""
Unit tests for app/services/release_date.py's compute_next_release - the
"what's the next occurrence" logic that both the public destination pages
and the purchase-cycle expiry logic depend on.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.release_date import compute_next_release


def test_fixed_annual_date_before_this_years_date_returns_this_year():
    now = datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC"))
    result = compute_next_release(
        "fixed_annual_date", {"typical_release_date": "11-03", "release_time": "14:00", "timezone": "Europe/Paris"}, now=now
    )
    assert result.year == 2026
    assert result.month == 11
    assert result.day == 3


def test_fixed_annual_date_after_this_years_date_rolls_to_next_year():
    now = datetime(2026, 12, 1, tzinfo=ZoneInfo("UTC"))
    result = compute_next_release(
        "fixed_annual_date", {"typical_release_date": "11-03", "release_time": "14:00", "timezone": "Europe/Paris"}, now=now
    )
    assert result.year == 2027
    assert result.month == 11
    assert result.day == 3


def test_lottery_uses_application_window_start():
    now = datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC"))
    result = compute_next_release(
        "lottery",
        {"application_window_start": "03-01", "application_window_end": "03-31", "results_date": "04-15", "registration_window": None},
        now=now,
    )
    assert (result.month, result.day) == (3, 1)


def test_lottery_prefers_registration_window_start_when_present():
    now = datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC"))
    result = compute_next_release(
        "lottery",
        {
            "application_window_start": "03-01",
            "application_window_end": "03-31",
            "results_date": "04-15",
            "registration_window": {"start": "02-01", "end": "02-15"},
        },
        now=now,
    )
    assert (result.month, result.day) == (2, 1)


def test_fixed_annual_date_with_additional_dates_picks_soonest():
    # Conundrum Hot Springs shape: 3 releases/year, all should be considered.
    now = datetime(2026, 9, 9, tzinfo=ZoneInfo("UTC"))
    config = {
        "typical_release_date": "02-15",
        "release_time": "08:00",
        "timezone": "America/Denver",
        "additional_dates": [{"typical_release_date": "06-15"}, {"typical_release_date": "10-15"}],
    }
    result = compute_next_release("fixed_annual_date", config, now=now)
    # Feb 15 and Jun 15 have already passed this year - Oct 15 is next.
    assert (result.year, result.month, result.day) == (2026, 10, 15)


def test_fixed_annual_date_additional_dates_inherit_parent_time_and_timezone():
    now = datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC"))
    config = {
        "typical_release_date": "02-15",
        "release_time": "08:00",
        "timezone": "America/Denver",
        "additional_dates": [{"typical_release_date": "06-15"}],
    }
    result = compute_next_release("fixed_annual_date", config, now=now)
    assert (result.month, result.day) == (2, 15)
    assert result.tzinfo == ZoneInfo("America/Denver")
    assert result.hour == 8


def test_lottery_with_additional_windows_picks_soonest():
    # Angels Landing shape: 4 seasonal windows/year.
    now = datetime(2026, 9, 9, tzinfo=ZoneInfo("UTC"))
    config = {
        "application_window_start": "10-01",
        "application_window_end": "10-20",
        "results_date": "10-25",
        "additional_windows": [
            {"application_window_start": "02-13", "application_window_end": "02-25", "results_date": "02-26"},
            {"application_window_start": "04-01", "application_window_end": "04-20", "results_date": "04-25"},
            {"application_window_start": "07-01", "application_window_end": "07-20", "results_date": "07-25"},
        ],
    }
    result = compute_next_release("lottery", config, now=now)
    # Jul 1 window has already passed this year - Oct 1 is next.
    assert (result.year, result.month, result.day) == (2026, 10, 1)


def test_recurring_lottery_weekly_off_season_jumps_to_season_start():
    # JMT shape: weekly (Sunday) draw, only active mid-Nov through early May.
    config = {
        "recurrence": "weekly",
        "application_weekday": "sunday",
        "results_delay_days": 8,
        "timezone": "America/Los_Angeles",
        "active_window_start": "11-15",
        "active_window_end": "05-03",
    }
    now = datetime(2026, 9, 9, tzinfo=ZoneInfo("UTC"))  # off-season
    result = compute_next_release("recurring_lottery", config, now=now)
    assert (result.year, result.month, result.day) == (2026, 11, 15)


def test_recurring_lottery_weekly_in_season_finds_next_weekday():
    config = {
        "recurrence": "weekly",
        "application_weekday": "sunday",
        "results_delay_days": 8,
        "timezone": "America/Los_Angeles",
        "active_window_start": "11-15",
        "active_window_end": "05-03",
    }
    now = datetime(2027, 1, 5, tzinfo=ZoneInfo("UTC"))  # a Tuesday, in-season
    result = compute_next_release("recurring_lottery", config, now=now)
    assert result.weekday() == 6  # Sunday
    assert (result.year, result.month, result.day) == (2027, 1, 10)


def test_recurring_lottery_monthly_year_round():
    # The Subway shape: opens the 1st of every month, no seasonal restriction.
    config = {"recurrence": "monthly", "application_day_of_month": 1, "results_delay_days": 26, "timezone": "America/Denver"}
    now = datetime(2026, 9, 9, tzinfo=ZoneInfo("UTC"))
    result = compute_next_release("recurring_lottery", config, now=now)
    assert (result.year, result.month, result.day) == (2026, 10, 1)


def test_recurring_lottery_dates_in_month_respects_active_window():
    config = {
        "recurrence": "weekly",
        "application_weekday": "sunday",
        "results_delay_days": 8,
        "timezone": "America/Los_Angeles",
        "active_window_start": "11-15",
        "active_window_end": "05-03",
    }
    from app.services.release_date import compute_release_dates_in_month

    assert compute_release_dates_in_month("recurring_lottery", config, 2026, 9) == []
    december_sundays = compute_release_dates_in_month("recurring_lottery", config, 2026, 12)
    assert all(d.weekday() == 6 for d in december_sundays)
    assert len(december_sundays) == 4


def test_mechanism_types_with_no_computable_date_return_none():
    now = datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC"))
    for mechanism_type in ["rolling_window", "guided_tour_only", "first_come_first_served", "single_operator_annual_quota", "fixed_daily_quota"]:
        assert compute_next_release(mechanism_type, {}, now=now) is None
