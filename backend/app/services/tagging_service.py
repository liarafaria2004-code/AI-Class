from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.note_tag import NoteTag
from app.models.tag import Tag
from app.services.llm_service import call_llm


def infer_tags_for_note(db: Session, note: Note) -> list[Tag]:
    response = call_llm(note.body)
    created_tags: list[Tag] = []

    for candidate in response.get("tags", []):
        name = str(candidate.get("name", "")).strip().lower()
        confidence = float(candidate.get("confidence", 0.0))
        if not name:
            continue

        tag = db.query(Tag).filter(Tag.name == name).one_or_none()
        if tag is None:
            tag = Tag(name=name, confidence=confidence, source_model=response.get("model", "unknown"))
            db.add(tag)
            db.flush()

        note_tag = NoteTag(note_id=note.id, tag_id=tag.id, relevance=confidence)
        db.merge(note_tag)
        created_tags.append(tag)

    db.commit()
    return created_tags
