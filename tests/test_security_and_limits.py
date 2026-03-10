from ai_class.main import App
from ai_class.settings import Settings, SettingsError, load_settings


class MockGemini:
    def answer(self, query, context):
        return '{"answer":"ok","citations":[]}'


def settings(**overrides):
    base = Settings(
        app_env="test",
        app_name="AI-Class",
        app_host="0.0.0.0",
        app_port=8000,
        app_debug=False,
        gemini_api_key="test",
        database_url="sqlite:///test.db",
        enable_api_key_auth=False,
        api_key="",
        rate_limit_per_minute=1,
        log_level="INFO",
        telemetry_enabled=False,
    )
    return Settings(**{**base.__dict__, **overrides})


def test_api_key_auth_enforced_when_enabled():
    app = App(MockGemini(), settings=settings(enable_api_key_auth=True, api_key="secret"))
    status, _ = app.handle_request("POST", "/notes", payload={"text": "hi", "tags": []})
    assert status == 401


def test_rate_limit_applies_to_query_endpoint():
    app = App(MockGemini(), settings=settings(rate_limit_per_minute=1))
    first_status, _ = app.handle_request("POST", "/query", payload={"query": "q", "top_k": 1}, client_id="u1")
    second_status, _ = app.handle_request("POST", "/query", payload={"query": "q", "top_k": 1}, client_id="u1")
    assert first_status == 200
    assert second_status == 429


def test_load_settings_rejects_invalid_rate_limit(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "0")
    try:
        load_settings()
        assert False, "Expected SettingsError"
    except SettingsError as exc:
        assert "RATE_LIMIT_PER_MINUTE" in str(exc)
