"""Centralized application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass


class SettingsError(Exception):
    """Raised when environment configuration is invalid."""


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str
    app_name: str
    app_host: str
    app_port: int
    app_debug: bool

    gemini_api_key: str
    database_url: str

    enable_api_key_auth: bool
    api_key: str
    rate_limit_per_minute: int

    log_level: str
    telemetry_enabled: bool


def _validate(settings: Settings) -> Settings:
    if not (1 <= settings.app_port <= 65535):
        raise SettingsError("APP_PORT must be between 1 and 65535")
    if settings.rate_limit_per_minute <= 0:
        raise SettingsError("RATE_LIMIT_PER_MINUTE must be > 0")
    if settings.enable_api_key_auth and not settings.api_key:
        raise SettingsError("API_KEY must be set when ENABLE_API_KEY_AUTH=true")
    return settings


def load_settings() -> Settings:
    settings = Settings(
        app_env=os.getenv("APP_ENV", "development"),
        app_name=os.getenv("APP_NAME", "AI-Class"),
        app_host=os.getenv("APP_HOST", "0.0.0.0"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        app_debug=_bool_env("APP_DEBUG", True),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./notes.db"),
        enable_api_key_auth=_bool_env("ENABLE_API_KEY_AUTH", False),
        api_key=os.getenv("API_KEY", ""),
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        telemetry_enabled=_bool_env("TELEMETRY_ENABLED", True),
    )
    return _validate(settings)
