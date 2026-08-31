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


class LotteryConfig(BaseModel):
    mechanism_type: Literal["lottery"] = "lottery"
    application_window_start: str = Field(pattern=r"^\d{2}-\d{2}$")
    application_window_end: str = Field(pattern=r"^\d{2}-\d{2}$")
    results_date: str = Field(pattern=r"^\d{2}-\d{2}$")
    # Optional two-stage extension (PCT / JMT): a registration window that
    # happens before the application/lottery window itself.
    registration_window: MonthDayWindow | None = None


class RollingWindowConfig(BaseModel):
    mechanism_type: Literal["rolling_window"] = "rolling_window"
    days_before_travel_date: int


class FixedAnnualDateConfig(BaseModel):
    mechanism_type: Literal["fixed_annual_date"] = "fixed_annual_date"
    typical_release_date: str = Field(pattern=r"^\d{2}-\d{2}$")
    release_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    timezone: str


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
