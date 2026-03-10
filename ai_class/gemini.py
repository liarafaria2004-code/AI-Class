"""Gemini client abstraction and safe response parsing."""

from __future__ import annotations

import json
from typing import Any


class GeminiClient:
    def answer(self, query: str, context: list[dict[str, Any]]) -> str:
        raise NotImplementedError


def _strip_code_fence(raw_output: str) -> str:
    output = raw_output.strip()
    if output.startswith("```") and output.endswith("```"):
        lines = output.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return raw_output


def parse_model_output(raw_output: str) -> dict[str, Any]:
    cleaned_output = _strip_code_fence(raw_output)
    try:
        obj = json.loads(cleaned_output)
    except json.JSONDecodeError:
        return {"answer": "", "citations": [], "raw": raw_output, "parse_error": True}

    if not isinstance(obj, dict):
        return {"answer": "", "citations": [], "raw": raw_output, "parse_error": True}

    answer = obj.get("answer") if isinstance(obj.get("answer"), str) else ""
    citations = obj.get("citations") if isinstance(obj.get("citations"), list) else []

    return {
        "answer": answer,
        "citations": [c for c in citations if isinstance(c, str)],
        "raw": raw_output,
        "parse_error": False,
    }
