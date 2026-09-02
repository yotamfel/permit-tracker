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


def test_mechanism_types_with_no_computable_date_return_none():
    now = datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC"))
    for mechanism_type in ["rolling_window", "guided_tour_only", "first_come_first_served", "single_operator_annual_quota", "fixed_daily_quota"]:
        assert compute_next_release(mechanism_type, {}, now=now) is None
