import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, get_locale, get_optional_current_user
from app.models.destination import Destination
from app.models.destination_alternative import DestinationAlternative
from app.models.enums import Category, CompetitivenessLevel, MechanismType
from app.models.general_requirement import DestinationRequirement
from app.models.user import User
from app.models.user_checklist_item import UserChecklistItem
from app.schemas.destination import (
    AlternativeOut,
    CalendarEntryOut,
    DestinationCardOut,
    DestinationChecklistOut,
    DestinationDetailOut,
    PrepItemOut,
    UserChecklistItemIn,
)
from app.services.checklist_completion import completed_prep_item_ids, toggle_completion
from app.services.i18n import translate_bulk, translate_one_entity_multi_type
from app.services.ownership import owned_destination_ids, user_owns_destination
from app.services.release_date import compute_next_release, compute_release_dates_in_month

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
    owned_ids = owned_destination_ids(db, user, [d.id for d in destinations])

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


@router.get("/calendar", response_model=list[CalendarEntryOut])
def calendar(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale),
) -> list[CalendarEntryOut]:
    """"What opens this month" (spec addendum: Post-Release Feedback + Homepage
    Calendar §2) - free to view, no purchase or login needed; only destinations
    with a computable destination-wide release date appear (see
    compute_release_dates_in_month for exactly which mechanism types qualify)."""
    year, month_num = (int(p) for p in month.split("-"))
    destinations = db.query(Destination).filter(Destination.is_published.is_(True)).all()
    names = translate_bulk(db, "destination.name", [d.id for d in destinations], locale)

    out = []
    for d in destinations:
        dates = compute_release_dates_in_month(d.mechanism_type.value, d.mechanism_config, year, month_num)
        if not dates:
            continue
        out.append(
            CalendarEntryOut(
                destination_id=d.id,
                name=names.get(d.id, d.name),
                category=d.category,
                mechanism_type=d.mechanism_type,
                dates=dates,
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

    is_owned = user_owns_destination(db, user, destination_id)

    texts = translate_one_entity_multi_type(
        db,
        ["destination.name", "destination.description", "destination.mechanism_explanation"],
        d.id,
        locale,
    )
    name = texts.get("destination.name", d.name)
    description = texts.get("destination.description")
    explanation = texts.get("destination.mechanism_explanation") if is_owned else None

    # Checklist "shape" teaser (spec addendum §1.2) - counts only, general +
    # specific (not good_to_know, which isn't required for the permit).
    checklist_item_counts: dict[str, int] = {}
    for item in d.checklist_items:
        if item.section.value == "specific":
            checklist_item_counts[item.item_type.value] = checklist_item_counts.get(item.item_type.value, 0) + 1
    general_count = (
        db.query(DestinationRequirement).filter(DestinationRequirement.destination_id == destination_id).count()
    )
    if general_count:
        checklist_item_counts["general_requirement"] = general_count

    alternatives: list[AlternativeOut] = []
    if is_owned:
        alt_rows = (
            db.query(DestinationAlternative)
            .filter(DestinationAlternative.destination_id == destination_id)
            .order_by(DestinationAlternative.order_index)
            .all()
        )
        alt_dest_ids = [r.alternative_destination_id for r in alt_rows]
        alt_destinations = {
            dd.id: dd
            for dd in db.query(Destination).filter(Destination.id.in_(alt_dest_ids), Destination.is_published.is_(True)).all()
        }
        alt_names = translate_bulk(db, "destination.name", list(alt_destinations.keys()), locale)
        for r in alt_rows:
            alt_d = alt_destinations.get(r.alternative_destination_id)
            if alt_d is None:
                continue
            alternatives.append(
                AlternativeOut(
                    destination_id=alt_d.id,
                    name=alt_names.get(alt_d.id, alt_d.name),
                    category=alt_d.category,
                    note=r.note,
                )
            )

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
        mechanism_config=d.mechanism_config,
        checklist_item_counts=checklist_item_counts,
        application_url=d.application_url if is_owned else None,
        alternatives=alternatives,
    )


_ICS_WEEKDAY = {
    "monday": "MO", "tuesday": "TU", "wednesday": "WE", "thursday": "TH",
    "friday": "FR", "saturday": "SA", "sunday": "SU",
}


def _ics_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


@router.get("/{destination_id}/calendar.ics")
def get_calendar_ics(
    destination_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    """Spec addendum: Pre-Purchase Trust Signals + Post-Purchase Tool Features
    §2.2 - owners only, an .ics file for the next computed release date.
    weekly_release destinations get a recurring event (RRULE); everything
    else is a single one-off event, since an annual date can shift slightly
    year to year and a naive yearly recurrence could mislead."""
    d = db.get(Destination, destination_id)
    if d is None or not d.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Destination not found")
    if not user_owns_destination(db, user, destination_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Unlock this destination first")

    start = compute_next_release(d.mechanism_type.value, d.mechanism_config)
    if start is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No fixed release date to add to a calendar")

    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dtstart = start.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary = _ics_escape(f"{d.name} - application window opens")

    rrule_line = ""
    if d.mechanism_type.value == "weekly_release":
        byday = _ICS_WEEKDAY[d.mechanism_config["release_weekday"]]
        rrule_line = f"RRULE:FREQ=WEEKLY;BYDAY={byday}\r\n"

    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Permit Tracker//EN\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{d.id}@permit-tracker\r\n"
        f"DTSTAMP:{dtstamp}\r\n"
        f"DTSTART:{dtstart}\r\n"
        f"SUMMARY:{summary}\r\n"
        f"{rrule_line}"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    filename = f"{d.name.lower().replace(' ', '-')}.ics"
    return Response(
        content=ics,
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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

    is_owned = user_owns_destination(db, user, destination_id)
    if not is_owned:
        return DestinationChecklistOut(is_owned=False, items=[])

    completed_ids = completed_prep_item_ids(db, user.id if user else None, destination_id)
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
                is_completed=dr.id in completed_ids,
                link_url=dr.action_url,
            )
        )

    # Sections 2 & 3: destination-specific checklist items - "Specific to this
    # permit" (section="specific") and "Good to know" (section="good_to_know").
    checklist_texts = translate_bulk(db, "checklist_item.text", [item.id for item in d.checklist_items], locale)
    for item in d.checklist_items:
        text = checklist_texts.get(item.id) or item.text_key
        items.append(
            PrepItemOut(
                id=item.id,
                section=item.section.value,
                type=item.item_type.value,
                order_index=item.order_index,
                is_required=item.is_required,
                text=text,
                is_completed=item.id in completed_ids,
                link_url=item.link_url,
            )
        )

    # Section 4: the user's own free-text additions - personal, never shown
    # to other users.
    custom_items = (
        db.query(UserChecklistItem)
        .filter(UserChecklistItem.user_id == user.id, UserChecklistItem.destination_id == destination_id)
        .order_by(UserChecklistItem.order_index)
        .all()
    )
    for c in custom_items:
        items.append(
            PrepItemOut(
                id=c.id,
                section="custom",
                type="custom",
                order_index=c.order_index,
                is_required=False,
                text=c.text,
                is_completed=c.is_completed,
                link_url=None,
            )
        )

    return DestinationChecklistOut(is_owned=True, items=items)


@router.post("/{destination_id}/checklist/{prep_item_id}/toggle")
def toggle_checklist_item(
    destination_id: uuid.UUID,
    prep_item_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    if not user_owns_destination(db, user, destination_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Unlock this destination first")
    is_completed = toggle_completion(db, user.id, destination_id, prep_item_id)
    return {"is_completed": is_completed}


@router.post("/{destination_id}/checklist/custom", response_model=PrepItemOut)
def add_custom_checklist_item(
    destination_id: uuid.UUID,
    body: UserChecklistItemIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PrepItemOut:
    if not user_owns_destination(db, user, destination_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Unlock this destination first")
    if not body.text.strip():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Text can't be empty")
    max_order = (
        db.query(UserChecklistItem)
        .filter(UserChecklistItem.user_id == user.id, UserChecklistItem.destination_id == destination_id)
        .count()
    )
    item = UserChecklistItem(
        user_id=user.id, destination_id=destination_id, text=body.text.strip(), order_index=max_order
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return PrepItemOut(
        id=item.id,
        section="custom",
        type="custom",
        order_index=item.order_index,
        is_required=False,
        text=item.text,
        is_completed=item.is_completed,
        link_url=None,
    )


@router.post("/{destination_id}/checklist/custom/{item_id}/toggle")
def toggle_custom_checklist_item(
    destination_id: uuid.UUID,
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    item = (
        db.query(UserChecklistItem)
        .filter(
            UserChecklistItem.id == item_id,
            UserChecklistItem.user_id == user.id,
            UserChecklistItem.destination_id == destination_id,
        )
        .first()
    )
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    item.is_completed = not item.is_completed
    db.add(item)
    db.commit()
    return {"is_completed": item.is_completed}


@router.delete("/{destination_id}/checklist/custom/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_custom_checklist_item(
    destination_id: uuid.UUID,
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    item = (
        db.query(UserChecklistItem)
        .filter(
            UserChecklistItem.id == item_id,
            UserChecklistItem.user_id == user.id,
            UserChecklistItem.destination_id == destination_id,
        )
        .first()
    )
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    db.delete(item)
    db.commit()
