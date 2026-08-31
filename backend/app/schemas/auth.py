import uuid

from pydantic import BaseModel, EmailStr

from app.models.enums import ThemePreference


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    credential: str  # the ID token JWT from Google Identity Services


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    id: uuid.UUID
    email: str
    preferred_locale: str
    theme_preference: ThemePreference

    model_config = {"from_attributes": True}


class MeUpdateRequest(BaseModel):
    preferred_locale: str | None = None
    theme_preference: ThemePreference | None = None
