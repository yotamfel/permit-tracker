import uuid

from pydantic import BaseModel

from app.models.enums import PurchaseStatus


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
