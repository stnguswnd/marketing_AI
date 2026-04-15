from __future__ import annotations

from app.core.settings import Settings


def test_settings_from_env_defaults():
    settings = Settings.from_env()

    assert settings.app_name
    assert settings.api_prefix == "/api/v1"
    assert settings.database_url.startswith("postgresql+psycopg://")
    assert settings.redis_url.startswith("redis://")
    assert settings.observability_slow_request_ms > 0
