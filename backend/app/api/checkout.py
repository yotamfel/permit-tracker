import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.alert_subscription import AlertSubscription
from app.models.destination import Destination
from app.models.enums import Platform, PurchaseStatus
from app.models.purchase import Purchase
from app.models.user import User
from app.schemas.purchase import CheckoutSessionOut, PurchaseOut
from app.services.purchase_cycle import purchase_still_active
from app.services.stripe_service import create_checkout_session

router = APIRouter(tags=["checkout"])


@router.post("/api/checkout/{destination_id}", response_model=CheckoutSessionOut)
def create_checkout(
    destination_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> CheckoutSessionOut:
    d = db.get(Destination, destination_id)
    if d is None or not d.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")

    # Only block re-purchase if a completed purchase is still within its
    # cycle - a lapsed one must NOT block buying again for the next cycle
    # (see app/services/purchase_cycle.py).
    latest_purchase = (
        db.query(Purchase)
        .filter(
            Purchase.user_id == user.id,
            Purchase.destination_id == destination_id,
            Purchase.status == PurchaseStatus.completed,
        )
        .order_by(Purchase.created_at.desc())
        .first()
    )
    if latest_purchase is not None:
        subscription = (
            db.query(AlertSubscription)
            .filter(AlertSubscription.user_id == user.id, AlertSubscription.destination_id == destination_id)
            .first()
        )
        travel_date = subscription.travel_date if subscription else None
        if purchase_still_active(
            d, latest_purchase.created_at, travel_date, admin_override_until=latest_purchase.admin_override_until
        ):
            raise HTTPException(status.HTTP_409_CONFLICT, "Destination already unlocked")

    checkout_url = create_checkout_session(
        destination_id=str(d.id),
        destination_name=d.name,
        price_usd=float(d.price_usd),
        user_id=str(user.id),
        user_email=user.email,
    )

    pending = Purchase(
        user_id=user.id,
        destination_id=d.id,
        platform=Platform.web,
        amount_usd=d.price_usd,
        status=PurchaseStatus.pending,
    )
    db.add(pending)
    db.commit()

    return CheckoutSessionOut(checkout_url=checkout_url)


@router.get("/api/me/purchases", response_model=list[PurchaseOut])
def list_my_purchases(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[PurchaseOut]:
    purchases = (
        db.query(Purchase)
        .filter(Purchase.user_id == user.id, Purchase.status == PurchaseStatus.completed)
        .order_by(Purchase.created_at.desc())
        .all()
    )
    out = []
    for p in purchases:
        d = db.get(Destination, p.destination_id)
        subscription = (
            db.query(AlertSubscription)
            .filter(AlertSubscription.user_id == user.id, AlertSubscription.destination_id == p.destination_id)
            .first()
        )
        travel_date = subscription.travel_date if subscription else None
        is_active = (
            purchase_still_active(d, p.created_at, travel_date, admin_override_until=p.admin_override_until)
            if d is not None
            else False
        )
        out.append(
            PurchaseOut(
                id=p.id,
                destination_id=p.destination_id,
                destination_name=d.name if d else "",
                amount_usd=float(p.amount_usd),
                status=p.status,
                is_active=is_active,
            )
        )
    return out
