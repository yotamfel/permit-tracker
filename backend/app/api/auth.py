from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import GoogleAuthRequest, LoginRequest, MeOut, MeUpdateRequest, SignupRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
me_router = APIRouter(prefix="/api/me", tags=["me"])
settings = get_settings()


@router.post("/signup", response_model=TokenResponse)
def signup(body: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(User).filter(User.email == body.email).first()
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == body.email).first()
    if user is None or user.password_hash is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/google", response_model=TokenResponse)
def google_login(body: GoogleAuthRequest, db: Session = Depends(get_db)) -> TokenResponse:
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
        # password_hash stays null - this account can only log in via Google
        # unless/until the user separately sets a password.
        user = User(email=email, password_hash=None)
        db.add(user)
        db.commit()
        db.refresh(user)

    return TokenResponse(access_token=create_access_token(user.id))


@me_router.get("", response_model=MeOut)
def get_me(user: User = Depends(get_current_user)) -> MeOut:
    return MeOut.model_validate(user)


@me_router.patch("", response_model=MeOut)
def update_me(body: MeUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MeOut:
    if body.preferred_locale is not None:
        user.preferred_locale = body.preferred_locale
    if body.theme_preference is not None:
        user.theme_preference = body.theme_preference
    db.add(user)
    db.commit()
    db.refresh(user)
    return MeOut.model_validate(user)
