import uuid
from datetime import datetime

from pydantic import BaseModel


class UserFileOut(BaseModel):
    id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    checklist_item_id: uuid.UUID | None
    user_checklist_item_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
