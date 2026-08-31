import uuid

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.translation import Translation

settings = get_settings()


def translate(db: Session, entity_type: str, entity_id: uuid.UUID, locale: str) -> str | None:
    row = (
        db.query(Translation)
        .filter(
            Translation.entity_type == entity_type,
            Translation.entity_id == entity_id,
            Translation.locale == locale,
        )
        .first()
    )
    if row is not None:
        return row.value
    if locale != settings.default_locale:
        fallback = (
            db.query(Translation)
            .filter(
                Translation.entity_type == entity_type,
                Translation.entity_id == entity_id,
                Translation.locale == settings.default_locale,
            )
            .first()
        )
        if fallback is not None:
            return fallback.value
    return None


def translate_bulk(db: Session, entity_type: str, entity_ids: list[uuid.UUID], locale: str) -> dict[uuid.UUID, str]:
    """Batch version of translate() for a list of entity ids of the same entity_type."""
    if not entity_ids:
        return {}
    rows = (
        db.query(Translation)
        .filter(
            Translation.entity_type == entity_type,
            Translation.entity_id.in_(entity_ids),
            Translation.locale.in_({locale, settings.default_locale}),
        )
        .all()
    )
    by_locale: dict[uuid.UUID, dict[str, str]] = {}
    for row in rows:
        by_locale.setdefault(row.entity_id, {})[row.locale] = row.value

    result: dict[uuid.UUID, str] = {}
    for entity_id in entity_ids:
        locales = by_locale.get(entity_id, {})
        value = locales.get(locale) or locales.get(settings.default_locale)
        if value is not None:
            result[entity_id] = value
    return result
