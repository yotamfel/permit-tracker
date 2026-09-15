import logging
import secrets

from sqlalchemy.orm import Session

from app.models.user import User
from app.services.paddle_service import PaddleError, create_flat_discount

logger = logging.getLogger(__name__)

# Avoids visually ambiguous characters (0/O, 1/I) since the code is meant to
# be read off a screen and typed into Paddle's checkout discount field.
_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
_CODE_LENGTH = 8

REFERRAL_DISCOUNT_AMOUNT_CENTS = "300"  # $3.00 off the $6.99 unlock price -> $3.99
REFERRAL_DISCOUNT_CURRENCY = "USD"
REFERRAL_DISCOUNT_USAGE_LIMIT = 3


def _generate_code() -> str:
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(_CODE_LENGTH))


def ensure_referral_code(db: Session, user: User) -> None:
    """Gives a paying user a shareable "bring a travel companion" discount
    code the first time they complete a purchase - not a formal
    referral-credit program, just a flat-amount Paddle discount code capped
    at a few redemptions. Safe to call on every completed purchase; no-ops
    once the user already has one."""
    if user.referral_code:
        return

    for _ in range(5):
        code = _generate_code()
        if db.query(User).filter(User.referral_code == code).first() is None:
            break
    else:
        logger.error("Could not generate a unique referral code for user %s", user.id)
        return

    try:
        discount_id = create_flat_discount(
            code=code,
            amount_cents=REFERRAL_DISCOUNT_AMOUNT_CENTS,
            currency_code=REFERRAL_DISCOUNT_CURRENCY,
            usage_limit=REFERRAL_DISCOUNT_USAGE_LIMIT,
            description=f"Referral discount - {user.email}",
        )
    except PaddleError:
        logger.exception("Failed to create Paddle referral discount for user %s", user.id)
        return

    user.referral_code = code
    user.referral_discount_id = discount_id
    db.add(user)
    db.commit()
