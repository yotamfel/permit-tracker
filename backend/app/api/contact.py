import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_db, get_optional_current_user
from app.core.rate_limit import limiter
from app.models.admin_user import AdminUser
from app.models.contact_message import ContactMessage
from app.models.destination import Destination
from app.models.user import User
from app.schemas.contact import ContactMessageCreate
from app.services.email_service import send_contact_notification

router = APIRouter(prefix="/api/contact", tags=["contact"])
logger = logging.getLogger(__name__)
settings = get_settings()


@router.post("", status_code=201)
@limiter.limit("5/minute")
def submit_contact_message(
    request: Request,
    body: ContactMessageCreate,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_current_user),
) -> dict:
    destination_name = None
    if body.destination_id is not None:
        d = db.get(Destination, body.destination_id)
        destination_name = d.name if d else None

    msg = ContactMessage(
        name=body.name,
        email=body.email,
        message=body.message,
        user_id=user.id if user else None,
        destination_id=body.destination_id,
    )
    db.add(msg)
    db.commit()

    try:
        admin_emails = [a.email for a in db.query(AdminUser).all()]
        send_contact_notification(admin_emails, body.name, body.email, body.message, destination_name)
    except Exception:
        # The message is already saved and visible in the admin panel either
        # way - a failed notification email shouldn't fail the submission.
        logger.exception("Failed to send contact notification email")

    return {"status": "received"}
