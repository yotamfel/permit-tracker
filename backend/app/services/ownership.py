import uuid

from sqlalchemy.orm import Session

from app.models.admin_user import AdminUser
from app.models.alert_subscription import AlertSubscription
from app.models.destination import Destination
from app.models.enums import PurchaseStatus
from app.models.purchase import Purchase
from app.models.user import User
from app.services.purchase_cycle import purchase_still_active


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
    # Most recent completed purchase - if an earlier one's cycle already
    # lapsed and the user bought again, the new purchase is what counts.
    purchase = (
        db.query(Purchase)
        .filter(
            Purchase.user_id == user.id,
            Purchase.destination_id == destination_id,
            Purchase.status == PurchaseStatus.completed,
        )
        .order_by(Purchase.created_at.desc())
        .first()
    )
    if purchase is None:
        return False
    destination = db.get(Destination, destination_id)
    subscription = (
        db.query(AlertSubscription)
        .filter(AlertSubscription.user_id == user.id, AlertSubscription.destination_id == destination_id)
        .first()
    )
    travel_date = subscription.travel_date if subscription else None
    return purchase_still_active(destination, purchase.created_at, travel_date)


def owned_destination_ids(db: Session, user: User | None, all_destination_ids: list[uuid.UUID]) -> set[uuid.UUID]:
    """Batched version of user_owns_destination for list endpoints - one round
    of queries instead of one-per-destination (was previously the dominant
    cost on /api/destinations for a logged-in user). For an admin, everything
    counts as owned, so all_destination_ids is returned as-is."""
    if user is None:
        return set()
    if is_admin(db, user):
        return set(all_destination_ids)

    purchases = (
        db.query(Purchase)
        .filter(Purchase.user_id == user.id, Purchase.status == PurchaseStatus.completed)
        .order_by(Purchase.created_at.desc())
        .all()
    )
    # Keep only the most recent purchase per destination.
    latest_purchase_by_destination = {}
    for p in purchases:
        latest_purchase_by_destination.setdefault(p.destination_id, p)
    if not latest_purchase_by_destination:
        return set()

    destinations = {
        d.id: d for d in db.query(Destination).filter(Destination.id.in_(latest_purchase_by_destination.keys())).all()
    }
    subscriptions = {
        s.destination_id: s
        for s in db.query(AlertSubscription)
        .filter(AlertSubscription.user_id == user.id, AlertSubscription.destination_id.in_(latest_purchase_by_destination.keys()))
        .all()
    }

    owned = set()
    for destination_id, purchase in latest_purchase_by_destination.items():
        destination = destinations.get(destination_id)
        if destination is None:
            continue
        subscription = subscriptions.get(destination_id)
        travel_date = subscription.travel_date if subscription else None
        if purchase_still_active(destination, purchase.created_at, travel_date):
            owned.add(destination_id)
    return owned
