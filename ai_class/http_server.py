"""HTTP server adapter for browser/API access."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from ai_class.main import App, EchoGeminiClient
from ai_class.settings import Settings, load_settings


class _Handler(BaseHTTPRequestHandler):
    app: App

    def _write_json(self, status: int, body: dict[str, Any]) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _write_html(self, status: int, html: str) -> None:
        payload = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _parse_json(self) -> dict[str, Any] | None:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON payload"})
            return None
        if not isinstance(parsed, dict):
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": "JSON payload must be an object"})
            return None
        return parsed

    def _client_id(self) -> str:
        return self.headers.get("x-forwarded-for") or self.client_address[0]

    def _headers_dict(self) -> dict[str, str]:
        return {k.lower(): v for k, v in self.headers.items()}

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._write_json(HTTPStatus.OK, {"status": "ok"})
            return
        if self.path == "/":
            self._write_html(
                HTTPStatus.OK,
                """
<!doctype html>
<html>
  <head><meta charset=\"utf-8\"><title>AI-Class</title></head>
  <body>
    <h1>AI-Class API</h1>
    <p>Use <code>POST /notes</code> and <code>POST /query</code>.</p>
    <p>Health check: <a href=\"/health\">/health</a></p>
  </body>
</html>
                """.strip(),
            )
            return

        self._write_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        payload = self._parse_json()
        if payload is None:
            return

        if self.path not in {"/notes", "/query"}:
            self._write_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return

        status, body = self.app.handle_request(
            "POST",
            self.path,
            payload=payload,
            headers=self._headers_dict(),
            client_id=self._client_id(),
        )
        self._write_json(status, body)


def create_server(settings: Settings | None = None, gemini_client: Any | None = None) -> ThreadingHTTPServer:
    app = App(gemini_client=gemini_client or EchoGeminiClient(), settings=settings)

    class AppHandler(_Handler):
        pass

    AppHandler.app = app
    return ThreadingHTTPServer((app.settings.app_host, app.settings.app_port), AppHandler)


def run() -> None:
    server = create_server(load_settings())
    host, port = server.server_address
    print(f"Serving AI-Class on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
