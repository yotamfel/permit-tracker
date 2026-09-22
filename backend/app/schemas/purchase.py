import uuid
from datetime import date

from pydantic import BaseModel

from app.models.enums import PurchaseStatus


class CheckoutCreateRequest(BaseModel):
    # Required (enforced in the endpoint, not here, so the error message can
    # name the destination's mechanism_type) for mechanism types with no
    # computable release date - see subscriptions.py's TRAVEL_DATE_REQUIRED_TYPES.
    # Without a travel_date, purchase_cycle.py has nothing to anchor the
    # 60-day access window to but the purchase timestamp itself, which can
    # close access long before the user actually needs it.
    travel_date: date | None = None


class CheckoutSessionOut(BaseModel):
    checkout_url: str


class PurchaseOut(BaseModel):
    id: uuid.UUID
    destination_id: uuid.UUID
    destination_name: str
    amount_usd: float
    status: PurchaseStatus
    # Whether THIS purchase's cycle is still active (see
    # app/services/purchase_cycle.py) - a completed purchase can still show
    # up here after its cycle has lapsed, so the account page can tell the
    # user apart from "still unlocked".
    is_active: bool

    model_config = {"from_attributes": True}
