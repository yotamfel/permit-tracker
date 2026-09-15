import hashlib
import hmac
import time

import httpx

from app.core.config import get_settings

settings = get_settings()

# Paddle recommends verifying the signature on the raw body before parsing
# it as JSON - transforming the body at all (even re-serializing it) changes
# its bytes and breaks the HMAC comparison.
WEBHOOK_SIGNATURE_MAX_AGE_SECONDS = 5 * 60


class PaddleError(Exception):
    pass


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {settings.paddle_api_key}"}


def get_or_create_customer_id(email: str) -> str:
    """Paddle transactions must reference an existing customer_id (ctm_...) -
    there's no way to pass an email inline. Looks one up by email first since
    creating a duplicate email 409s."""
    resp = httpx.get(
        f"{settings.paddle_api_base_url}/customers", headers=_auth_headers(), params={"email": email}, timeout=15
    )
    if resp.status_code >= 400:
        raise PaddleError(f"Paddle customer lookup failed ({resp.status_code}): {resp.text}")
    existing = resp.json()["data"]
    if existing:
        return existing[0]["id"]

    resp = httpx.post(
        f"{settings.paddle_api_base_url}/customers", headers=_auth_headers(), json={"email": email}, timeout=15
    )
    if resp.status_code == 409:
        # Race: another request created this customer between the lookup and now.
        resp = httpx.get(
            f"{settings.paddle_api_base_url}/customers", headers=_auth_headers(), params={"email": email}, timeout=15
        )
        if resp.status_code >= 400 or not resp.json()["data"]:
            raise PaddleError(f"Paddle customer race-recovery lookup failed ({resp.status_code}): {resp.text}")
        return resp.json()["data"][0]["id"]
    if resp.status_code >= 400:
        raise PaddleError(f"Paddle customer creation failed ({resp.status_code}): {resp.text}")
    return resp.json()["data"]["id"]


def create_transaction(destination_id: str, destination_name: str, user_id: str, customer_id: str) -> str:
    """Creates a Paddle transaction for the flat destination-unlock price and
    returns the hosted checkout URL to redirect the browser to."""
    resp = httpx.post(
        f"{settings.paddle_api_base_url}/transactions",
        headers=_auth_headers(),
        json={
            "items": [{"price_id": settings.paddle_price_id, "quantity": 1}],
            "customer_id": customer_id,
            "custom_data": {"destination_id": destination_id, "user_id": user_id},
            "checkout": {
                "url": f"{settings.frontend_url}/destinations/{destination_id}?purchase=success",
            },
        },
        timeout=15,
    )
    if resp.status_code >= 400:
        raise PaddleError(f"Paddle transaction creation failed ({resp.status_code}): {resp.text}")

    data = resp.json()["data"]
    checkout_url = data.get("checkout", {}).get("url")
    if not checkout_url:
        raise PaddleError(f"Paddle transaction {data.get('id')} has no checkout URL: {data}")
    return checkout_url


def create_flat_discount(
    *, code: str, amount_cents: str, currency_code: str, usage_limit: int, description: str
) -> str:
    """Creates a Paddle discount code with a flat amount off, capped at
    usage_limit redemptions, and returns its Paddle discount id (dsc_...)."""
    resp = httpx.post(
        f"{settings.paddle_api_base_url}/discounts",
        headers=_auth_headers(),
        json={
            "type": "flat",
            "amount": amount_cents,
            "currency_code": currency_code,
            "code": code,
            "usage_limit": usage_limit,
            "enabled_for_checkout": True,
            "description": description,
        },
        timeout=15,
    )
    if resp.status_code >= 400:
        raise PaddleError(f"Paddle discount creation failed ({resp.status_code}): {resp.text}")
    return resp.json()["data"]["id"]


def verify_webhook_signature(payload: bytes, signature_header: str) -> bool:
    """Verifies the `Paddle-Signature: ts=<unix_ts>;h1=<hex_hmac>` header per
    https://developer.paddle.com/webhooks/about/signature-verification/."""
    parts = dict(part.split("=", 1) for part in signature_header.split(";") if "=" in part)
    ts, h1 = parts.get("ts"), parts.get("h1")
    if not ts or not h1:
        return False

    try:
        if abs(time.time() - int(ts)) > WEBHOOK_SIGNATURE_MAX_AGE_SECONDS:
            return False
    except ValueError:
        return False

    signed_payload = f"{ts}:".encode() + payload
    expected = hmac.new(settings.paddle_webhook_secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, h1)
