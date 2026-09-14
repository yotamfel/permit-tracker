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
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.db import SessionLocal
import app.models  # noqa: F401 - registers every model so cross-model relationships (e.g. Destination.sources) resolve
from app.models.admin_user import AdminUser
from app.models.destination import Destination
from app.models.monitoring import MonitoringDiff, MonitoringSnapshot
from app.services.email_service import send_source_fetch_failure_email

logger = logging.getLogger(__name__)

MAX_EXCERPT_CHARS = 20_000
REQUEST_TIMEOUT_SECONDS = 20

# These government hosts (Corcovado/Manuel Antonio's SINAC pages, Machu
# Picchu's official site, Kenya Wildlife Service) don't send their
# intermediate TLS certificate - something browsers tolerate (they already
# cache common intermediates) but httpx's strict verification rejects
# outright. Confirmed 2026-09-14 this reproduces from multiple networks, so
# it's a real server misconfiguration, not transient. Explicit, narrow
# exception per the site owner's decision: retry without verification ONLY
# for these already-known hosts, for this read-only public-content
# monitoring fetch only (never for anything that submits data or
# credentials). Do not add a host here without confirming the
# failure is genuinely a cert-chain issue (see the ConnectError branch below).
INSECURE_FALLBACK_HOSTS = {"www.sinac.go.cr", "www.machupicchu.gob.pe", "kws.go.ke"}


def extract_visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    # Postgres text columns reject literal NUL bytes outright - a source_url that
    # actually serves a PDF/binary file (e.g. Rock Islands' Palau fact-sheet PDF)
    # parses as garbage through an HTML parser and can smuggle one in, which
    # crashes the whole job's DB commit rather than just failing that one fetch.
    text = text.replace("\x00", "")
    return " ".join(text.split())


def _is_cert_verification_error(exc: Exception) -> bool:
    cause = exc.__cause__
    return "CERTIFICATE_VERIFY_FAILED" in str(cause or exc)


def fetch_text(url: str) -> tuple[str | None, str | None]:
    """Returns (text, error) - exactly one of which is None."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; PermitTrackerBot/1.0)"}
    try:
        try:
            resp = httpx.get(url, timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=True, headers=headers)
        except httpx.ConnectError as exc:
            host = urlparse(url).hostname
            if host in INSECURE_FALLBACK_HOSTS and _is_cert_verification_error(exc):
                logger.warning("TLS cert verification failed for known host %s - retrying without verification", host)
                resp = httpx.get(
                    url, timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=True, headers=headers, verify=False
                )
            else:
                raise
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "html" not in content_type and "text" not in content_type:
            # A PDF/image/other binary source_url - not something an HTML parser
            # can meaningfully diff over time. Treat like any other fetch failure
            # instead of feeding binary bytes through BeautifulSoup.
            return None, f"Unsupported content-type for monitoring: {content_type or 'unknown'}"
        return extract_visible_text(resp.text), None
    except httpx.HTTPError as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None, str(exc)


def run() -> None:
    db = SessionLocal()
    try:
        destinations = db.query(Destination).filter(Destination.is_published.is_(True)).all()

        for d in destinations:
            try:
                _check_one(db, d)
            except Exception:
                # One destination's fetch/parse/DB write must never take down the
                # rest of the run - this crashed the whole job on 2026-09-14 when
                # Rock Islands' PDF source_url produced a NUL byte Postgres
                # rejected, silently skipping every destination after it that day.
                logger.exception("Unhandled error monitoring %s (%s) - skipping", d.name, d.id)
                db.rollback()
    finally:
        db.close()


def _check_one(db, d: Destination) -> None:
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
            admin_emails = [a.email for a in db.query(AdminUser).all()]
            try:
                send_source_fetch_failure_email(admin_emails, d.name, d.source_url, error)
            except Exception:
                logger.exception("Failed to send source-fetch-failure email for %s", d.id)
        else:
            d.source_fetch_error = error
            db.add(d)
            db.commit()
        return

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
        return  # no change

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


if __name__ == "__main__":
    from app.core.monitoring import init_sentry

    init_sentry()
    logging.basicConfig(level=logging.INFO)
    run()
