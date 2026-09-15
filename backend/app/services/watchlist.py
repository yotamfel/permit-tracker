import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.watchlist_item import WatchlistItem


def watched_destination_ids(db: Session, user: User | None, all_destination_ids: list[uuid.UUID]) -> set[uuid.UUID]:
    """Batched lookup for list endpoints - one query instead of one per destination."""
    if user is None or not all_destination_ids:
        return set()
    rows = (
        db.query(WatchlistItem.destination_id)
        .filter(WatchlistItem.user_id == user.id, WatchlistItem.destination_id.in_(all_destination_ids))
        .all()
    )
    return {r[0] for r in rows}
