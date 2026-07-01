import importlib

from fastapi.testclient import TestClient


def load_app(monkeypatch, origins, app_env="production"):
    monkeypatch.setenv("APP_ENV", app_env)
    monkeypatch.setenv("CORS_ORIGINS", origins)
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role")
    from app.core.config import get_settings
    from app.services import repository
    import app.main as main

    repository._REPO = None
    get_settings.cache_clear()
    reloaded = importlib.reload(main)
    return reloaded.app, get_settings


def preflight(client, path, origin, request_headers="Content-Type, Authorization"):
    return client.options(
        path,
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": request_headers,
        },
    )


def test_chat_preflight_allows_configured_origins(monkeypatch):
    origin = "https://finguard-cx.vercel.app"
    app, get_settings = load_app(monkeypatch, f"{origin}/")
    try:
        client = TestClient(app)

        chat = preflight(client, "/api/v1/chat", origin)
        stream = preflight(client, "/api/v1/chat/stream", origin)

        assert chat.status_code in {200, 204}
        assert stream.status_code in {200, 204}
        assert chat.headers["access-control-allow-origin"] == origin
        assert stream.headers["access-control-allow-origin"] == origin
    finally:
        monkeypatch.delenv("APP_ENV", raising=False)
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
        get_settings.cache_clear()


def test_chat_preflight_allows_browser_requested_headers(monkeypatch):
    origin = "https://finguard-cx.vercel.app"
    app, get_settings = load_app(monkeypatch, origin)
    try:
        client = TestClient(app)

        chat = preflight(client, "/api/v1/chat", origin, "content-type, x-requested-with")
        stream = preflight(client, "/api/v1/chat/stream", origin, "content-type, x-requested-with")

        assert chat.status_code in {200, 204}
        assert stream.status_code in {200, 204}
        assert chat.headers["access-control-allow-origin"] == origin
        assert stream.headers["access-control-allow-origin"] == origin
        assert "x-requested-with" in chat.headers["access-control-allow-headers"].lower()
    finally:
        monkeypatch.delenv("APP_ENV", raising=False)
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
        get_settings.cache_clear()


def test_chat_preflight_rejects_disallowed_origins(monkeypatch):
    app, get_settings = load_app(monkeypatch, "https://finguard-cx.vercel.app")
    try:
        client = TestClient(app)

        response = preflight(client, "/api/v1/chat", "https://evil.example")

        assert response.status_code == 400
        assert "access-control-allow-origin" not in response.headers
    finally:
        monkeypatch.delenv("APP_ENV", raising=False)
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
        get_settings.cache_clear()


def test_localhost_preflight_still_works_in_development(monkeypatch):
    app, get_settings = load_app(monkeypatch, "https://finguard-cx.vercel.app", app_env="local")
    try:
        client = TestClient(app)

        response = preflight(client, "/api/v1/chat", "http://localhost:3000")

        assert response.status_code in {200, 204}
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    finally:
        monkeypatch.delenv("APP_ENV", raising=False)
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
        get_settings.cache_clear()
