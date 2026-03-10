import json
import threading
from http.client import HTTPConnection

from ai_class.http_server import create_server
from ai_class.settings import Settings


class MockGemini:
    def answer(self, query, context):
        return json.dumps({"answer": f"resolved:{query}", "citations": [str(c["id"]) for c in context]})


def make_settings(**overrides):
    base = Settings(
        app_env="test",
        app_name="AI-Class",
        app_host="127.0.0.1",
        app_port=0,
        app_debug=False,
        gemini_api_key="test-key",
        database_url="sqlite:///test.db",
        enable_api_key_auth=False,
        api_key="",
        rate_limit_per_minute=100,
        log_level="INFO",
        telemetry_enabled=False,
    )
    return Settings(**{**base.__dict__, **overrides})


def _start_server(server):
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def test_http_server_routes_for_browser_and_api():
    server = create_server(settings=make_settings(), gemini_client=MockGemini())
    _start_server(server)
    host, port = server.server_address

    conn = HTTPConnection(host, port)

    conn.request("GET", "/")
    response = conn.getresponse()
    assert response.status == 200
    assert "AI-Class API" in response.read().decode("utf-8")

    conn.request("GET", "/health")
    response = conn.getresponse()
    assert response.status == 200
    assert json.loads(response.read()) == {"status": "ok"}

    conn.request("POST", "/notes", body=json.dumps({"text": "hello", "tags": ["ai"]}))
    response = conn.getresponse()
    assert response.status == 201
    assert json.loads(response.read())["id"] == 1

    conn.request("POST", "/query", body=json.dumps({"query": "hello", "top_k": 1}))
    response = conn.getresponse()
    body = json.loads(response.read())
    assert response.status == 200
    assert body["result"]["answer"] == "resolved:hello"

    server.shutdown()
    server.server_close()


def test_http_server_rejects_invalid_json():
    server = create_server(settings=make_settings(), gemini_client=MockGemini())
    _start_server(server)
    host, port = server.server_address

    conn = HTTPConnection(host, port)
    conn.request("POST", "/notes", body="{oops")
    response = conn.getresponse()

    assert response.status == 400
    assert "Invalid JSON" in json.loads(response.read())["error"]

    server.shutdown()
    server.server_close()
