import uuid
from datetime import datetime

from pydantic import BaseModel


class UserFileAttachmentOut(BaseModel):
    id: uuid.UUID
    checklist_item_id: uuid.UUID | None
    user_checklist_item_id: uuid.UUID | None

    model_config = {"from_attributes": True}


class UserFileOut(BaseModel):
    id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime
    attachments: list[UserFileAttachmentOut] = []

    model_config = {"from_attributes": True}


class AttachFileRequest(BaseModel):
    checklist_item_id: uuid.UUID | None = None
    user_checklist_item_id: uuid.UUID | None = None
