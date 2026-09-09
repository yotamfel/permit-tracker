"""
Pydantic models for `destinations.mechanism_config` (JSONB), one per MechanismType.
Shapes are fixed by PROJECT_SPEC.md §5 — do not accept arbitrary JSON.

Note on PCT / John Muir Trail (two-stage registration + lottery): per the spec's
explicit instruction, this is NOT a new mechanism_type. It is a `lottery` config
with the optional `registration_window` field populated (a separate date range,
before `application_window`, during which hikers register to become eligible
for the lottery itself).
"""
from typing import Literal

from pydantic import BaseModel, Field


class MonthDayWindow(BaseModel):
    start: str = Field(pattern=r"^\d{2}-\d{2}$", description="MM-DD")
    end: str = Field(pattern=r"^\d{2}-\d{2}$", description="MM-DD")


class FixedDailyQuotaConfig(BaseModel):
    mechanism_type: Literal["fixed_daily_quota"] = "fixed_daily_quota"
    daily_quota: int
    booking_opens_days_before: int


class LotteryWindow(BaseModel):
    """One occurrence of an application/lottery window - same shape as
    LotteryConfig's own top-level fields, used for `additional_windows` below."""

    application_window_start: str = Field(pattern=r"^\d{2}-\d{2}$")
    application_window_end: str = Field(pattern=r"^\d{2}-\d{2}$")
    results_date: str = Field(pattern=r"^\d{2}-\d{2}$")
    registration_window: MonthDayWindow | None = None


class LotteryConfig(BaseModel):
    mechanism_type: Literal["lottery"] = "lottery"
    application_window_start: str = Field(pattern=r"^\d{2}-\d{2}$")
    application_window_end: str = Field(pattern=r"^\d{2}-\d{2}$")
    results_date: str = Field(pattern=r"^\d{2}-\d{2}$")
    # Optional two-stage extension (PCT / JMT): a registration window that
    # happens before the application/lottery window itself.
    registration_window: MonthDayWindow | None = None
    # For destinations that run more than one lottery per year (e.g. Angels
    # Landing's 4 seasonal windows) - the fields above are the first/primary
    # window, this holds any further ones. Empty for the common single-window
    # case, so nothing about existing destinations needs to change.
    additional_windows: list[LotteryWindow] = []


class RecurringLotteryConfig(BaseModel):
    """A lottery/application window that recurs weekly or monthly, rather than
    once a year - e.g. JMT's weekly Yosemite wilderness-permit draw, or The
    Subway/The Wave/Grand Canyon Corridor's monthly Recreation.gov lotteries.
    This is inherently an approximation of real systems that have their own
    quirks (exact weekday cutoffs, results-notification timing) - the
    destination's own mechanism_explanation/checklist text is the source of
    truth for those details; this config only drives "when's the next one"
    and the release calendar.
    """

    mechanism_type: Literal["recurring_lottery"] = "recurring_lottery"
    recurrence: Literal["weekly", "monthly"]
    # For recurrence="weekly": which day each application window opens.
    application_weekday: Literal[
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ] | None = None
    # For recurrence="monthly": which day of the month each window opens (1-28,
    # to stay valid in every month).
    application_day_of_month: int | None = Field(default=None, ge=1, le=28)
    # Approximate days from an application window opening to results being
    # announced - a best-effort single number even when the real system's
    # exact delay varies (e.g. by month length).
    results_delay_days: int
    timezone: str
    # Only part of the year is active (e.g. JMT: mid-Nov to early May) - null
    # on both means it recurs year-round (The Subway, The Wave, Grand Canyon
    # Corridor).
    active_window_start: str | None = Field(default=None, pattern=r"^\d{2}-\d{2}$")
    active_window_end: str | None = Field(default=None, pattern=r"^\d{2}-\d{2}$")


class RollingWindowConfig(BaseModel):
    mechanism_type: Literal["rolling_window"] = "rolling_window"
    days_before_travel_date: int


class AdditionalAnnualDate(BaseModel):
    """One further occurrence of a fixed_annual_date release, for destinations
    that release more than once a year (e.g. Conundrum Hot Springs' 3 fixed
    dates). release_time/timezone default to the parent config's own values
    when omitted, since multiple releases in a year are usually at the same
    time of day."""

    typical_release_date: str = Field(pattern=r"^\d{2}-\d{2}$")
    release_time: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    timezone: str | None = None


class FixedAnnualDateConfig(BaseModel):
    mechanism_type: Literal["fixed_annual_date"] = "fixed_annual_date"
    typical_release_date: str = Field(pattern=r"^\d{2}-\d{2}$")
    release_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    timezone: str
    # Further releases in the same year beyond the primary one above - empty
    # for the common once-a-year case.
    additional_dates: list[AdditionalAnnualDate] = []


class WeeklyReleaseConfig(BaseModel):
    mechanism_type: Literal["weekly_release"] = "weekly_release"
    release_weekday: Literal[
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ]
    release_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    timezone: str
    weeks_ahead: int


class GuidedTourOnlyConfig(BaseModel):
    mechanism_type: Literal["guided_tour_only"] = "guided_tour_only"
    note: str = "no self-service release date - booking depends on tour operator availability"


class SingleOperatorAnnualQuotaConfig(BaseModel):
    mechanism_type: Literal["single_operator_annual_quota"] = "single_operator_annual_quota"
    operator_name: str
    annual_quota: int
    typical_booking_lead_time_months: int


class FirstComeFirstServedConfig(BaseModel):
    mechanism_type: Literal["first_come_first_served"] = "first_come_first_served"
    typical_booking_lead_time_months: int


MECHANISM_CONFIG_MODELS: dict[str, type[BaseModel]] = {
    "fixed_daily_quota": FixedDailyQuotaConfig,
    "lottery": LotteryConfig,
    "recurring_lottery": RecurringLotteryConfig,
    "rolling_window": RollingWindowConfig,
    "fixed_annual_date": FixedAnnualDateConfig,
    "weekly_release": WeeklyReleaseConfig,
    "guided_tour_only": GuidedTourOnlyConfig,
    "single_operator_annual_quota": SingleOperatorAnnualQuotaConfig,
    "first_come_first_served": FirstComeFirstServedConfig,
}


def validate_mechanism_config(mechanism_type: str, config: dict) -> BaseModel:
    model = MECHANISM_CONFIG_MODELS.get(mechanism_type)
    if model is None:
        raise ValueError(f"Unknown mechanism_type: {mechanism_type}")
    return model.model_validate({**config, "mechanism_type": mechanism_type})
