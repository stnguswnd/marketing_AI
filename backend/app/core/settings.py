from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    app_env: str
    api_prefix: str
    public_api_base_url: str
    backend_cors_origins: tuple[str, ...]
    database_url: str
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str
    asset_storage_dir: str
    webhook_secret: str
    nano_banana_api_key: str
    blog_api_base_url: str
    blog_api_token: str
    observability_slow_request_ms: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_name=os.getenv("APP_NAME", "Marketing AI Demo API"),
            app_version=os.getenv("APP_VERSION", "0.1.0"),
            app_env=os.getenv("APP_ENV", "local"),
            api_prefix=os.getenv("API_PREFIX", "/api/v1"),
            public_api_base_url=os.getenv("PUBLIC_API_BASE_URL", "http://127.0.0.1:8000/api/v1"),
            backend_cors_origins=tuple(_split_csv(os.getenv("BACKEND_CORS_ORIGINS", "http://127.0.0.1:3000"))),
            database_url=os.getenv("DATABASE_URL", "postgresql+psycopg://harness:harness@127.0.0.1:5432/harness"),
            redis_url=os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"),
            celery_broker_url=os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/1"),
            celery_result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/2"),
            asset_storage_dir=os.getenv("ASSET_STORAGE_DIR", "/tmp/marketing_ai_uploads"),
            webhook_secret=os.getenv("WEBHOOK_SECRET", "dev-webhook-secret"),
            nano_banana_api_key=os.getenv("NANO_BANANA_API_KEY", ""),
            blog_api_base_url=os.getenv("BLOG_API_BASE_URL", "https://blog.example.com/api"),
            blog_api_token=os.getenv("BLOG_API_TOKEN", ""),
            observability_slow_request_ms=int(os.getenv("OBSERVABILITY_SLOW_REQUEST_MS", "1500")),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
