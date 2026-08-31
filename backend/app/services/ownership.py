import uuid

from sqlalchemy.orm import Session

from app.models.admin_user import AdminUser
from app.models.enums import PurchaseStatus
from app.models.purchase import Purchase
from app.models.user import User


def is_admin(db: Session, user: User | None) -> bool:
    """Admins can see every destination fully unlocked, without purchasing -
    needed to review/QA content before publishing it for real users."""
    if user is None:
        return False
    return db.query(AdminUser).filter(AdminUser.email == user.email).first() is not None


def user_owns_destination(db: Session, user: User | None, destination_id: uuid.UUID) -> bool:
    if user is None:
        return False
    if is_admin(db, user):
        return True
    return (
        db.query(Purchase)
        .filter(
            Purchase.user_id == user.id,
            Purchase.destination_id == destination_id,
            Purchase.status == PurchaseStatus.completed,
        )
        .first()
        is not None
    )


def owned_destination_ids(db: Session, user: User | None, all_destination_ids: list[uuid.UUID]) -> set[uuid.UUID]:
    """Batched version of user_owns_destination for list endpoints - one query
    instead of one-per-destination (was previously the dominant cost on
    /api/destinations for a logged-in user). For an admin, everything counts
    as owned, so all_destination_ids is returned as-is."""
    if user is None:
        return set()
    if is_admin(db, user):
        return set(all_destination_ids)
    rows = (
        db.query(Purchase.destination_id)
        .filter(Purchase.user_id == user.id, Purchase.status == PurchaseStatus.completed)
        .all()
    )
    return {r[0] for r in rows}
