import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.alert_subscription import AlertSubscription
from app.models.destination import Destination
from app.models.enums import MechanismType
from app.models.user import User
from app.schemas.subscription import SubscriptionCreateRequest, SubscriptionOut
from app.services.ownership import user_owns_destination

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

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

    if not user_owns_destination(db, user.id, d.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Purchase this destination to enable alerts")

    if d.mechanism_type in TRAVEL_DATE_REQUIRED_TYPES and body.travel_date is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"travel_date is required to set an alert for mechanism_type={d.mechanism_type.value}",
        )

    sub = AlertSubscription(
        user_id=user.id,
        destination_id=d.id,
        lead_time_days=body.lead_time_days,
        travel_date=body.travel_date,
        is_active=True,
    )
    db.add(sub)
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
