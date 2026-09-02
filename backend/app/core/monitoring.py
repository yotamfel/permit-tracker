"""
Error monitoring - inactive (no-op) until SENTRY_DSN is set, so this is safe
to import from anywhere (the FastAPI app, or a standalone cron job script)
without configuring anything first.

Call init_sentry() once, as early as possible, from both app/main.py (for
API request errors) and each app/jobs/*.py script's __main__ block (for cron
job failures, which used to fail silently - see the JWT_SECRET incident on
dispatch-follow-up-reminders).
"""
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
_initialized = False


def init_sentry() -> None:
    global _initialized
    if _initialized:
        return
    settings = get_settings()
    if not settings.sentry_dsn:
        return
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=0.1,
        # Sentry's own default for this project - includes request headers,
        # IP, and user info on captured errors to make them easier to debug.
        # See https://docs.sentry.io/platforms/python/data-management/data-collected/
        send_default_pii=True,
    )
    _initialized = True
    logger.info("Sentry initialized (environment=%s)", settings.environment)
