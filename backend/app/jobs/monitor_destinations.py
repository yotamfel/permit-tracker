"""
Weekly monitoring job. For each published destination, fetch source_url, extract
visible text, hash it, and compare against the latest snapshot.

If the text changed: store a new snapshot + a monitoring_diffs row (review_status=pending).
This job NEVER writes to destinations.mechanism_config or checklist content - it only
surfaces the diff for a human to review in the admin panel (see app/api/admin.py).

Run via: python -m app.jobs.monitor_destinations
"""
import difflib
import hashlib
import logging
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from app.db import SessionLocal
from app.models.admin_user import AdminUser
from app.models.destination import Destination
from app.models.monitoring import MonitoringDiff, MonitoringSnapshot
from app.services.email_service import send_source_fetch_failure_email

logger = logging.getLogger(__name__)

MAX_EXCERPT_CHARS = 20_000
REQUEST_TIMEOUT_SECONDS = 20


def extract_visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())


def fetch_text(url: str) -> tuple[str | None, str | None]:
    """Returns (text, error) - exactly one of which is None."""
    try:
        resp = httpx.get(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; PermitTrackerBot/1.0)"},
        )
        resp.raise_for_status()
        return extract_visible_text(resp.text), None
    except httpx.HTTPError as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None, str(exc)


def run() -> None:
    db = SessionLocal()
    try:
        destinations = db.query(Destination).filter(Destination.is_published.is_(True)).all()
        admin_emails = None  # lazily loaded only if a failure notification is actually needed

        for d in destinations:
            text, error = fetch_text(d.source_url)
            if text is None:
                # Only notify on the transition into a failing state, not on every
                # weekly re-check, so a persistently-broken source doesn't spam.
                if not d.source_fetch_failing:
                    d.source_fetch_failing = True
                    d.source_fetch_failing_since = datetime.now(timezone.utc)
                    d.source_fetch_error = error
                    db.add(d)
                    db.commit()
                    if admin_emails is None:
                        admin_emails = [a.email for a in db.query(AdminUser).all()]
                    try:
                        send_source_fetch_failure_email(admin_emails, d.name, d.source_url, error)
                    except Exception:
                        logger.exception("Failed to send source-fetch-failure email for %s", d.id)
                else:
                    d.source_fetch_error = error
                    db.add(d)
                    db.commit()
                continue

            if d.source_fetch_failing:
                d.source_fetch_failing = False
                d.source_fetch_failing_since = None
                d.source_fetch_error = None
                db.add(d)
                db.commit()

            excerpt = text[:MAX_EXCERPT_CHARS]
            content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

            latest = (
                db.query(MonitoringSnapshot)
                .filter(MonitoringSnapshot.destination_id == d.id)
                .order_by(MonitoringSnapshot.captured_at.desc())
                .first()
            )

            if latest is not None and latest.content_hash == content_hash:
                continue  # no change

            new_snapshot = MonitoringSnapshot(
                destination_id=d.id,
                content_hash=content_hash,
                raw_text_excerpt=excerpt,
                captured_at=datetime.now(timezone.utc),
            )
            db.add(new_snapshot)
            db.flush()

            if latest is not None:
                diff_lines = list(
                    difflib.unified_diff(
                        latest.raw_text_excerpt.split(". "),
                        excerpt.split(". "),
                        lineterm="",
                        n=1,
                    )
                )
                diff_summary = "\n".join(diff_lines[:200]) or "Content hash changed but no line-level diff computed."

                db.add(
                    MonitoringDiff(
                        destination_id=d.id,
                        previous_snapshot_id=latest.id,
                        new_snapshot_id=new_snapshot.id,
                        diff_summary=diff_summary,
                    )
                )
            # else: first-ever snapshot for this destination - nothing to diff against yet.

            db.commit()
            logger.info("Captured new snapshot for %s (%s)", d.name, d.id)
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
