from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 30

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_publishable_key: str = ""

    email_provider_api_key: str = ""
    email_from: str = "alerts@permit-tracker.example"

    frontend_url: str = "http://localhost:5173"
    # The backend's own public URL - needed to build absolute links in emails
    # that point back at backend-rendered pages (e.g. the no-login post-release
    # feedback response page), as opposed to frontend_url which is for links
    # into the SPA.
    backend_url: str = "http://localhost:8000"

    # Google Identity Services client ID - not a secret, but the backend needs it
    # to verify the "audience" claim on ID tokens it receives from the frontend.
    google_client_id: str = ""

    # English-only for now (multilingual support paused at the user's request - see
    # README.md). The translations table / mechanism_config / API all already support
    # arbitrary locales without code changes - this list is the only thing to extend
    # when translated content work resumes.
    default_locale: str = "en"
    supported_locales: list[str] = ["en"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
