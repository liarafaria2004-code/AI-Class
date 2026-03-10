from typing import Any


def retrieve_notes(query: str) -> list[dict[str, Any]]:
    """Stub retrieval pipeline for semantic search and reranking."""
    return [
        {
            "note_id": 0,
            "score": 0.0,
            "snippet": f"Retrieval pipeline not yet implemented for query: {query}",
        }
    ]
