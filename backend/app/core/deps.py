from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db import get_db
from app.models.admin_user import AdminUser
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)
settings = get_settings()


def get_locale(locale: str | None = Query(default=None)) -> str:
    if locale and locale in settings.supported_locales:
        return locale
    return settings.default_locale


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        return None
    return db.get(User, user_id)


def get_current_admin(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    is_admin = db.query(AdminUser).filter(AdminUser.email == user.email).first()
    if is_admin is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user
