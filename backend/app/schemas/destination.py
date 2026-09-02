import uuid
from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Category, CompetitivenessLevel, IssuingAuthority, MechanismType


class PrepItemOut(BaseModel):
    """
    A single row in the unified "what you need to prepare" list (spec addendum §2.3):
    section="general" comes from destination_requirements -> general_requirements,
    section="specific" comes from the original checklist_items table.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    section: str  # "general" | "specific"
    type: str  # RequirementType value for general, ChecklistItemType value for specific
    order_index: int
    is_required: bool
    text: str  # resolved via translations table for the active locale
    is_completed: bool = False
    # Optional link shown under this item (e.g. a form, a directory of
    # registered operators, an insurance provider, the exact official page for
    # this specific step) - any section can have one.
    link_url: str | None = None


class UserChecklistItemIn(BaseModel):
    text: str


class OperatorOut(BaseModel):
    name: str
    url: str | None
    note: str | None


class DestinationCardOut(BaseModel):
    id: uuid.UUID
    country: str
    category: Category
    name: str
    mechanism_type: MechanismType
    issuing_authority: IssuingAuthority
    competitiveness_level: CompetitivenessLevel
    price_usd: float
    next_known_release: datetime | None
    is_owned: bool
    season_start_month: int | None = None
    season_end_month: int | None = None


class AlternativeOut(BaseModel):
    destination_id: uuid.UUID
    name: str
    category: Category
    note: str | None = None


class DestinationDetailOut(BaseModel):
    id: uuid.UUID
    country: str
    category: Category
    name: str
    description: str | None
    mechanism_type: MechanismType
    # Only populated when is_owned is True - gated server-side (same pattern as
    # application_url below). Only the description paragraph and the concrete
    # mechanism_config numbers (below) are free to read before unlocking - the
    # prose explanation of how it works is part of what unlocking pays for.
    mechanism_explanation: str | None
    issuing_authority: IssuingAuthority
    competitiveness_level: CompetitivenessLevel
    last_verified_at: datetime | None
    price_usd: float
    is_owned: bool
    next_known_release: datetime | None
    # Free to everyone (spec addendum: Pre-Purchase Trust Signals §1.3) - shows
    # concrete numbers (quota size, lottery odds, etc.) as a trust/urgency
    # signal, even though the prose mechanism_explanation stays locked above.
    mechanism_config: dict
    # Counts only, not the item text itself (spec addendum §1.2) - e.g. "3
    # documents, 2 registration steps" - computed from "general" + "specific"
    # checklist sections (not "good_to_know", which isn't required for the permit).
    checklist_item_counts: dict[str, int] = {}
    # Only populated when is_owned is True - gated server-side, not just hidden in
    # the UI. source_url is intentionally never exposed here - we don't want to
    # send unlocked users elsewhere; application_url is the "apply here" action
    # link, which is part of what unlocking pays for.
    application_url: str | None = None
    # Only populated when is_owned is True - the neutral fallback when there's
    # no single application_url (multiple legitimate operators, or no online
    # booking system at all): a plain contact list instead of picking one.
    operators: list[OperatorOut] = []
    # Only populated when is_owned is True (spec addendum §2.4) - only
    # suggested when the user already has skin in the game.
    alternatives: list[AlternativeOut] = []


class DestinationChecklistOut(BaseModel):
    is_owned: bool
    items: list[PrepItemOut] = []


class CalendarEntryOut(BaseModel):
    destination_id: uuid.UUID
    name: str
    category: Category
    mechanism_type: MechanismType
    dates: list[date_type]
