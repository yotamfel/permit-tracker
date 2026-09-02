import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.checklist_item import ChecklistItem
from app.models.user import User
from app.models.user_checklist_item import UserChecklistItem
from app.models.user_file import ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE_BYTES, UserFile, UserFileAttachment
from app.schemas.user_file import AttachFileRequest, UserFileOut
from app.services.ownership import user_owns_destination

router = APIRouter(prefix="/api/me/files", tags=["user-files"])


def _validate_attachment_target(
    db: Session, user: User, checklist_item_id: uuid.UUID | None, user_checklist_item_id: uuid.UUID | None
) -> None:
    if checklist_item_id is not None and user_checklist_item_id is not None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "A file can attach to at most one checklist row at a time")
    if checklist_item_id is None and user_checklist_item_id is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Specify which checklist row to attach to")
    if checklist_item_id is not None:
        item = db.get(ChecklistItem, checklist_item_id)
        if item is None or not user_owns_destination(db, user, item.destination_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Checklist item not found")
    if user_checklist_item_id is not None:
        item = db.get(UserChecklistItem, user_checklist_item_id)
        if item is None or item.user_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Checklist item not found")


def _file_out(db: Session, f: UserFile) -> UserFileOut:
    attachments = db.query(UserFileAttachment).filter(UserFileAttachment.file_id == f.id).all()
    out = UserFileOut.model_validate(f)
    out.attachments = attachments
    return out


@router.get("", response_model=list[UserFileOut])
def list_files(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[UserFileOut]:
    files = db.query(UserFile).filter(UserFile.user_id == user.id).order_by(UserFile.created_at.desc()).all()
    return [_file_out(db, f) for f in files]


@router.post("", response_model=UserFileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    checklist_item_id: uuid.UUID | None = Form(None),
    user_checklist_item_id: uuid.UUID | None = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserFileOut:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Only images and PDFs are supported")
    data = await file.read()
    if len(data) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "File is larger than the 10MB limit")

    # Uploading directly from a checklist row optionally attaches it in the
    # same step; uploading from the general library (Account page) leaves
    # both null - the file just sits there until explicitly attached.
    if checklist_item_id is not None or user_checklist_item_id is not None:
        _validate_attachment_target(db, user, checklist_item_id, user_checklist_item_id)

    record = UserFile(
        user_id=user.id,
        filename=file.filename or "upload",
        content_type=file.content_type,
        size_bytes=len(data),
        data=data,
    )
    db.add(record)
    db.flush()

    if checklist_item_id is not None or user_checklist_item_id is not None:
        db.add(
            UserFileAttachment(
                file_id=record.id, checklist_item_id=checklist_item_id, user_checklist_item_id=user_checklist_item_id
            )
        )

    db.commit()
    db.refresh(record)
    return _file_out(db, record)


@router.post("/{file_id}/attach", response_model=UserFileOut)
def attach_file(
    file_id: uuid.UUID, body: AttachFileRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> UserFileOut:
    record = db.get(UserFile, file_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    _validate_attachment_target(db, user, body.checklist_item_id, body.user_checklist_item_id)

    existing = (
        db.query(UserFileAttachment)
        .filter(
            UserFileAttachment.file_id == file_id,
            UserFileAttachment.checklist_item_id == body.checklist_item_id,
            UserFileAttachment.user_checklist_item_id == body.user_checklist_item_id,
        )
        .first()
    )
    if existing is None:
        db.add(
            UserFileAttachment(
                file_id=file_id, checklist_item_id=body.checklist_item_id, user_checklist_item_id=body.user_checklist_item_id
            )
        )
        db.commit()
    return _file_out(db, record)


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_attachment(attachment_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    attachment = db.get(UserFileAttachment, attachment_id)
    if attachment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Attachment not found")
    record = db.get(UserFile, attachment.file_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Attachment not found")
    db.delete(attachment)
    db.commit()


@router.get("/{file_id}/download")
def download_file(file_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    record = db.get(UserFile, file_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    return Response(
        content=record.data,
        media_type=record.content_type,
        headers={"Content-Disposition": f'inline; filename="{record.filename}"'},
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    record = db.get(UserFile, file_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    db.delete(record)
    db.commit()
