from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.note import Note
from app.services.tagging_service import infer_tags_for_note

router = APIRouter(prefix="/notes", tags=["notes"])


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)


class NoteOut(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.post("", response_model=NoteOut, summary="Create a note")
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> Note:
    note = Note(title=payload.title, body=payload.body)
    db.add(note)
    db.commit()
    db.refresh(note)

    infer_tags_for_note(db, note)
    return note
