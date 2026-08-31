import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_db
from app.models.checklist_item import ChecklistItem
from app.models.contact_message import ContactMessage
from app.models.destination import Destination
from app.models.enums import ContactMessageStatus, PurchaseStatus, ReviewStatus
from app.models.general_requirement import DestinationRequirement, GeneralRequirement
from app.models.monitoring import MonitoringDiff, MonitoringSnapshot
from app.models.purchase import Purchase
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
    DestinationPurchaseStatsOut,
    PurchaseStatsOut,
    ReviewQueueItemOut,
)
from app.schemas.contact import AdminContactMessageOut, AdminContactMessageReplyIn, AdminContactMessageStatusUpdate
from app.schemas.mechanism_config import validate_mechanism_config
from app.services.email_service import send_contact_reply
from app.services.i18n import translate

router = APIRouter(prefix="/admin/api", tags=["admin"], dependencies=[Depends(get_current_admin)])


def _validate_config(body: AdminDestinationIn) -> None:
    try:
        validate_mechanism_config(body.mechanism_type.value, body.mechanism_config)
    except Exception as exc:  # pydantic ValidationError or ValueError
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Invalid mechanism_config: {exc}") from exc


def _upsert_en_translation(db: Session, entity_type: str, entity_id: uuid.UUID, value: str | None) -> None:
    if value is None:
        return
    existing = (
        db.query(Translation)
        .filter(Translation.entity_type == entity_type, Translation.entity_id == entity_id, Translation.locale == "en")
        .first()
    )
    if existing is not None:
        existing.value = value
        db.add(existing)
    else:
        db.add(Translation(entity_type=entity_type, entity_id=entity_id, locale="en", value=value))


def _destination_out(db: Session, d: Destination) -> AdminDestinationOut:
    out = AdminDestinationOut.model_validate(d)
    out.description = translate(db, "destination.description", d.id, "en")
    out.mechanism_explanation = translate(db, "destination.mechanism_explanation", d.id, "en")
    return out


# --- Destinations ---------------------------------------------------------


_DESTINATION_MODEL_FIELDS = {
    "country", "category", "name", "mechanism_type", "mechanism_config", "issuing_authority",
    "competitiveness_level", "source_url", "application_url", "price_usd", "is_published",
}


@router.get("/destinations", response_model=list[AdminDestinationOut])
def list_destinations(db: Session = Depends(get_db)) -> list[AdminDestinationOut]:
    return [_destination_out(db, d) for d in db.query(Destination).order_by(Destination.name).all()]


@router.post("/destinations", response_model=AdminDestinationOut)
def create_destination(body: AdminDestinationIn, db: Session = Depends(get_db)) -> AdminDestinationOut:
    _validate_config(body)
    payload = {k: v for k, v in body.model_dump().items() if k in _DESTINATION_MODEL_FIELDS}
    d = Destination(**payload)
    db.add(d)
    db.flush()
    _upsert_en_translation(db, "destination.description", d.id, body.description)
    _upsert_en_translation(db, "destination.mechanism_explanation", d.id, body.mechanism_explanation)
    db.commit()
    db.refresh(d)
    return _destination_out(db, d)


@router.get("/destinations/{destination_id}", response_model=AdminDestinationOut)
def get_destination(destination_id: uuid.UUID, db: Session = Depends(get_db)) -> AdminDestinationOut:
    d = db.get(Destination, destination_id)
    if d is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")
    return _destination_out(db, d)


@router.put("/destinations/{destination_id}", response_model=AdminDestinationOut)
def update_destination(
    destination_id: uuid.UUID, body: AdminDestinationIn, db: Session = Depends(get_db)
) -> AdminDestinationOut:
    d = db.get(Destination, destination_id)
    if d is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")
    _validate_config(body)
    for field, value in body.model_dump().items():
        if field in _DESTINATION_MODEL_FIELDS:
            setattr(d, field, value)
    d.last_verified_at = datetime.now(timezone.utc)
    db.add(d)
    _upsert_en_translation(db, "destination.description", d.id, body.description)
    _upsert_en_translation(db, "destination.mechanism_explanation", d.id, body.mechanism_explanation)
    db.commit()
    db.refresh(d)
    return _destination_out(db, d)


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


# --- Purchase stats -----------------------------------------------------------


@router.get("/stats/purchases", response_model=PurchaseStatsOut)
def purchase_stats(db: Session = Depends(get_db)) -> PurchaseStatsOut:
    completed = db.query(Purchase).filter(Purchase.status == PurchaseStatus.completed).all()

    by_destination: dict[uuid.UUID, dict] = {}
    for p in completed:
        entry = by_destination.setdefault(p.destination_id, {"count": 0, "revenue": 0.0})
        entry["count"] += 1
        entry["revenue"] += float(p.amount_usd)

    destinations = {d.id: d for d in db.query(Destination).filter(Destination.id.in_(by_destination.keys())).all()}

    rows = [
        DestinationPurchaseStatsOut(
            destination_id=dest_id,
            destination_name=destinations[dest_id].name if dest_id in destinations else "(deleted destination)",
            purchase_count=data["count"],
            revenue_usd=round(data["revenue"], 2),
        )
        for dest_id, data in by_destination.items()
    ]
    rows.sort(key=lambda r: r.purchase_count, reverse=True)

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    total_accounts = db.query(User).count()
    recent_accounts = db.query(User).filter(User.created_at >= seven_days_ago).count()

    return PurchaseStatsOut(
        total_purchases=len(completed),
        total_revenue_usd=round(sum(float(p.amount_usd) for p in completed), 2),
        total_accounts=total_accounts,
        accounts_created_last_7_days=recent_accounts,
        by_destination=rows,
    )


# --- Review queue (spec-addendum-style human-verification gate) -------------
# Every destination starts unpublished (is_published=False) whether it came
# from the stub_import script, the monitoring job's research, or manual admin
# entry. This surfaces all of them in one place with whatever source context
# exists, so an admin can verify/edit before it ever appears on the public
# site - nothing here is ever auto-published.


@router.get("/review-queue", response_model=list[ReviewQueueItemOut])
def list_review_queue(db: Session = Depends(get_db)) -> list[ReviewQueueItemOut]:
    pending = (
        db.query(Destination)
        .filter(Destination.is_published.is_(False))
        .order_by(Destination.country, Destination.name)
        .all()
    )

    notes = {
        t.entity_id: t.value
        for t in db.query(Translation)
        .filter(
            Translation.entity_type == "destination.description",
            Translation.entity_id.in_([d.id for d in pending]),
        )
        .all()
    }

    explanations = {
        t.entity_id: t.value
        for t in db.query(Translation)
        .filter(
            Translation.entity_type == "destination.mechanism_explanation",
            Translation.entity_id.in_([d.id for d in pending]),
        )
        .all()
    }

    items = []
    for d in pending:
        description = notes.get(d.id)
        source_note = d.source_url or description
        items.append(
            ReviewQueueItemOut(
                id=d.id,
                country=d.country,
                category=d.category,
                name=d.name,
                mechanism_type=d.mechanism_type,
                mechanism_config=d.mechanism_config,
                issuing_authority=d.issuing_authority,
                competitiveness_level=d.competitiveness_level,
                source_url=d.source_url,
                application_url=d.application_url,
                price_usd=float(d.price_usd),
                description=description,
                mechanism_explanation=explanations.get(d.id),
                source_note=source_note,
            )
        )
    return items


@router.post("/review-queue/{destination_id}/approve", response_model=AdminDestinationOut)
def approve_review_item(
    destination_id: uuid.UUID, body: AdminDestinationIn, db: Session = Depends(get_db)
) -> AdminDestinationOut:
    """Save any edits made during review, then publish - one action, per the
    "I go through, approve or change if needed, and then it goes live" flow."""
    d = db.get(Destination, destination_id)
    if d is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")
    _validate_config(body)
    for field, value in body.model_dump().items():
        if field in _DESTINATION_MODEL_FIELDS:
            setattr(d, field, value)
    d.is_published = True
    d.last_verified_at = datetime.now(timezone.utc)
    db.add(d)
    _upsert_en_translation(db, "destination.description", d.id, body.description)
    _upsert_en_translation(db, "destination.mechanism_explanation", d.id, body.mechanism_explanation)
    db.commit()
    db.refresh(d)
    return _destination_out(db, d)


# --- Contact messages ---------------------------------------------------------


@router.get("/contact-messages", response_model=list[AdminContactMessageOut])
def list_contact_messages(
    status_filter: ContactMessageStatus | None = None, db: Session = Depends(get_db)
) -> list[AdminContactMessageOut]:
    query = db.query(ContactMessage)
    if status_filter:
        query = query.filter(ContactMessage.status == status_filter)
    messages = query.order_by(ContactMessage.created_at.desc()).all()
    return [AdminContactMessageOut.model_validate(m) for m in messages]


@router.patch("/contact-messages/{message_id}", response_model=AdminContactMessageOut)
def update_contact_message_status(
    message_id: uuid.UUID, body: AdminContactMessageStatusUpdate, db: Session = Depends(get_db)
) -> AdminContactMessageOut:
    msg = db.get(ContactMessage, message_id)
    if msg is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message not found")
    msg.status = body.status
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return AdminContactMessageOut.model_validate(msg)


@router.post("/contact-messages/{message_id}/reply", response_model=AdminContactMessageOut)
def reply_to_contact_message(
    message_id: uuid.UUID, body: AdminContactMessageReplyIn, db: Session = Depends(get_db)
) -> AdminContactMessageOut:
    msg = db.get(ContactMessage, message_id)
    if msg is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message not found")

    send_contact_reply(msg.email, msg.name, msg.message, body.message)

    msg.admin_reply = body.message
    msg.replied_at = datetime.now(timezone.utc)
    msg.status = ContactMessageStatus.resolved
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return AdminContactMessageOut.model_validate(msg)
