import resend

from app.core.config import get_settings

settings = get_settings()
resend.api_key = settings.email_provider_api_key


def send_alert_email(to_email: str, destination_name: str, body_html: str) -> None:
    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [to_email],
            "subject": f"Permit Tracker alert: {destination_name}",
            "html": body_html,
        }
    )
