import stripe

from app.core.config import get_settings

settings = get_settings()
stripe.api_key = settings.stripe_secret_key


def create_checkout_session(
    destination_id: str, destination_name: str, price_usd: float, user_id: str, user_email: str
) -> str:
    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(round(price_usd * 100)),
                    "product_data": {"name": f"Permit Tracker unlock: {destination_name}"},
                },
                "quantity": 1,
            }
        ],
        customer_email=user_email,
        metadata={"destination_id": destination_id, "user_id": user_id},
        success_url=f"{settings.frontend_url}/destinations/{destination_id}?purchase=success",
        cancel_url=f"{settings.frontend_url}/destinations/{destination_id}?purchase=cancelled",
    )
    return session.url


def construct_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
    return stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
