from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source_model: Mapped[str] = mapped_column(String(100), nullable=False, default="unknown")

    notes = relationship("NoteTag", back_populates="tag", cascade="all, delete-orphan")
