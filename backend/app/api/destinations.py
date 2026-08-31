import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_db, get_locale, get_optional_current_user
from app.models.destination import Destination
from app.models.enums import Category, CompetitivenessLevel, MechanismType
from app.models.general_requirement import DestinationRequirement
from app.models.user import User
from app.schemas.destination import (
    DestinationCardOut,
    DestinationChecklistOut,
    DestinationDetailOut,
    PrepItemOut,
)
from app.services.i18n import translate_bulk, translate_one_entity_multi_type
from app.services.ownership import owned_destination_ids, user_owns_destination
from app.services.release_date import compute_next_release

router = APIRouter(prefix="/api/destinations", tags=["destinations"])


@router.get("", response_model=list[DestinationCardOut])
def list_destinations(
    country: str | None = None,
    category: Category | None = None,
    mechanism_type: MechanismType | None = None,
    competitiveness_level: CompetitivenessLevel | None = None,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale),
    user: User | None = Depends(get_optional_current_user),
) -> list[DestinationCardOut]:
    query = db.query(Destination).filter(Destination.is_published.is_(True))
    if country:
        query = query.filter(Destination.country == country)
    if category:
        query = query.filter(Destination.category == category)
    if mechanism_type:
        query = query.filter(Destination.mechanism_type == mechanism_type)
    if competitiveness_level:
        query = query.filter(Destination.competitiveness_level == competitiveness_level)
    destinations = query.order_by(Destination.country, Destination.name).all()

    names = translate_bulk(db, "destination.name", [d.id for d in destinations], locale)
    owned_ids = owned_destination_ids(db, user.id if user else None)

    out = []
    for d in destinations:
        out.append(
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
            )
        )
    return out


@router.get("/{destination_id}", response_model=DestinationDetailOut)
def get_destination(
    destination_id: uuid.UUID,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale),
    user: User | None = Depends(get_optional_current_user),
) -> DestinationDetailOut:
    d = db.get(Destination, destination_id)
    if d is None or not d.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")

    is_owned = user_owns_destination(db, user.id if user else None, destination_id)

    texts = translate_one_entity_multi_type(
        db,
        ["destination.name", "destination.description", "destination.mechanism_explanation"],
        d.id,
        locale,
    )
    name = texts.get("destination.name", d.name)
    description = texts.get("destination.description")
    explanation = texts.get("destination.mechanism_explanation", "")

    return DestinationDetailOut(
        id=d.id,
        country=d.country,
        category=d.category,
        name=name,
        description=description,
        mechanism_type=d.mechanism_type,
        mechanism_explanation=explanation,
        issuing_authority=d.issuing_authority,
        competitiveness_level=d.competitiveness_level,
        last_verified_at=d.last_verified_at,
        price_usd=float(d.price_usd),
        is_owned=is_owned,
        next_known_release=compute_next_release(d.mechanism_type.value, d.mechanism_config),
        mechanism_config=d.mechanism_config if is_owned else None,
        application_url=d.application_url if is_owned else None,
    )


@router.get("/{destination_id}/checklist", response_model=DestinationChecklistOut)
def get_checklist(
    destination_id: uuid.UUID,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale),
    user: User | None = Depends(get_optional_current_user),
) -> DestinationChecklistOut:
    d = db.get(Destination, destination_id)
    if d is None or not d.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")

    is_owned = user_owns_destination(db, user.id if user else None, destination_id)
    if not is_owned:
        return DestinationChecklistOut(is_owned=False, items=[])

    items: list[PrepItemOut] = []

    # Section 1: general requirements ("Documents & Bureaucracy") - spec addendum §2.3.
    # joinedload avoids a lazy-loaded query per row for dr.general_requirement.
    dest_reqs = (
        db.query(DestinationRequirement)
        .options(joinedload(DestinationRequirement.general_requirement))
        .filter(DestinationRequirement.destination_id == destination_id)
        .order_by(DestinationRequirement.order_index)
        .all()
    )
    note_ids = [dr.id for dr in dest_reqs if dr.destination_specific_note_key]
    notes = translate_bulk(db, "destination_requirement.note", note_ids, locale)
    gr_ids = [dr.general_requirement_id for dr in dest_reqs]
    gr_descriptions = translate_bulk(db, "general_requirement.description", gr_ids, locale)

    for dr in dest_reqs:
        gr = dr.general_requirement
        text = notes.get(dr.id) or gr_descriptions.get(gr.id) or gr.description_key
        items.append(
            PrepItemOut(
                id=dr.id,
                section="general",
                type=gr.requirement_type.value,
                order_index=dr.order_index,
                is_required=True,
                text=text,
            )
        )

    # Section 2: destination-specific checklist items ("Specific to this permit").
    checklist_texts = translate_bulk(db, "checklist_item.text", [item.id for item in d.checklist_items], locale)
    for item in d.checklist_items:
        text = checklist_texts.get(item.id) or item.text_key
        items.append(
            PrepItemOut(
                id=item.id,
                section="specific",
                type=item.item_type.value,
                order_index=item.order_index,
                is_required=item.is_required,
                text=text,
            )
        )

    return DestinationChecklistOut(is_owned=True, items=items)
