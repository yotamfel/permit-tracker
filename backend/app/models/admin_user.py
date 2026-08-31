from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class AdminUser(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "admin_users"

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
