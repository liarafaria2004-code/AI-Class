from typing import Any


def call_llm(prompt: str, *, model_name: str = "mock-tagger-v1") -> dict[str, Any]:
    """Mock LLM call placeholder for future provider integration."""
    return {
        "model": model_name,
        "tags": [
            {"name": "general", "confidence": 0.5},
        ],
        "raw": {"prompt": prompt},
    }
