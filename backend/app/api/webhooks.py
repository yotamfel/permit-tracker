import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_db
from app.models.alert_subscription import AlertSubscription
from app.models.destination import Destination
from app.models.destination_operator import DestinationOperator
from app.models.enums import PurchaseStatus
from app.models.purchase import Purchase
from app.models.user import User
from app.services.email_service import send_purchase_confirmation_email
from app.services.paddle_service import verify_webhook_signature
from app.services.purchase_cycle import purchase_active_until
from app.services.referral import ensure_referral_code

settings = get_settings()

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/paddle")
async def paddle_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    payload = await request.body()
    signature_header = request.headers.get("paddle-signature", "")

    if not verify_webhook_signature(payload, signature_header):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid webhook signature")

    event = (await request.json()) if payload else {}
    event_type = event.get("event_type")

    if event_type == "transaction.completed":
        return _handle_transaction_completed(event, db)
    if event_type in ("transaction.payment_failed",):
        return _handle_payment_failed(event, db)
    if event_type == "adjustment.updated":
        return _handle_adjustment_updated(event, db)

    return {"status": "ignored"}


def _handle_transaction_completed(event: dict, db: Session) -> dict:
    data = event.get("data", {})
    transaction_id = data.get("id")
    custom_data = data.get("custom_data") or {}
    user_id = custom_data.get("user_id")
    destination_id = custom_data.get("destination_id")

    if not transaction_id or not user_id or not destination_id:
        logger.warning("Paddle webhook missing required custom_data: %s", transaction_id)
        return {"status": "ignored_missing_metadata"}

    # Idempotency: if we've already recorded this transaction as completed, no-op.
    existing = db.query(Purchase).filter(Purchase.paddle_transaction_id == transaction_id).first()
    if existing is not None:
        return {"status": "already_processed"}

    pending = (
        db.query(Purchase)
        .filter(
            Purchase.user_id == uuid.UUID(user_id),
            Purchase.destination_id == uuid.UUID(destination_id),
            Purchase.status == PurchaseStatus.pending,
        )
        .order_by(Purchase.created_at.desc())
        .first()
    )
    if pending is None:
        # No matching pending row (shouldn't normally happen) - create one directly.
        amount_minor = 0
        totals = data.get("details", {}).get("totals", {})
        if totals.get("total") is not None:
            amount_minor = int(totals["total"])
        pending = Purchase(
            user_id=uuid.UUID(user_id),
            destination_id=uuid.UUID(destination_id),
            amount_usd=amount_minor / 100,
        )
        db.add(pending)

    pending.status = PurchaseStatus.completed
    pending.paddle_transaction_id = transaction_id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Concurrent webhook delivery already inserted this transaction_id.
        return {"status": "already_processed"}

    buyer = db.get(User, uuid.UUID(user_id))
    if buyer is not None:
        ensure_referral_code(db, buyer)
        try:
            _send_purchase_confirmation(db, buyer, pending)
        except Exception:
            logger.exception("Failed to send purchase confirmation email for purchase %s", pending.id)

    return {"status": "completed"}


def _send_purchase_confirmation(db: Session, buyer: User, purchase: Purchase) -> None:
    destination = db.get(Destination, purchase.destination_id)
    if destination is None:
        return

    subscription = (
        db.query(AlertSubscription)
        .filter(AlertSubscription.user_id == buyer.id, AlertSubscription.destination_id == destination.id)
        .first()
    )
    travel_date = subscription.travel_date if subscription else None
    access_until = purchase_active_until(
        destination, purchase.created_at, travel_date, admin_override_until=purchase.admin_override_until
    )
    days_remaining = max((access_until - datetime.now(timezone.utc)).days, 0)

    operators = None
    if not destination.application_url:
        operators = [
            {"name": o.name, "url": o.url}
            for o in db.query(DestinationOperator)
            .filter(DestinationOperator.destination_id == destination.id)
            .order_by(DestinationOperator.order_index)
            .all()
        ]

    send_purchase_confirmation_email(
        buyer.email,
        destination.name,
        float(purchase.amount_usd),
        f"{settings.frontend_url}/destinations/{destination.id}",
        days_remaining,
        application_url=destination.application_url,
        operators=operators,
        referral_code=buyer.referral_code,
    )


def _handle_payment_failed(event: dict, db: Session) -> dict:
    data = event.get("data", {})
    custom_data = data.get("custom_data") or {}
    user_id = custom_data.get("user_id")
    destination_id = custom_data.get("destination_id")
    if not user_id or not destination_id:
        return {"status": "ignored_missing_metadata"}

    pending = (
        db.query(Purchase)
        .filter(
            Purchase.user_id == uuid.UUID(user_id),
            Purchase.destination_id == uuid.UUID(destination_id),
            Purchase.status == PurchaseStatus.pending,
        )
        .order_by(Purchase.created_at.desc())
        .first()
    )
    if pending is None:
        return {"status": "ignored_no_pending_purchase"}

    pending.status = PurchaseStatus.failed
    db.add(pending)
    db.commit()
    return {"status": "failed"}


def _handle_adjustment_updated(event: dict, db: Session) -> dict:
    """A refund or chargeback only actually returns money once its adjustment
    reaches status "approved" (most refunds start "pending_approval" and are
    reviewed by Paddle) - acting on adjustment.created would revoke access on
    a refund request that could still be rejected. Reaching this point means
    the money came back, so revoke access by marking the purchase refunded;
    the ownership checks (see app/services/ownership.py) only ever consider
    completed purchases, so this takes effect immediately without any other
    code change. A chargeback_reverse (Paddle successfully contested a
    chargeback) means the money came back to us, so access is restored."""
    data = event.get("data", {})
    transaction_id = data.get("transaction_id")
    action = data.get("action")
    status_ = data.get("status")
    if not transaction_id:
        return {"status": "ignored_missing_transaction_id"}

    purchase = db.query(Purchase).filter(Purchase.paddle_transaction_id == transaction_id).first()
    if purchase is None:
        logger.warning("Paddle adjustment for unknown transaction %s", transaction_id)
        return {"status": "ignored_unknown_purchase"}

    if status_ != "approved" or action not in ("refund", "chargeback", "chargeback_reverse"):
        return {"status": "ignored"}

    new_status = PurchaseStatus.completed if action == "chargeback_reverse" else PurchaseStatus.refunded
    if purchase.status == new_status:
        return {"status": "already_processed"}

    purchase.status = new_status
    db.add(purchase)
    db.commit()
    logger.info("Purchase %s set to %s (Paddle %s on transaction %s)", purchase.id, new_status, action, transaction_id)
    return {"status": new_status.value}
