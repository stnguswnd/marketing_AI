from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or key in os.environ:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ[key] = value


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
    openai_api_key: str
    openai_api_base_url: str
    openai_model: str
    nano_banana_api_key: str
    nano_banana_api_base_url: str
    nano_banana_model: str
    nano_banana_timeout_ms: int
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
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_api_base_url=os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            nano_banana_api_key=os.getenv("NANO_BANANA_API_KEY", ""),
            nano_banana_api_base_url=os.getenv("NANO_BANANA_API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"),
            nano_banana_model=os.getenv("NANO_BANANA_MODEL", "gemini-2.5-flash-image"),
            nano_banana_timeout_ms=int(os.getenv("NANO_BANANA_TIMEOUT_MS", "30000")),
            blog_api_base_url=os.getenv("BLOG_API_BASE_URL", "https://blog.example.com/api"),
            blog_api_token=os.getenv("BLOG_API_TOKEN", ""),
            observability_slow_request_ms=int(os.getenv("OBSERVABILITY_SLOW_REQUEST_MS", "1500")),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _load_dotenv()
    return Settings.from_env()
