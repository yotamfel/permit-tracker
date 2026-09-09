from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Defensive: Railway's DATABASE_URL for one specific service (serene-success /
# monitor_destinations) has repeatedly reverted to a value missing its scheme
# prefix ("//user:pass@host/db" instead of "postgresql+psycopg://user:pass@host/db"),
# cause not confirmed - crashes create_engine() with ArgumentError otherwise.
# Repair it here so a bad env var degrades to "still works" rather than a
# crash-looping cron job.
database_url = settings.database_url
if database_url.startswith("//"):
    database_url = "postgresql+psycopg:" + database_url

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
