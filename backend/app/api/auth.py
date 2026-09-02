import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db
from app.core.rate_limit import limiter
from app.core.security import create_access_token, hash_password, verify_password
from app.models.admin_user import AdminUser
from app.models.contact_message import ContactMessage
from app.models.user import User
from app.schemas.auth import (
    DeleteAccountRequest,
    ForgotPasswordRequest,
    GoogleAuthRequest,
    LoginRequest,
    MeOut,
    MeUpdateRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
)
from app.services.email_service import send_contact_notification, send_password_reset_email
from app.services.ownership import is_admin

router = APIRouter(prefix="/api/auth", tags=["auth"])
me_router = APIRouter(prefix="/api/me", tags=["me"])
settings = get_settings()
logger = logging.getLogger(__name__)
RESET_TOKEN_TTL = timedelta(hours=1)
# Bump this (and record the change in the Terms/Privacy pages) whenever the
# terms materially change, so terms_version tells us which text a given user
# actually agreed to.
CURRENT_TERMS_VERSION = "2026-09-01"


@router.post("/signup", response_model=TokenResponse)
@limiter.limit("5/minute")
def signup(request: Request, body: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    if not body.terms_accepted:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You must accept the Terms of Service and Privacy Policy")
    existing = db.query(User).filter(User.email == body.email).first()
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        terms_accepted_at=datetime.now(timezone.utc),
        terms_version=CURRENT_TERMS_VERSION,
        country=body.country,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == body.email).first()
    if user is None or user.password_hash is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/google", response_model=TokenResponse)
@limiter.limit("10/minute")
def google_login(request: Request, body: GoogleAuthRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        payload = google_id_token.verify_oauth2_token(
            body.credential, google_requests.Request(), settings.google_client_id
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Google credential") from exc

    email = payload.get("email")
    if not email or not payload.get("email_verified"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Google account has no verified email")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        if not body.terms_accepted:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "No account found for this Google account. Please sign up and accept the Terms of Service to create one.",
            )
        # password_hash stays null - this account can only log in via Google
        # unless/until the user separately sets a password.
        user = User(
            email=email,
            password_hash=None,
            terms_accepted_at=datetime.now(timezone.utc),
            terms_version=CURRENT_TERMS_VERSION,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(request: Request, body: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.email == body.email).first()
    if user is not None:
        token = secrets.token_urlsafe(32)
        user.password_reset_token = token
        user.password_reset_expires_at = datetime.now(timezone.utc) + RESET_TOKEN_TTL
        db.add(user)
        db.commit()

        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        try:
            send_password_reset_email(user.email, reset_url)
        except Exception:
            logger.exception("Failed to send password reset email to %s", user.email)

    # Always return the same response whether or not the email exists, so this
    # endpoint can't be used to check which emails have accounts.
    return {"status": "if that email exists, a reset link was sent"}


@router.post("/reset-password", response_model=TokenResponse)
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.password_reset_token == body.token).first()
    if (
        user is None
        or user.password_reset_expires_at is None
        or user.password_reset_expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired reset link")

    user.password_hash = hash_password(body.new_password)
    user.password_reset_token = None
    user.password_reset_expires_at = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))


@me_router.get("", response_model=MeOut)
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MeOut:
    out = MeOut.model_validate(user)
    out.is_admin = is_admin(db, user)
    return out


@me_router.patch("", response_model=MeOut)
def update_me(body: MeUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MeOut:
    if body.preferred_locale is not None:
        user.preferred_locale = body.preferred_locale
    if body.theme_preference is not None:
        user.theme_preference = body.theme_preference
    if body.country is not None:
        user.country = body.country
    db.add(user)
    db.commit()
    db.refresh(user)
    out = MeOut.model_validate(user)
    out.is_admin = is_admin(db, user)
    return out


@me_router.post("/delete-account-request", status_code=status.HTTP_201_CREATED)
def request_account_deletion(
    body: DeleteAccountRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    """Self-service deletion is deliberately NOT instant - purchases carry
    financial/accounting records the business needs to keep, and User has
    several ondelete=CASCADE relationships that would silently wipe them.
    This raises a flagged request for the admin to process by hand (matches
    what the Privacy Policy already tells users to expect)."""
    message = f"ACCOUNT DELETION REQUEST from {user.email} (user_id={user.id})."
    if body.reason:
        message += f"\n\nReason given: {body.reason}"
    msg = ContactMessage(name=user.email, email=user.email, message=message, user_id=user.id)
    db.add(msg)
    db.commit()

    try:
        admin_emails = [a.email for a in db.query(AdminUser).all()]
        send_contact_notification(admin_emails, user.email, user.email, message)
    except Exception:
        logger.exception("Failed to send account-deletion-request notification for %s", user.id)

    return {"status": "received"}
