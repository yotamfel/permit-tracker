import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, get_locale
from app.models.destination import Destination
from app.models.user import User
from app.models.watchlist_item import WatchlistItem
from app.schemas.destination import DestinationCardOut
from app.services.ownership import owned_destination_ids
from app.services.i18n import translate_bulk
from app.services.release_date import compute_next_release

router = APIRouter(prefix="/api", tags=["watchlist"])


@router.post("/watchlist/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_to_watchlist(
    destination_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    d = db.get(Destination, destination_id)
    if d is None or not d.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")

    existing = db.query(WatchlistItem).filter_by(user_id=user.id, destination_id=destination_id).first()
    if existing is None:
        db.add(WatchlistItem(user_id=user.id, destination_id=destination_id))
        db.commit()


@router.delete("/watchlist/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    destination_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    db.query(WatchlistItem).filter_by(user_id=user.id, destination_id=destination_id).delete()
    db.commit()


@router.get("/me/watchlist", response_model=list[DestinationCardOut])
def list_my_watchlist(
    user: User = Depends(get_current_user), db: Session = Depends(get_db), locale: str = Depends(get_locale)
) -> list[DestinationCardOut]:
    destination_ids = [
        r[0] for r in db.query(WatchlistItem.destination_id).filter(WatchlistItem.user_id == user.id).all()
    ]
    if not destination_ids:
        return []
    destinations = (
        db.query(Destination)
        .filter(Destination.id.in_(destination_ids), Destination.is_published.is_(True))
        .order_by(Destination.country, Destination.name)
        .all()
    )
    names = translate_bulk(db, "destination.name", [d.id for d in destinations], locale)
    owned_ids = owned_destination_ids(db, user, [d.id for d in destinations])

    return [
        DestinationCardOut(
            id=d.id,
            country=d.country,
            category=d.category,
            name=names.get(d.id, d.name),
            mechanism_type=d.mechanism_type,
            issuing_authority=d.issuing_authority,
            competitiveness_level=d.competitiveness_level,
            price_usd=float(d.price_usd),
            next_known_release=compute_next_release(d.mechanism_type.value, d.mechanism_config),
            is_owned=d.id in owned_ids,
            is_watching=True,
            season_start_month=d.season_start_month,
            season_end_month=d.season_end_month,
            safety_advisory=d.safety_advisory,
            image_url=d.image_url,
            image_credit_name=d.image_credit_name,
            image_credit_url=d.image_credit_url,
            image_license=d.image_license,
        )
        for d in destinations
    ]
