import uuid

from sqlalchemy.orm import Session

from app.models.enums import PurchaseStatus
from app.models.purchase import Purchase


def user_owns_destination(db: Session, user_id: uuid.UUID | None, destination_id: uuid.UUID) -> bool:
    if user_id is None:
        return False
    return (
        db.query(Purchase)
        .filter(
            Purchase.user_id == user_id,
            Purchase.destination_id == destination_id,
            Purchase.status == PurchaseStatus.completed,
        )
        .first()
        is not None
    )
