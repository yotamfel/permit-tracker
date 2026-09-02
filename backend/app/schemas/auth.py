import uuid

from pydantic import BaseModel, EmailStr

from app.models.enums import ThemePreference


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    # Must be true - enforced in the endpoint, not just here, so the error
    # message can be specific ("please accept the terms") rather than a
    # generic 422.
    terms_accepted: bool = False
    country: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    credential: str  # the ID token JWT from Google Identity Services
    # Only meaningful (and required) when this Google sign-in is creating a
    # brand-new account; ignored for an existing user logging back in.
    terms_accepted: bool = False


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
    is_admin: bool = False

    model_config = {"from_attributes": True}


class MeUpdateRequest(BaseModel):
    preferred_locale: str | None = None
    theme_preference: ThemePreference | None = None
