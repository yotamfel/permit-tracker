from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import ThemePreference
from app.models.mixins import TimestampMixin, UUIDPKMixin


class User(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    preferred_locale: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    theme_preference: Mapped[ThemePreference] = mapped_column(
        Enum(ThemePreference, name="theme_preference"), nullable=False, default=ThemePreference.system
    )
    password_reset_token: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Proof of Terms of Service / Privacy Policy acceptance at signup - kept
    # for legal recordkeeping. terms_version lets us tell which version of
    # the terms a given user actually agreed to if they're revised later.
    terms_accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    terms_version: Mapped[str | None] = mapped_column(String, nullable=True)
