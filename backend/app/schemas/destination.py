import uuid
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


class DestinationDetailOut(BaseModel):
    id: uuid.UUID
    country: str
    category: Category
    name: str
    description: str | None
    mechanism_type: MechanismType
    mechanism_explanation: str
    issuing_authority: IssuingAuthority
    competitiveness_level: CompetitivenessLevel
    source_url: str
    last_verified_at: datetime | None
    price_usd: float
    is_owned: bool
    next_known_release: datetime | None
    # Only populated when is_owned is True - gated server-side, not just hidden in the UI.
    mechanism_config: dict | None = None


class DestinationChecklistOut(BaseModel):
    is_owned: bool
    items: list[PrepItemOut] = []
