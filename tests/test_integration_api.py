import json

from ai_class.main import App
from ai_class.settings import Settings


class MockGemini:
    def answer(self, query, context):
        return json.dumps({"answer": f"resolved:{query}", "citations": [str(c["id"]) for c in context]})


def make_settings(**overrides):
    base = Settings(
        app_env="test",
        app_name="AI-Class",
        app_host="0.0.0.0",
        app_port=8000,
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


def test_post_notes_validates_and_creates_note():
    app = App(MockGemini(), settings=make_settings())

    status, body = app.handle_request("POST", "/notes", payload={"text": "  hello world  ", "tags": [" AI ", "ai"]})

    assert status == 201
    assert body["text"] == "hello world"
    assert body["tags"] == ["ai"]


def test_post_query_uses_ranked_context_and_mocked_gemini():
    app = App(MockGemini(), settings=make_settings())
    app.handle_request("POST", "/notes", payload={"text": "python ai", "tags": ["ml"]})
    app.handle_request("POST", "/notes", payload={"text": "python only", "tags": ["code"]})

    status, body = app.handle_request("POST", "/query", payload={"query": "python ai", "top_k": 1})

    assert status == 200
    assert body["context_count"] == 1
    assert body["result"]["answer"] == "resolved:python ai"
    assert body["result"]["citations"] == ["1"]


def test_post_query_returns_503_if_gemini_key_is_missing():
    app = App(MockGemini(), settings=make_settings(gemini_api_key=""))

    status, body = app.handle_request("POST", "/query", payload={"query": "python ai", "top_k": 1})

    assert status == 503
    assert "GEMINI_API_KEY" in body["error"]
