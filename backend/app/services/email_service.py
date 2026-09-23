import html
from datetime import datetime

import resend

from app.core.config import get_settings

settings = get_settings()
resend.api_key = settings.email_provider_api_key

# Bare "from": settings.email_from has no display name, so most mail clients
# fall back to showing the address's local-part (e.g. "alerts") as the
# sender name instead of the brand.
_FROM = f"SlotScout <{settings.email_from}>"

_FONT = "-apple-system,Segoe UI,Helvetica,Arial,sans-serif"
_TEXT_STYLE = f"margin:0 0 16px;font-size:15px;line-height:1.5;color:#1c1917;font-family:{_FONT}"
_MUTED_STYLE = f"margin:0;font-size:12px;color:#a8a29e;font-family:{_FONT}"


def _wrap_email(inner_html: str) -> str:
    """Shared branded shell (dark header + white card) every outgoing email
    renders inside - table-based layout for compatibility with email clients
    that don't support flexbox/grid (notably Outlook)."""
    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f4;padding:32px 16px">
      <tr><td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:480px;background:#ffffff;border-radius:16px;overflow:hidden;font-family:{_FONT}">
          <tr><td style="background:#292524;padding:20px 24px">
            <span style="font-size:18px;font-weight:700;color:#ffffff">\U0001F9ED SlotScout</span>
          </td></tr>
          <tr><td style="padding:28px 24px 24px">
            {inner_html}
          </td></tr>
        </table>
      </td></tr>
    </table>
    """


def _button(url: str, label: str) -> str:
    return f"""
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 16px">
      <tr><td style="border-radius:999px;background:#d97706">
        <a href="{url}" style="display:inline-block;padding:10px 20px;font-size:14px;font-weight:600;color:#ffffff;text-decoration:none;font-family:{_FONT}">{label}</a>
      </td></tr>
    </table>
    """


def send_alert_email(to_email: str, destination_name: str, body_html: str) -> None:
    resend.Emails.send(
        {
            "from": _FROM,
            "to": [to_email],
            "subject": f"SlotScout alert: {destination_name}",
            "html": _wrap_email(body_html),
        }
    )


def send_contact_notification(
    admin_emails: list[str], name: str, from_email: str, message: str, destination_name: str | None = None
) -> None:
    if not admin_emails:
        return
    safe_name = html.escape(name)
    safe_from_email = html.escape(from_email)
    safe_message = html.escape(message)
    urgent_line = (
        f"<p style='{_TEXT_STYLE}'><strong>URGENT - sent from the {html.escape(destination_name)} page.</strong></p>"
        if destination_name
        else ""
    )
    body = (
        f"{urgent_line}"
        f"<p style='{_TEXT_STYLE}'><strong>{safe_name}</strong> ({safe_from_email}) sent a message via the contact form:</p>"
        f"<p style='{_TEXT_STYLE}'>{safe_message}</p>"
    )
    subject = (
        f"[URGENT - {destination_name}] SlotScout contact form: {name}"
        if destination_name
        else f"SlotScout contact form: {name}"
    )
    resend.Emails.send(
        {
            "from": _FROM,
            "to": admin_emails,
            "subject": subject,
            "html": _wrap_email(body),
        }
    )


def send_password_reset_email(to_email: str, reset_url: str) -> None:
    body = (
        f"<p style='{_TEXT_STYLE}'>We received a request to reset your SlotScout password.</p>"
        f"{_button(reset_url, 'Choose a new password')}"
        f"<p style='{_MUTED_STYLE}'>This link expires in 1 hour. If you didn't request this, you can safely "
        f"ignore this email.</p>"
    )
    resend.Emails.send(
        {
            "from": _FROM,
            "to": [to_email],
            "subject": "Reset your SlotScout password",
            "html": _wrap_email(body),
        }
    )


def send_post_release_feedback_email(to_email: str, destination_name: str, respond_url_base: str) -> None:
    yes_url = f"{respond_url_base}?succeeded=true"
    no_url = f"{respond_url_base}?succeeded=false"
    body = (
        f"<p style='{_TEXT_STYLE}'>The application window for <strong>{destination_name}</strong> opened a day "
        f"ago - did you get in?</p>"
        f'<p style="margin:0 0 16px"><a href="{yes_url}" style="color:#d97706;font-weight:600;text-decoration:none">Yes, I got it</a>'
        f'&nbsp;&nbsp;|&nbsp;&nbsp;<a href="{no_url}" style="color:#78716c;font-weight:600;text-decoration:none">No, I missed it</a></p>'
        f"<p style='{_MUTED_STYLE}'>Clicking either link takes you to a page with one more quick question and "
        f"an optional comment box.</p>"
    )
    resend.Emails.send(
        {
            "from": _FROM,
            "to": [to_email],
            "subject": f"How did it go with {destination_name}?",
            "html": _wrap_email(body),
        }
    )


def send_source_fetch_failure_email(admin_emails: list[str], destination_name: str, source_url: str, error: str) -> None:
    if not admin_emails:
        return
    body = (
        f"<p style='{_TEXT_STYLE}'>The weekly monitoring job couldn't fetch the source page for "
        f"<strong>{destination_name}</strong> - it may be blocking automated requests, or the URL may have "
        f"changed or broken.</p>"
        f"<p style='{_TEXT_STYLE}'><strong>Source:</strong> {source_url}<br/><strong>Error:</strong> {error}</p>"
        f"<p style='{_TEXT_STYLE}'>Automated change-detection won't work for this destination until this is "
        f'resolved. It now shows under "Needs manual check" in the admin Monitoring diffs tab - worth checking '
        f"it by hand periodically, or fixing/replacing the source URL if it's simply wrong.</p>"
    )
    resend.Emails.send(
        {
            "from": _FROM,
            "to": admin_emails,
            "subject": f"SlotScout: can't monitor {destination_name} automatically",
            "html": _wrap_email(body),
        }
    )


def send_follow_up_reminder_email(admin_emails: list[str], items: list[dict]) -> None:
    """items: list of {destination_name, title, notes} due today."""
    if not admin_emails or not items:
        return
    rows = "".join(
        f"<li style='margin-bottom:8px'><strong>{i['destination_name']}</strong> - {i['title']}"
        + (f"<br/><span style='color:#78716c;font-size:13px'>{i['notes']}</span>" if i.get("notes") else "")
        + "</li>"
        for i in items
    )
    body = (
        f"<p style='{_TEXT_STYLE}'>You scheduled these for today - worth checking:</p>"
        f"<ul style='margin:0 0 16px;padding-left:20px;font-size:15px;line-height:1.5;color:#1c1917;font-family:{_FONT}'>{rows}</ul>"
    )
    resend.Emails.send(
        {
            "from": _FROM,
            "to": admin_emails,
            "subject": f"SlotScout: {len(items)} follow-up{'s' if len(items) != 1 else ''} due today",
            "html": _wrap_email(body),
        }
    )


def send_destination_updated_email(to_email: str, destination_name: str, diff_summary: str) -> None:
    body = (
        f"<p style='{_TEXT_STYLE}'>Something changed on <strong>{destination_name}</strong>, a destination "
        f"you've unlocked - here's what's new:</p>"
        f"<pre style='white-space:pre-wrap;font-size:13px;background:#f5f5f4;padding:12px;border-radius:8px;"
        f"font-family:{_FONT};color:#1c1917;margin:0 0 16px'>{html.escape(diff_summary)}</pre>"
        f"<p style='{_MUTED_STYLE}'>This is a one-off update notice, separate from your regular pre-release "
        f"alert.</p>"
    )
    resend.Emails.send(
        {
            "from": _FROM,
            "to": [to_email],
            "subject": f"SlotScout: {destination_name} was updated",
            "html": _wrap_email(body),
        }
    )


def send_purchase_confirmation_email(
    to_email: str,
    destination_name: str,
    checklist_url: str,
    access_until: datetime,
    referral_code: str | None = None,
) -> None:
    referral_block = (
        f"""
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:8px;background:#fffbeb;border:1px solid #fde68a;border-radius:12px">
          <tr><td style="padding:16px 20px;font-family:{_FONT};font-size:14px;color:#78350f">
            Traveling with friends? Give them this code for <strong>$3.99</strong> instead of $6.99 on any
            destination (good for up to 3 uses):
            <div style="margin-top:8px;font-size:18px;font-weight:700;letter-spacing:1px;color:#92400e">{referral_code}</div>
          </td></tr>
        </table>
        """
        if referral_code
        else ""
    )
    body = (
        f"<p style='{_TEXT_STYLE}'>Hey! Your <strong>{destination_name}</strong> checklist is unlocked and ready "
        f"to go.</p>"
        f"{_button(checklist_url, 'View your checklist')}"
        f"<p style='margin:0;font-size:14px;color:#57534e;font-family:{_FONT}'>Your access is open until "
        f"<strong>{access_until.strftime('%B %d, %Y')}</strong>.</p>"
        f"{referral_block}"
        f"<p style='{_MUTED_STYLE};margin-top:16px'>Questions? Just reply to this email or use the contact form "
        f"on the site.</p>"
    )
    resend.Emails.send(
        {
            "from": _FROM,
            "to": [to_email],
            "subject": f"You're all set for {destination_name}",
            "html": _wrap_email(body),
        }
    )


def send_contact_reply(to_email: str, to_name: str, original_message: str, reply_message: str) -> None:
    safe_to_name = html.escape(to_name)
    safe_reply_message = html.escape(reply_message)
    safe_original_message = html.escape(original_message)
    body = (
        f"<p style='{_TEXT_STYLE}'>Hi {safe_to_name},</p>"
        f"<p style='{_TEXT_STYLE}'>{safe_reply_message}</p>"
        f"<hr style='border:none;border-top:1px solid #e7e5e4;margin:0 0 16px'/>"
        f"<p style='{_MUTED_STYLE}'>Your original message: {safe_original_message}</p>"
    )
    resend.Emails.send(
        {
            "from": _FROM,
            "to": [to_email],
            "subject": "Re: your message to SlotScout",
            "html": _wrap_email(body),
        }
    )


_URGENCY_DOT = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def send_admin_weekly_digest_email(
    admin_emails: list[str],
    pending_diffs: list[dict],
    failing_sources: list[dict],
    follow_ups: list[dict],
    open_inquiries_count: int,
) -> None:
    """Weekly "what needs your attention" summary for admins - see
    app/jobs/dispatch_admin_weekly_digest.py for what populates each list.

    pending_diffs: [{destination_id, destination_name, unreadable: bool}]
    failing_sources: [{destination_id, destination_name, days_failing: int|None, urgency: "high"|"medium"|"low"}]
    follow_ups: [{destination_id, destination_name, title, notes, due_str, overdue: bool}]
    """
    if not admin_emails or not (pending_diffs or failing_sources or follow_ups or open_inquiries_count):
        return

    def _dest_link(destination_id) -> str:
        return f"{settings.frontend_url}/admin/destinations/{destination_id}"

    sections = []

    if pending_diffs:
        rows = "".join(
            f"<li style='margin-bottom:8px'><a href='{_dest_link(d['destination_id'])}' "
            f"style='color:#b45309'>{html.escape(d['destination_name'])}</a>"
            + (
                " <span style='color:#dc2626;font-weight:600'>- no readable diff, check the source manually</span>"
                if d.get("unreadable")
                else " - review the change on the Monitoring tab"
            )
            + "</li>"
            for d in pending_diffs
        )
        sections.append(
            f"<h3 style='margin:0 0 6px;font-size:15px;color:#1c1917;font-family:{_FONT}'>"
            f"🔍 {len(pending_diffs)} source change{'s' if len(pending_diffs) != 1 else ''} to review</h3>"
            f"<ul style='margin:0 0 20px;padding-left:20px;font-size:14px;line-height:1.6;"
            f"color:#1c1917;font-family:{_FONT}'>{rows}</ul>"
        )

    if failing_sources:
        rows = "".join(
            f"<li style='margin-bottom:8px'>{_URGENCY_DOT.get(s['urgency'], '⚪')} "
            f"<a href='{_dest_link(s['destination_id'])}' style='color:#b45309'>{html.escape(s['destination_name'])}</a>"
            f" - failing for {s['days_failing']} day{'s' if s['days_failing'] != 1 else ''}"
            f"</li>"
            for s in failing_sources
        )
        sections.append(
            f"<h3 style='margin:0 0 6px;font-size:15px;color:#1c1917;font-family:{_FONT}'>"
            f"⚠️ {len(failing_sources)} source{'s' if len(failing_sources) != 1 else ''} our monitor can't reach</h3>"
            f"<ul style='margin:0 0 20px;padding-left:20px;font-size:14px;line-height:1.6;"
            f"color:#1c1917;font-family:{_FONT}'>{rows}</ul>"
        )

    if follow_ups:
        rows = "".join(
            f"<li style='margin-bottom:8px'>{'🔴 overdue' if f['overdue'] else '🟡 due ' + f['due_str']} - "
            f"<a href='{_dest_link(f['destination_id'])}' style='color:#b45309'>{html.escape(f['destination_name'])}</a>"
            f" - {html.escape(f['title'])}"
            + (f"<br/><span style='color:#78716c;font-size:13px'>{html.escape(f['notes'])}</span>" if f.get("notes") else "")
            + "</li>"
            for f in follow_ups
        )
        sections.append(
            f"<h3 style='margin:0 0 6px;font-size:15px;color:#1c1917;font-family:{_FONT}'>"
            f"📅 {len(follow_ups)} follow-up{'s' if len(follow_ups) != 1 else ''} due this week</h3>"
            f"<ul style='margin:0 0 20px;padding-left:20px;font-size:14px;line-height:1.6;"
            f"color:#1c1917;font-family:{_FONT}'>{rows}</ul>"
        )

    if open_inquiries_count:
        sections.append(
            f"<p style='{_TEXT_STYLE}'>✉️ {open_inquiries_count} open contact message"
            f"{'s' if open_inquiries_count != 1 else ''} waiting for a reply.</p>"
        )

    body = "".join(sections)
    total = len(pending_diffs) + len(failing_sources) + len(follow_ups) + open_inquiries_count
    resend.Emails.send(
        {
            "from": _FROM,
            "to": admin_emails,
            "subject": f"SlotScout weekly digest: {total} item{'s' if total != 1 else ''} need attention",
            "html": _wrap_email(body),
        }
    )
