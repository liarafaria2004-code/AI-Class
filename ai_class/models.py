"""Domain models and input validation."""

from __future__ import annotations

from dataclasses import dataclass


class ValidationError(Exception):
    pass


@dataclass
class NoteInput:
    text: str
    tags: list[str]

    @classmethod
    def from_payload(cls, payload: dict) -> "NoteInput":
        text = payload.get("text", "")
        tags = payload.get("tags", [])

        if not isinstance(text, str) or not text.strip():
            raise ValidationError("text must be a non-empty string")
        if len(text) > 2000:
            raise ValidationError("text must be <= 2000 chars")
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            raise ValidationError("tags must be a list of strings")

        normalized_tags = normalize_tags(tags)
        return cls(text=text.strip(), tags=normalized_tags)


@dataclass
class QueryInput:
    query: str
    top_k: int = 3

    @classmethod
    def from_payload(cls, payload: dict) -> "QueryInput":
        query = payload.get("query", "")
        top_k = payload.get("top_k", 3)

        if not isinstance(query, str) or not query.strip():
            raise ValidationError("query must be a non-empty string")
        if len(query) > 500:
            raise ValidationError("query must be <= 500 chars")
        if not isinstance(top_k, int) or not (1 <= top_k <= 20):
            raise ValidationError("top_k must be an integer in [1, 20]")

        return cls(query=query.strip(), top_k=top_k)


def normalize_tags(tags: list[str]) -> list[str]:
    cleaned = [tag.strip().lower() for tag in tags if tag.strip()]
    return sorted(set(cleaned))
