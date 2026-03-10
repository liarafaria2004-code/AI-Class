"""In-memory note persistence and retrieval."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Note:
    id: int
    text: str
    tags: list[str]


class NoteRepository:
    def __init__(self) -> None:
        self._notes: list[Note] = []
        self._id = 1

    def add(self, text: str, tags: list[str]) -> Note:
        note = Note(id=self._id, text=text, tags=tags)
        self._id += 1
        self._notes.append(note)
        return note

    def all(self) -> list[Note]:
        return list(self._notes)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))


def rank_notes(query: str, notes: list[Note]) -> list[Note]:
    q_tokens = _tokenize(query)

    def score(note: Note) -> tuple[int, int, int]:
        text_tokens = _tokenize(note.text)
        overlap = len(q_tokens.intersection(text_tokens))
        # tie-break by shorter note length and then oldest id for stability
        return (overlap, -len(note.text), -note.id)

    return sorted(notes, key=score, reverse=True)
