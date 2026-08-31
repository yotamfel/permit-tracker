import uuid
from datetime import date

from pydantic import BaseModel

# Preset lead times offered in the UI, in minutes.
LEAD_TIME_PRESET_MINUTES = {20160, 10080, 4320, 1440, 30}


class SubscriptionCreateRequest(BaseModel):
    destination_id: uuid.UUID
    lead_time_minutes: int = 10080
    travel_date: date | None = None  # required for mechanism types with no fixed release date


class SubscriptionOut(BaseModel):
    id: uuid.UUID
    destination_id: uuid.UUID
    lead_time_minutes: int
    is_active: bool
    travel_date: date | None

    model_config = {"from_attributes": True}
