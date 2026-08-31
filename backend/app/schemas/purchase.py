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

    model_config = {"from_attributes": True}
