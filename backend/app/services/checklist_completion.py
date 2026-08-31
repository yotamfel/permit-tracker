import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.checklist_completion import ChecklistCompletion


def completed_prep_item_ids(db: Session, user_id: uuid.UUID | None, destination_id: uuid.UUID) -> set[uuid.UUID]:
    if user_id is None:
        return set()
    rows = (
        db.query(ChecklistCompletion.prep_item_id)
        .filter(ChecklistCompletion.user_id == user_id, ChecklistCompletion.destination_id == destination_id)
        .all()
    )
    return {r[0] for r in rows}


def toggle_completion(db: Session, user_id: uuid.UUID, destination_id: uuid.UUID, prep_item_id: uuid.UUID) -> bool:
    """Returns the new completed state."""
    existing = (
        db.query(ChecklistCompletion)
        .filter(ChecklistCompletion.user_id == user_id, ChecklistCompletion.prep_item_id == prep_item_id)
        .first()
    )
    if existing is not None:
        db.delete(existing)
        db.commit()
        return False

    db.add(
        ChecklistCompletion(
            user_id=user_id,
            destination_id=destination_id,
            prep_item_id=prep_item_id,
            completed_at=datetime.now(timezone.utc),
        )
    )
    db.commit()
    return True
