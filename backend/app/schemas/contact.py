import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.enums import ContactMessageStatus


class ContactMessageCreate(BaseModel):
    name: str
    email: EmailStr
    message: str


class AdminContactMessageOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    message: str
    status: ContactMessageStatus
    user_id: uuid.UUID | None
    created_at: datetime
    admin_reply: str | None
    replied_at: datetime | None

    model_config = {"from_attributes": True}


class AdminContactMessageStatusUpdate(BaseModel):
    status: ContactMessageStatus


class AdminContactMessageReplyIn(BaseModel):
    message: str
