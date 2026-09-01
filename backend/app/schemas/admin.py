import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.enums import (
    Category,
    ChecklistItemSection,
    ChecklistItemType,
    CompetitivenessLevel,
    IssuingAuthority,
    MechanismType,
    RequirementType,
    ReviewStatus,
)


class DestinationPurchaseStatsOut(BaseModel):
    destination_id: uuid.UUID
    destination_name: str
    purchase_count: int
    revenue_usd: float


class PurchaseStatsOut(BaseModel):
    total_purchases: int
    total_revenue_usd: float
    total_accounts: int
    accounts_created_last_7_days: int
    by_destination: list[DestinationPurchaseStatsOut]


class DestinationFeedbackStatsOut(BaseModel):
    destination_id: uuid.UUID
    destination_name: str
    category: Category
    response_count: int
    succeeded_pct: float | None
    helpful_pct: float | None
    comments: list[str]


class FeedbackStatsOut(BaseModel):
    total_responses: int
    overall_succeeded_pct: float | None
    overall_helpful_pct: float | None
    by_destination: list[DestinationFeedbackStatsOut]


class ReviewQueueItemOut(BaseModel):
    id: uuid.UUID
    country: str
    category: Category
    name: str
    mechanism_type: MechanismType
    mechanism_config: dict
    issuing_authority: IssuingAuthority
    competitiveness_level: CompetitivenessLevel
    source_url: str | None
    application_url: str | None
    price_usd: float
    description: str | None = None
    mechanism_explanation: str | None = None
    # Best-available research context for this draft, so the admin can see
    # where the data came from before approving it - source_url if set, else
    # whatever description text (often the original scraped/imported research
    # note) exists for it in any locale. Full source list lives in the
    # separate destination_sources table (see AdminSourceOut).
    source_note: str | None

    model_config = {"from_attributes": True}


class AdminDestinationIn(BaseModel):
    country: str
    category: Category
    name: str
    mechanism_type: MechanismType
    mechanism_config: dict
    issuing_authority: IssuingAuthority
    competitiveness_level: CompetitivenessLevel
    # Nullable to match the DB column - stub destinations (§10) may not have a
    # verified source yet. Admins should fill this in before publishing. This
    # is the single canonical URL the weekly monitoring job re-fetches to
    # detect changes - keep it to one URL, not a list.
    source_url: str | None = None
    # Shown to users as "Apply here" once they've unlocked the destination.
    application_url: str | None = None
    price_usd: float = 4.99
    is_published: bool = False
    # Not Destination model columns - these live in the translations table
    # (locale="en") and are upserted there by the endpoint, not written
    # directly onto the Destination row.
    description: str | None = None
    mechanism_explanation: str | None = None


class AdminDestinationOut(BaseModel):
    id: uuid.UUID
    country: str
    category: Category
    name: str
    mechanism_type: MechanismType
    mechanism_config: dict
    issuing_authority: IssuingAuthority
    competitiveness_level: CompetitivenessLevel
    source_url: str | None
    application_url: str | None
    price_usd: float
    is_published: bool
    last_verified_at: datetime | None
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    mechanism_explanation: str | None = None
    source_fetch_failing: bool = False
    source_fetch_error: str | None = None
    source_fetch_failing_since: datetime | None = None

    model_config = {"from_attributes": True}


class SourceFetchFailureOut(BaseModel):
    destination_id: uuid.UUID
    destination_name: str
    source_url: str | None
    error: str | None
    failing_since: datetime | None

    model_config = {"from_attributes": True}


class AdminChecklistItemIn(BaseModel):
    destination_id: uuid.UUID
    item_type: ChecklistItemType
    section: ChecklistItemSection = ChecklistItemSection.specific
    order_index: int = 0
    is_required: bool = True
    text_key: str
    link_url: str | None = None


class AdminChecklistItemOut(AdminChecklistItemIn):
    id: uuid.UUID

    model_config = {"from_attributes": True}


class AdminSourceIn(BaseModel):
    destination_id: uuid.UUID
    order_index: int = 0
    url: str | None = None
    note: str | None = None


class AdminSourceOut(AdminSourceIn):
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
    order_index: int = 0
    action_url: str | None = None
    # Plain text - the endpoint upserts this into the translations table
    # (entity_type="destination_requirement.note") rather than the client
    # managing destination_specific_note_key directly.
    note: str | None = None


class AdminDestinationRequirementOut(BaseModel):
    id: uuid.UUID
    destination_id: uuid.UUID
    general_requirement_id: uuid.UUID
    general_requirement_title: str
    order_index: int
    action_url: str | None
    note: str | None


class AdminAlternativeIn(BaseModel):
    destination_id: uuid.UUID
    alternative_destination_id: uuid.UUID
    order_index: int = 0
    note: str | None = None


class AdminAlternativeOut(AdminAlternativeIn):
    id: uuid.UUID
    alternative_destination_name: str

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


class AdminFollowUpIn(BaseModel):
    destination_id: uuid.UUID
    due_date: date
    title: str
    notes: str | None = None
    is_done: bool = False


class AdminFollowUpOut(AdminFollowUpIn):
    id: uuid.UUID
    destination_name: str
    created_at: datetime

    model_config = {"from_attributes": True}
