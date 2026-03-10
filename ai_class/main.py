"""Minimal HTTP-like app with note and query endpoints."""

from __future__ import annotations

import json
from typing import Any

from ai_class.gemini import GeminiClient, parse_model_output
from ai_class.models import NoteInput, QueryInput, ValidationError
from ai_class.rate_limit import InMemoryRateLimiter, RateLimitExceeded
from ai_class.repository import NoteRepository, rank_notes
from ai_class.security import UnauthorizedError, verify_api_key
from ai_class.settings import Settings, SettingsError, load_settings
from ai_class.telemetry import Telemetry


class DependencyError(Exception):
    pass


class App:
    def __init__(self, gemini_client: GeminiClient, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()
        self.repo = NoteRepository()
        self.gemini_client = gemini_client
        self.rate_limiter = InMemoryRateLimiter(self.settings.rate_limit_per_minute)
        self.telemetry = Telemetry(enabled=self.settings.telemetry_enabled, level=self.settings.log_level)

    def handle_request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        client_id: str = "anonymous",
    ) -> tuple[int, dict[str, Any]]:
        payload = payload or {}
        headers = {k.lower(): v for k, v in (headers or {}).items()}

        try:
            verify_api_key(headers, self.settings)
            if method == "POST" and path == "/notes":
                status, body = self._post_notes(payload)
            elif method == "POST" and path == "/query":
                self.rate_limiter.check(client_id)
                status, body = self._post_query(payload)
            else:
                status, body = 404, {"error": "Not found"}
        except UnauthorizedError as exc:
            status, body = 401, {"error": str(exc)}
        except ValidationError as exc:
            status, body = 400, {"error": str(exc)}
        except RateLimitExceeded as exc:
            status, body = 429, {"error": str(exc)}
        except (DependencyError, SettingsError) as exc:
            status, body = 503, {"error": str(exc)}
        except Exception as exc:  # safety net with telemetry
            self.telemetry.log_error(exc, context={"method": method, "path": path})
            status, body = 500, {"error": "internal server error"}

        self.telemetry.log_request(method, path, status)
        return status, body

    def _post_notes(self, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        note_in = NoteInput.from_payload(payload)
        note = self.repo.add(note_in.text, note_in.tags)
        return 201, {"id": note.id, "text": note.text, "tags": note.tags}

    def _post_query(self, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        if not self.settings.gemini_api_key:
            raise DependencyError("GEMINI_API_KEY is not configured")

        query_in = QueryInput.from_payload(payload)
        ranked = rank_notes(query_in.query, self.repo.all())[: query_in.top_k]
        context = [{"id": n.id, "text": n.text, "tags": n.tags} for n in ranked]
        raw = self.gemini_client.answer(query_in.query, context)
        parsed = parse_model_output(raw)
        return 200, {"result": parsed, "context_count": len(context)}


class EchoGeminiClient(GeminiClient):
    def answer(self, query: str, context: list[dict[str, Any]]) -> str:
        return json.dumps({"answer": f"Echo: {query}", "citations": [str(item["id"]) for item in context]})
