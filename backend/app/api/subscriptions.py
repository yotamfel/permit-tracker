import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.alert_subscription import AlertSubscription
from app.models.destination import Destination
from app.models.enums import MechanismType, PurchaseStatus
from app.models.purchase import Purchase
from app.models.user import User
from app.schemas.subscription import LEAD_TIME_PRESET_MINUTES, SubscriptionCreateRequest, SubscriptionListOut, SubscriptionOut
from app.services.ownership import user_owns_destination

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

# Once this many days have passed since the purchase that unlocked a
# no-fixed-date destination, the user can no longer self-service set or
# change their travel_date - doing so would let them keep pushing the date
# forward forever and extend a single $6.99 purchase's access indefinitely
# (purchase_cycle.py recomputes the 60-day window live off whatever
# travel_date is currently on file). Past this window, they have to contact
# support so an admin can review and apply a manual override
# (POST /admin/api/purchases/{id}/override) instead.
TRAVEL_DATE_EDIT_WINDOW_DAYS = 7


@router.get("", response_model=list[SubscriptionListOut])
def list_my_subscriptions(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[SubscriptionListOut]:
    subs = db.query(AlertSubscription).filter(AlertSubscription.user_id == user.id).all()
    out = []
    for s in subs:
        d = db.get(Destination, s.destination_id)
        out.append(
            SubscriptionListOut(
                id=s.id,
                destination_id=s.destination_id,
                destination_name=d.name if d else "(deleted destination)",
                lead_time_minutes_list=s.lead_time_minutes_list,
                is_active=s.is_active,
                travel_date=s.travel_date,
            )
        )
    return out

# Mechanism types with no fixed calendar release date - alerting for these requires
# a user-supplied travel_date to compute "book early" reminders against.
TRAVEL_DATE_REQUIRED_TYPES = {
    MechanismType.guided_tour_only,
    MechanismType.first_come_first_served,
    MechanismType.single_operator_annual_quota,
    MechanismType.fixed_daily_quota,
    MechanismType.rolling_window,
}


@router.post("", response_model=SubscriptionOut)
def create_subscription(
    body: SubscriptionCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> SubscriptionOut:
    d = db.get(Destination, body.destination_id)
    if d is None or not d.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")

    if not user_owns_destination(db, user, d.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Purchase this destination to enable alerts")

    if d.mechanism_type in TRAVEL_DATE_REQUIRED_TYPES and body.travel_date is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"travel_date is required to set an alert for mechanism_type={d.mechanism_type.value}",
        )

    if not body.lead_time_minutes_list:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Select at least one lead time")
    if not set(body.lead_time_minutes_list) <= LEAD_TIME_PRESET_MINUTES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "lead_time_minutes_list must only contain offered presets")

    # Upsert: one alert per user+destination (see the unique constraint on the
    # model) - re-submitting (including a double-submit race on the button)
    # updates the existing alert instead of creating a duplicate.
    sub = db.query(AlertSubscription).filter_by(user_id=user.id, destination_id=d.id).first()

    if d.mechanism_type in TRAVEL_DATE_REQUIRED_TYPES and body.travel_date != (sub.travel_date if sub else None):
        purchase = (
            db.query(Purchase)
            .filter(
                Purchase.user_id == user.id,
                Purchase.destination_id == d.id,
                Purchase.status == PurchaseStatus.completed,
            )
            .order_by(Purchase.created_at.desc())
            .first()
        )
        if purchase is not None and datetime.now(timezone.utc) > purchase.created_at + timedelta(days=TRAVEL_DATE_EDIT_WINDOW_DAYS):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Your travel date can only be set or changed within {TRAVEL_DATE_EDIT_WINDOW_DAYS} days of "
                "purchase. Contact us via the Contact page to update it after that.",
            )

    if sub is None:
        sub = AlertSubscription(user_id=user.id, destination_id=d.id)
        db.add(sub)
    sub.lead_time_minutes_list = sorted(set(body.lead_time_minutes_list))
    sub.travel_date = body.travel_date
    sub.is_active = True
    db.commit()
    db.refresh(sub)
    return SubscriptionOut.model_validate(sub)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    sub = db.get(AlertSubscription, subscription_id)
    if sub is None or sub.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subscription not found")
    db.delete(sub)
    db.commit()
