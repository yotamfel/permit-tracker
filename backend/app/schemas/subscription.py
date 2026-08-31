import uuid
from datetime import date

from pydantic import BaseModel


class SubscriptionCreateRequest(BaseModel):
    destination_id: uuid.UUID
    lead_time_days: int = 7
    travel_date: date | None = None  # required for mechanism types with no fixed release date


class SubscriptionOut(BaseModel):
    id: uuid.UUID
    destination_id: uuid.UUID
    lead_time_days: int
    is_active: bool
    travel_date: date | None

    model_config = {"from_attributes": True}
