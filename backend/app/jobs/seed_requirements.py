"""
Seeds general_requirements (spec addendum §2.5) and attaches them to the relevant
MVP destinations. Idempotent: skips general requirements that already exist by key
(title_key), and skips a destination<->requirement link if already attached.

Run via: python -m app.jobs.seed_requirements (after python -m app.jobs.seed)
"""
from app.db import SessionLocal
from app.jobs.seed_data_requirements import (
    DESTINATION_REQUIREMENT_LINKS,
    GENERAL_REQUIREMENTS,
    _NON_DOMESTIC_COUNTRIES,
)
from app.models.destination import Destination
from app.models.general_requirement import DestinationRequirement, GeneralRequirement
from app.models.translation import Translation

GENERAL_DEFAULT_KEYS = ["passport_validity", "travel_insurance_general"]


def run() -> None:
    db = SessionLocal()
    try:
        requirement_ids: dict[str, object] = {}

        for entry in GENERAL_REQUIREMENTS:
            existing = db.query(GeneralRequirement).filter(GeneralRequirement.title_key == entry["key"]).first()
            if existing is not None:
                requirement_ids[entry["key"]] = existing.id
                continue

            g = GeneralRequirement(
                requirement_type=entry["requirement_type"],
                title_key=entry["key"],
                description_key=f"{entry['key']}.description",
                is_general_default=entry["is_general_default"],
            )
            db.add(g)
            db.flush()
            requirement_ids[entry["key"]] = g.id

            db.add(Translation(entity_type="general_requirement.title", entity_id=g.id, locale="en", value=entry["title_en"]))
            db.add(Translation(entity_type="general_requirement.description", entity_id=g.id, locale="en", value=entry["description_en"]))
            # entry["title_he"] / entry["description_he"] intentionally not loaded -
            # multilingual content is paused for now (English-only launch, see
            # README.md). They stay archived here in seed_data_requirements.py.

        db.commit()

        def attach(destination_id, requirement_key: str, note_en: str | None, note_he: str | None) -> None:
            general_requirement_id = requirement_ids[requirement_key]
            existing = (
                db.query(DestinationRequirement)
                .filter(
                    DestinationRequirement.destination_id == destination_id,
                    DestinationRequirement.general_requirement_id == general_requirement_id,
                )
                .first()
            )
            if existing is not None:
                return
            dr = DestinationRequirement(
                destination_id=destination_id,
                general_requirement_id=general_requirement_id,
                destination_specific_note_key=f"note.{requirement_key}" if note_en else None,
            )
            db.add(dr)
            db.flush()
            if note_en:
                db.add(Translation(entity_type="destination_requirement.note", entity_id=dr.id, locale="en", value=note_en))
            # note_he intentionally not loaded - multilingual content is paused for
            # now (English-only launch, see README.md). Stays archived in the
            # DESTINATION_REQUIREMENT_LINKS tuples in seed_data_requirements.py.

        destinations = db.query(Destination).all()
        by_name = {d.name: d for d in destinations}

        attached_count = 0
        for d in destinations:
            if d.country in _NON_DOMESTIC_COUNTRIES:
                for key in GENERAL_DEFAULT_KEYS:
                    attach(d.id, key, None, None)
                    attached_count += 1

        for name, key, note_en, note_he in DESTINATION_REQUIREMENT_LINKS:
            d = by_name.get(name)
            if d is None:
                continue
            attach(d.id, key, note_en, note_he)
            attached_count += 1

        db.commit()
        print(f"Seeded {len(requirement_ids)} general requirements, attempted {attached_count} attachments.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
