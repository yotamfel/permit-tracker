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


def send_contact_notification(admin_emails: list[str], name: str, from_email: str, message: str) -> None:
    if not admin_emails:
        return
    body = (
        f"<p><strong>{name}</strong> ({from_email}) sent a message via the contact form:</p>"
        f"<p>{message}</p>"
    )
    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": admin_emails,
            "subject": f"Permit Tracker contact form: {name}",
            "html": body,
        }
    )


def send_password_reset_email(to_email: str, reset_url: str) -> None:
    body = (
        f"<p>We received a request to reset your Permit Tracker password.</p>"
        f'<p><a href="{reset_url}">Click here to choose a new password</a>. This link expires in 1 hour.</p>'
        f"<p style='color:#777;font-size:12px'>If you didn't request this, you can safely ignore this email.</p>"
    )
    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [to_email],
            "subject": "Reset your Permit Tracker password",
            "html": body,
        }
    )


def send_post_release_feedback_email(to_email: str, destination_name: str, respond_url_base: str) -> None:
    yes_url = f"{respond_url_base}?succeeded=true"
    no_url = f"{respond_url_base}?succeeded=false"
    body = (
        f"<p>The application window for <strong>{destination_name}</strong> opened a day ago - did you get in?</p>"
        f'<p><a href="{yes_url}">Yes, I got it</a> &nbsp;|&nbsp; <a href="{no_url}">No, I missed it</a></p>'
        f"<p style='color:#777;font-size:12px'>Clicking either link takes you to a page with one more quick "
        f"question and an optional comment box.</p>"
    )
    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [to_email],
            "subject": f"How did it go with {destination_name}?",
            "html": body,
        }
    )


def send_contact_reply(to_email: str, to_name: str, original_message: str, reply_message: str) -> None:
    body = (
        f"<p>Hi {to_name},</p>"
        f"<p>{reply_message}</p>"
        f"<hr/>"
        f"<p style='color:#777;font-size:12px'>Your original message: {original_message}</p>"
    )
    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [to_email],
            "subject": "Re: your message to Permit Tracker",
            "html": body,
        }
    )
