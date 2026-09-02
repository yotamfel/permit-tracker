"""
Unit tests for the purchase-cycle expiry logic (app/services/purchase_cycle.py).

A purchase unlocks a destination for one application cycle, not forever -
these tests pin down exactly when that cycle ends for each mechanism type,
since getting this wrong either locks out a paying user early or leaves
access open indefinitely. No DB needed - purchase_cycle.py takes plain
values, so these run fast and don't depend on a live database.
"""
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

from app.services.purchase_cycle import CYCLE_BUFFER_DAYS, purchase_active_until, purchase_still_active


def _destination(mechanism_type, config):
    return SimpleNamespace(mechanism_type=mechanism_type, mechanism_config=config)


class TestFixedAnnualDate:
    def setup_method(self):
        self.destination = _destination(
            "fixed_annual_date", {"typical_release_date": "11-03", "release_time": "14:00", "timezone": "Europe/Paris"}
        )

    def test_active_before_cycle_end(self):
        purchased = datetime(2025, 8, 1, tzinfo=timezone.utc)
        assert purchase_still_active(self.destination, purchased, now=datetime(2026, 1, 1, tzinfo=timezone.utc))

    def test_locked_after_cycle_end(self):
        purchased = datetime(2025, 8, 1, tzinfo=timezone.utc)
        assert not purchase_still_active(self.destination, purchased, now=datetime(2026, 1, 10, tzinfo=timezone.utc))

    def test_purchase_after_this_years_date_anchors_to_next_year(self):
        # Bought Dec 1, after that year's Nov 3 release already happened.
        purchased = datetime(2025, 12, 1, tzinfo=timezone.utc)
        assert purchase_still_active(self.destination, purchased, now=datetime(2026, 12, 1, tzinfo=timezone.utc))
        assert not purchase_still_active(self.destination, purchased, now=datetime(2027, 2, 1, tzinfo=timezone.utc))


class TestNoFixedDateMechanisms:
    def setup_method(self):
        self.destination = _destination("rolling_window", {"days_before_travel_date": 180})

    def test_active_before_travel_date_plus_buffer(self):
        purchased = datetime(2026, 1, 1, tzinfo=timezone.utc)
        assert purchase_still_active(
            self.destination, purchased, travel_date=date(2026, 6, 15), now=datetime(2026, 7, 1, tzinfo=timezone.utc)
        )

    def test_locked_after_travel_date_plus_buffer(self):
        purchased = datetime(2026, 1, 1, tzinfo=timezone.utc)
        assert not purchase_still_active(
            self.destination, purchased, travel_date=date(2026, 6, 15), now=datetime(2026, 9, 1, tzinfo=timezone.utc)
        )

    def test_no_travel_date_falls_back_to_purchase_date(self):
        purchased = datetime(2026, 1, 1, tzinfo=timezone.utc)
        assert purchase_still_active(self.destination, purchased, travel_date=None, now=datetime(2026, 1, 31, tzinfo=timezone.utc))
        assert not purchase_still_active(self.destination, purchased, travel_date=None, now=datetime(2026, 4, 1, tzinfo=timezone.utc))


class TestAdminOverride:
    def setup_method(self):
        self.destination = _destination("rolling_window", {"days_before_travel_date": 180})
        self.purchased = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def test_override_keeps_access_past_normal_lock(self):
        override_until = datetime(2026, 6, 1, tzinfo=timezone.utc)
        assert purchase_still_active(
            self.destination, self.purchased, now=datetime(2026, 4, 1, tzinfo=timezone.utc), admin_override_until=override_until
        )

    def test_override_still_expires(self):
        override_until = datetime(2026, 6, 1, tzinfo=timezone.utc)
        assert not purchase_still_active(
            self.destination, self.purchased, now=datetime(2026, 7, 1, tzinfo=timezone.utc), admin_override_until=override_until
        )

    def test_active_until_reflects_override_when_later_than_cycle_end(self):
        override_until = datetime(2026, 6, 1, tzinfo=timezone.utc)
        result = purchase_active_until(self.destination, self.purchased, admin_override_until=override_until)
        assert result == override_until

    def test_active_until_ignores_override_when_earlier_than_cycle_end(self):
        # An override in the past (e.g. cleared/expired) shouldn't shorten
        # the normal cycle end.
        override_until = datetime(2026, 1, 15, tzinfo=timezone.utc)
        result = purchase_active_until(self.destination, self.purchased, admin_override_until=override_until)
        assert result == self.purchased + timedelta(days=CYCLE_BUFFER_DAYS)
