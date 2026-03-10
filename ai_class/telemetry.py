"""Request logging and error telemetry."""

from __future__ import annotations

import logging
from typing import Any


class Telemetry:
    def __init__(self, enabled: bool, level: str = "INFO") -> None:
        self.enabled = enabled
        self.logger = logging.getLogger("ai_class")
        self.logger.setLevel(level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            self.logger.addHandler(handler)

    def log_request(self, method: str, path: str, status_code: int) -> None:
        if self.enabled:
            self.logger.info("request method=%s path=%s status=%s", method, path, status_code)

    def log_error(self, error: Exception, context: dict[str, Any] | None = None) -> None:
        if self.enabled:
            self.logger.error("error=%s context=%s", error, context or {})
