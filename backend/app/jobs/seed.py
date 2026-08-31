"""
Seeds the 29 MVP destinations (full detail, published) from seed_data.py.
Idempotent: re-running skips destinations that already exist (matched by name).

Run via: python -m app.jobs.seed
"""
from app.db import SessionLocal
from app.jobs.seed_data import DESTINATIONS
from app.models.checklist_item import ChecklistItem
from app.models.destination import Destination
from app.models.translation import Translation


def run() -> None:
    db = SessionLocal()
    created = 0
    try:
        for entry in DESTINATIONS:
            existing = db.query(Destination).filter(Destination.name == entry["name"]).first()
            if existing is not None:
                continue

            d = Destination(
                country=entry["country"],
                category=entry["category"],
                name=entry["name"],
                mechanism_type=entry["mechanism_type"],
                mechanism_config=entry["mechanism_config"],
                issuing_authority=entry["issuing_authority"],
                competitiveness_level=entry["competitiveness_level"],
                source_url=entry["source_url"],
                is_published=True,
                price_usd=4.99,
            )
            db.add(d)
            db.flush()  # assign d.id

            db.add(Translation(entity_type="destination.name", entity_id=d.id, locale="en", value=entry["name"]))
            db.add(
                Translation(
                    entity_type="destination.description", entity_id=d.id, locale="en", value=entry["description_en"]
                )
            )
            db.add(
                Translation(
                    entity_type="destination.mechanism_explanation",
                    entity_id=d.id,
                    locale="en",
                    value=entry["mechanism_explanation_en"],
                )
            )
            # entry["name_he"] is intentionally not loaded - multilingual content is
            # paused for now (English-only launch, see README.md). The Hebrew name
            # stays archived here in seed_data.py for whenever that resumes.

            for index, (item_type, text_en, is_required) in enumerate(entry["checklist"]):
                item = ChecklistItem(
                    destination_id=d.id,
                    item_type=item_type,
                    order_index=index,
                    is_required=is_required,
                    text_key=f"checklist.{d.id}.{index}",
                )
                db.add(item)
                db.flush()
                db.add(
                    Translation(entity_type="checklist_item.text", entity_id=item.id, locale="en", value=text_en)
                )

            created += 1

        db.commit()
    finally:
        db.close()

    print(f"Seeded {created} new MVP destinations (skipped {len(DESTINATIONS) - created} already present).")


if __name__ == "__main__":
    run()
