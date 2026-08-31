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


def owned_destination_ids(db: Session, user_id: uuid.UUID | None) -> set[uuid.UUID]:
    """Batched version of user_owns_destination for list endpoints - one query
    instead of one-per-destination (was previously the dominant cost on
    /api/destinations for a logged-in user)."""
    if user_id is None:
        return set()
    rows = (
        db.query(Purchase.destination_id)
        .filter(Purchase.user_id == user_id, Purchase.status == PurchaseStatus.completed)
        .all()
    )
    return {r[0] for r in rows}
