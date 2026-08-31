import logging
import uuid

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.enums import PurchaseStatus
from app.models.purchase import Purchase
from app.services.stripe_service import construct_webhook_event

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = construct_webhook_event(payload, sig_header)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid webhook signature: {exc}") from exc

    if event["type"] != "checkout.session.completed":
        return {"status": "ignored"}

    session = event["data"]["object"]
    payment_intent_id = session.get("payment_intent")
    metadata = session.get("metadata", {})
    user_id = metadata.get("user_id")
    destination_id = metadata.get("destination_id")

    if not payment_intent_id or not user_id or not destination_id:
        logger.warning("Stripe webhook missing required metadata: %s", session.get("id"))
        return {"status": "ignored_missing_metadata"}

    # Idempotency: if we've already recorded this payment_intent as completed, no-op.
    existing = db.query(Purchase).filter(Purchase.stripe_payment_intent_id == payment_intent_id).first()
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
        pending = Purchase(
            user_id=uuid.UUID(user_id),
            destination_id=uuid.UUID(destination_id),
            amount_usd=(session.get("amount_total") or 0) / 100,
        )
        db.add(pending)

    pending.status = PurchaseStatus.completed
    pending.stripe_payment_intent_id = payment_intent_id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Concurrent webhook delivery already inserted this payment_intent_id.
        return {"status": "already_processed"}

    return {"status": "completed"}
