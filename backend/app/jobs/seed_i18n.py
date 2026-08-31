"""
Loads the draft machine-translated content from seed_data_i18n.py into the
translations table for he/de/fr/es/pt-BR (English is already seeded by seed.py /
seed_requirements.py as the source-of-truth locale).

Run via: python -m app.jobs.seed_i18n (after seed.py and seed_requirements.py)

Every row written here is a first-draft machine translation - see README.md's
"Decisions made where the spec was ambiguous" section. Nothing here is marked
last_verified_at or otherwise treated as human-confirmed.
"""
from app.db import SessionLocal
from app.jobs.seed_data_i18n import (
    DESTINATION_REQUIREMENT_NOTE_TRANSLATIONS,
    DESTINATION_TRANSLATIONS,
    GENERAL_REQUIREMENT_TRANSLATIONS,
)
from app.models.checklist_item import ChecklistItem
from app.models.destination import Destination
from app.models.general_requirement import DestinationRequirement, GeneralRequirement
from app.models.translation import Translation

DESTINATION_LOCALES = ["he", "de", "fr", "es", "pt-BR"]
REQUIREMENT_LOCALES = ["de", "fr", "es", "pt-BR"]


def _upsert(db, entity_type: str, entity_id, locale: str, value: str) -> None:
    if not value:
        return
    existing = (
        db.query(Translation)
        .filter(Translation.entity_type == entity_type, Translation.entity_id == entity_id, Translation.locale == locale)
        .first()
    )
    if existing is not None:
        existing.value = value
        db.add(existing)
    else:
        db.add(Translation(entity_type=entity_type, entity_id=entity_id, locale=locale, value=value))


def run() -> None:
    db = SessionLocal()
    written = 0
    try:
        destinations_by_name = {d.name: d for d in db.query(Destination).all()}

        for dest_name, locale_map in DESTINATION_TRANSLATIONS.items():
            d = destinations_by_name.get(dest_name)
            if d is None:
                print(f"WARN: destination not found in DB, skipping translations: {dest_name}")
                continue

            checklist_items = (
                db.query(ChecklistItem)
                .filter(ChecklistItem.destination_id == d.id)
                .order_by(ChecklistItem.order_index)
                .all()
            )

            for locale in DESTINATION_LOCALES:
                content = locale_map.get(locale)
                if not content:
                    continue
                _upsert(db, "destination.name", d.id, locale, content.get("name"))
                _upsert(db, "destination.description", d.id, locale, content.get("description"))
                _upsert(db, "destination.mechanism_explanation", d.id, locale, content.get("mechanism_explanation"))
                written += 3

                checklist_text = content.get("checklist") or []
                if len(checklist_text) != len(checklist_items):
                    print(
                        f"WARN: checklist length mismatch for {dest_name} [{locale}]: "
                        f"{len(checklist_text)} translations vs {len(checklist_items)} items - skipping checklist translations"
                    )
                    continue
                for item, text in zip(checklist_items, checklist_text):
                    _upsert(db, "checklist_item.text", item.id, locale, text)
                    written += 1

        general_requirements_by_key = {g.title_key: g for g in db.query(GeneralRequirement).all()}
        for key, locale_map in GENERAL_REQUIREMENT_TRANSLATIONS.items():
            g = general_requirements_by_key.get(key)
            if g is None:
                print(f"WARN: general requirement not found, skipping: {key}")
                continue
            for locale in REQUIREMENT_LOCALES:
                content = locale_map.get(locale)
                if not content:
                    continue
                _upsert(db, "general_requirement.title", g.id, locale, content.get("title"))
                _upsert(db, "general_requirement.description", g.id, locale, content.get("description"))
                written += 2

        for (dest_name, req_key), locale_map in DESTINATION_REQUIREMENT_NOTE_TRANSLATIONS.items():
            d = destinations_by_name.get(dest_name)
            g = general_requirements_by_key.get(req_key)
            if d is None or g is None:
                continue
            dr = (
                db.query(DestinationRequirement)
                .filter(DestinationRequirement.destination_id == d.id, DestinationRequirement.general_requirement_id == g.id)
                .first()
            )
            if dr is None:
                continue
            for locale in REQUIREMENT_LOCALES:
                note = locale_map.get(locale)
                if not note:
                    continue
                _upsert(db, "destination_requirement.note", dr.id, locale, note)
                written += 1

        db.commit()
        print(f"Wrote/updated {written} translation rows.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
