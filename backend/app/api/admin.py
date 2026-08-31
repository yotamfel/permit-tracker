import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_db
from app.models.checklist_item import ChecklistItem
from app.models.destination import Destination
from app.models.enums import ReviewStatus
from app.models.general_requirement import DestinationRequirement, GeneralRequirement
from app.models.monitoring import MonitoringDiff, MonitoringSnapshot
from app.models.translation import Translation
from app.models.user import User
from app.schemas.admin import (
    AdminChecklistItemIn,
    AdminChecklistItemOut,
    AdminDestinationIn,
    AdminDestinationOut,
    AdminDestinationRequirementIn,
    AdminDestinationRequirementOut,
    AdminGeneralRequirementIn,
    AdminGeneralRequirementOut,
    AdminMonitoringDiffOut,
    AdminTranslationIn,
    AdminTranslationOut,
)
from app.schemas.mechanism_config import validate_mechanism_config

router = APIRouter(prefix="/admin/api", tags=["admin"], dependencies=[Depends(get_current_admin)])


def _validate_config(body: AdminDestinationIn) -> None:
    try:
        validate_mechanism_config(body.mechanism_type.value, body.mechanism_config)
    except Exception as exc:  # pydantic ValidationError or ValueError
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Invalid mechanism_config: {exc}") from exc


# --- Destinations ---------------------------------------------------------


@router.get("/destinations", response_model=list[AdminDestinationOut])
def list_destinations(db: Session = Depends(get_db)) -> list[AdminDestinationOut]:
    return [AdminDestinationOut.model_validate(d) for d in db.query(Destination).order_by(Destination.name).all()]


@router.post("/destinations", response_model=AdminDestinationOut)
def create_destination(body: AdminDestinationIn, db: Session = Depends(get_db)) -> AdminDestinationOut:
    _validate_config(body)
    d = Destination(**body.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return AdminDestinationOut.model_validate(d)


@router.get("/destinations/{destination_id}", response_model=AdminDestinationOut)
def get_destination(destination_id: uuid.UUID, db: Session = Depends(get_db)) -> AdminDestinationOut:
    d = db.get(Destination, destination_id)
    if d is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")
    return AdminDestinationOut.model_validate(d)


@router.put("/destinations/{destination_id}", response_model=AdminDestinationOut)
def update_destination(
    destination_id: uuid.UUID, body: AdminDestinationIn, db: Session = Depends(get_db)
) -> AdminDestinationOut:
    d = db.get(Destination, destination_id)
    if d is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")
    _validate_config(body)
    for field, value in body.model_dump().items():
        setattr(d, field, value)
    d.last_verified_at = datetime.now(timezone.utc)
    db.add(d)
    db.commit()
    db.refresh(d)
    return AdminDestinationOut.model_validate(d)


@router.delete("/destinations/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_destination(destination_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    d = db.get(Destination, destination_id)
    if d is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")
    db.delete(d)
    db.commit()


# --- Checklist items -------------------------------------------------------


@router.get("/checklist-items", response_model=list[AdminChecklistItemOut])
def list_checklist_items(destination_id: uuid.UUID | None = None, db: Session = Depends(get_db)) -> list[AdminChecklistItemOut]:
    query = db.query(ChecklistItem)
    if destination_id:
        query = query.filter(ChecklistItem.destination_id == destination_id)
    return [AdminChecklistItemOut.model_validate(i) for i in query.order_by(ChecklistItem.order_index).all()]


@router.post("/checklist-items", response_model=AdminChecklistItemOut)
def create_checklist_item(body: AdminChecklistItemIn, db: Session = Depends(get_db)) -> AdminChecklistItemOut:
    item = ChecklistItem(**body.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return AdminChecklistItemOut.model_validate(item)


@router.put("/checklist-items/{item_id}", response_model=AdminChecklistItemOut)
def update_checklist_item(item_id: uuid.UUID, body: AdminChecklistItemIn, db: Session = Depends(get_db)) -> AdminChecklistItemOut:
    item = db.get(ChecklistItem, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Checklist item not found")
    for field, value in body.model_dump().items():
        setattr(item, field, value)
    db.add(item)
    db.commit()
    db.refresh(item)
    return AdminChecklistItemOut.model_validate(item)


@router.delete("/checklist-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checklist_item(item_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    item = db.get(ChecklistItem, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Checklist item not found")
    db.delete(item)
    db.commit()


# --- General requirements (spec addendum §2) --------------------------------


@router.get("/general-requirements", response_model=list[AdminGeneralRequirementOut])
def list_general_requirements(db: Session = Depends(get_db)) -> list[AdminGeneralRequirementOut]:
    """Also serves as the search/autocomplete source for §2.4's admin attach-flow."""
    return [
        AdminGeneralRequirementOut.model_validate(g)
        for g in db.query(GeneralRequirement).order_by(GeneralRequirement.title_key).all()
    ]


@router.post("/general-requirements", response_model=AdminGeneralRequirementOut)
def create_general_requirement(body: AdminGeneralRequirementIn, db: Session = Depends(get_db)) -> AdminGeneralRequirementOut:
    g = GeneralRequirement(**body.model_dump())
    db.add(g)
    db.commit()
    db.refresh(g)
    return AdminGeneralRequirementOut.model_validate(g)


@router.put("/general-requirements/{requirement_id}", response_model=AdminGeneralRequirementOut)
def update_general_requirement(
    requirement_id: uuid.UUID, body: AdminGeneralRequirementIn, db: Session = Depends(get_db)
) -> AdminGeneralRequirementOut:
    g = db.get(GeneralRequirement, requirement_id)
    if g is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "General requirement not found")
    for field, value in body.model_dump().items():
        setattr(g, field, value)
    db.add(g)
    db.commit()
    db.refresh(g)
    return AdminGeneralRequirementOut.model_validate(g)


@router.delete("/general-requirements/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_general_requirement(requirement_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    g = db.get(GeneralRequirement, requirement_id)
    if g is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "General requirement not found")
    db.delete(g)
    db.commit()


# --- Destination <-> general requirement attachments (spec addendum §2.2) ---


@router.get("/destination-requirements", response_model=list[AdminDestinationRequirementOut])
def list_destination_requirements(
    destination_id: uuid.UUID | None = None, db: Session = Depends(get_db)
) -> list[AdminDestinationRequirementOut]:
    query = db.query(DestinationRequirement)
    if destination_id:
        query = query.filter(DestinationRequirement.destination_id == destination_id)
    return [
        AdminDestinationRequirementOut.model_validate(dr)
        for dr in query.order_by(DestinationRequirement.order_index).all()
    ]


@router.post("/destination-requirements", response_model=AdminDestinationRequirementOut)
def attach_destination_requirement(
    body: AdminDestinationRequirementIn, db: Session = Depends(get_db)
) -> AdminDestinationRequirementOut:
    dr = DestinationRequirement(**body.model_dump())
    db.add(dr)
    db.commit()
    db.refresh(dr)
    return AdminDestinationRequirementOut.model_validate(dr)


@router.delete("/destination-requirements/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def detach_destination_requirement(attachment_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    dr = db.get(DestinationRequirement, attachment_id)
    if dr is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Attachment not found")
    db.delete(dr)
    db.commit()


# --- Translations -----------------------------------------------------------


@router.get("/translations", response_model=list[AdminTranslationOut])
def list_translations(
    entity_type: str | None = None, entity_id: uuid.UUID | None = None, db: Session = Depends(get_db)
) -> list[AdminTranslationOut]:
    query = db.query(Translation)
    if entity_type:
        query = query.filter(Translation.entity_type == entity_type)
    if entity_id:
        query = query.filter(Translation.entity_id == entity_id)
    return [AdminTranslationOut.model_validate(t) for t in query.all()]


@router.post("/translations", response_model=AdminTranslationOut)
def upsert_translation(body: AdminTranslationIn, db: Session = Depends(get_db)) -> AdminTranslationOut:
    existing = (
        db.query(Translation)
        .filter(
            Translation.entity_type == body.entity_type,
            Translation.entity_id == body.entity_id,
            Translation.locale == body.locale,
        )
        .first()
    )
    if existing is not None:
        existing.value = body.value
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return AdminTranslationOut.model_validate(existing)

    t = Translation(**body.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return AdminTranslationOut.model_validate(t)


@router.delete("/translations/{translation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_translation(translation_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    t = db.get(Translation, translation_id)
    if t is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Translation not found")
    db.delete(t)
    db.commit()


# --- Monitoring diffs review queue ------------------------------------------


@router.get("/monitoring/diffs", response_model=list[AdminMonitoringDiffOut])
def list_monitoring_diffs(status_filter: ReviewStatus | None = None, db: Session = Depends(get_db)) -> list[AdminMonitoringDiffOut]:
    query = db.query(MonitoringDiff)
    if status_filter:
        query = query.filter(MonitoringDiff.review_status == status_filter)
    diffs = query.order_by(MonitoringDiff.created_at.desc()).all()
    return [_resolve_diff(diff, db) for diff in diffs]


def _resolve_diff(diff: MonitoringDiff, db: Session) -> AdminMonitoringDiffOut:
    d = db.get(Destination, diff.destination_id)
    new_snap = db.get(MonitoringSnapshot, diff.new_snapshot_id)
    prev_snap = db.get(MonitoringSnapshot, diff.previous_snapshot_id) if diff.previous_snapshot_id else None
    return AdminMonitoringDiffOut(
        id=diff.id,
        destination_id=diff.destination_id,
        destination_name=d.name if d else "",
        previous_text=prev_snap.raw_text_excerpt if prev_snap else None,
        new_text=new_snap.raw_text_excerpt if new_snap else "",
        diff_summary=diff.diff_summary,
        review_status=diff.review_status,
        reviewed_at=diff.reviewed_at,
        created_at=diff.created_at,
    )


@router.post("/monitoring/diffs/{diff_id}/approve", response_model=AdminMonitoringDiffOut)
def approve_diff(diff_id: uuid.UUID, db: Session = Depends(get_db)) -> AdminMonitoringDiffOut:
    diff = db.get(MonitoringDiff, diff_id)
    if diff is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Diff not found")
    diff.review_status = ReviewStatus.approved
    diff.reviewed_at = datetime.now(timezone.utc)
    db.add(diff)
    db.commit()
    db.refresh(diff)
    return _resolve_diff(diff, db)


@router.post("/monitoring/diffs/{diff_id}/dismiss", response_model=AdminMonitoringDiffOut)
def dismiss_diff(diff_id: uuid.UUID, db: Session = Depends(get_db)) -> AdminMonitoringDiffOut:
    diff = db.get(MonitoringDiff, diff_id)
    if diff is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Diff not found")
    diff.review_status = ReviewStatus.dismissed
    diff.reviewed_at = datetime.now(timezone.utc)
    db.add(diff)
    db.commit()
    db.refresh(diff)
    return _resolve_diff(diff, db)
