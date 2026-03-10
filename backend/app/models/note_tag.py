from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class NoteTag(Base):
    __tablename__ = "note_tags"

    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    relevance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    note = relationship("Note", back_populates="tags")
    tag = relationship("Tag", back_populates="notes")
