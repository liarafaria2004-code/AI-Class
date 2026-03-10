"""Security helpers for API key auth."""

from __future__ import annotations

from ai_class.settings import Settings


class UnauthorizedError(Exception):
    pass


def verify_api_key(headers: dict[str, str], settings: Settings) -> None:
    if not settings.enable_api_key_auth:
        return

    header_key = headers.get("x-api-key", "")
    if not settings.api_key or header_key != settings.api_key:
        raise UnauthorizedError("Invalid API key")
