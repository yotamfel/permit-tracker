import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import (
    Category,
    ChecklistItemType,
    CompetitivenessLevel,
    IssuingAuthority,
    MechanismType,
    RequirementType,
    ReviewStatus,
)


class AdminDestinationIn(BaseModel):
    country: str
    category: Category
    name: str
    mechanism_type: MechanismType
    mechanism_config: dict
    issuing_authority: IssuingAuthority
    competitiveness_level: CompetitivenessLevel
    source_url: str
    price_usd: float = 4.99
    is_published: bool = False


class AdminDestinationOut(AdminDestinationIn):
    id: uuid.UUID
    last_verified_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminChecklistItemIn(BaseModel):
    destination_id: uuid.UUID
    item_type: ChecklistItemType
    order_index: int = 0
    is_required: bool = True
    text_key: str


class AdminChecklistItemOut(AdminChecklistItemIn):
    id: uuid.UUID

    model_config = {"from_attributes": True}


class AdminTranslationIn(BaseModel):
    entity_type: str
    entity_id: uuid.UUID
    locale: str
    value: str


class AdminTranslationOut(AdminTranslationIn):
    id: uuid.UUID

    model_config = {"from_attributes": True}


class AdminGeneralRequirementIn(BaseModel):
    requirement_type: RequirementType
    title_key: str
    description_key: str
    is_general_default: bool = False


class AdminGeneralRequirementOut(AdminGeneralRequirementIn):
    id: uuid.UUID

    model_config = {"from_attributes": True}


class AdminDestinationRequirementIn(BaseModel):
    destination_id: uuid.UUID
    general_requirement_id: uuid.UUID
    destination_specific_note_key: str | None = None
    order_index: int = 0


class AdminDestinationRequirementOut(AdminDestinationRequirementIn):
    id: uuid.UUID

    model_config = {"from_attributes": True}


class AdminMonitoringDiffOut(BaseModel):
    id: uuid.UUID
    destination_id: uuid.UUID
    destination_name: str
    previous_text: str | None
    new_text: str
    diff_summary: str
    review_status: ReviewStatus
    reviewed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
