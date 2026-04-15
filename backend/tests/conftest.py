import os
import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = "sqlite+pysqlite:////tmp/marketing_ai_test.db"
    os.environ["ASSET_STORAGE_DIR"] = "/tmp/marketing_ai_test_uploads"
    os.environ["PUBLIC_API_BASE_URL"] = "http://testserver/api/v1"

    from app.core.settings import get_settings

    get_settings.cache_clear()
    import app.db.session as session_module
    import app.db.bootstrap as bootstrap_module
    import app.main as main_module

    importlib.reload(session_module)
    importlib.reload(bootstrap_module)
    importlib.reload(main_module)
    bootstrap_module.reset_database_schema()
    app_instance = main_module.create_app()
    yield app_instance

    os.environ.pop("APP_ENV", None)
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("ASSET_STORAGE_DIR", None)
    os.environ.pop("PUBLIC_API_BASE_URL", None)
    get_settings.cache_clear()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def merchant_headers():
    return {
        "X-Role": "merchant",
        "X-Test-Role": "merchant",
        "X-Actor-Id": "user_001",
        "X-Test-User-Id": "user_001",
        "X-Merchant-Id": "m_123",
        "X-Test-Merchant-Id": "m_123",
    }


@pytest.fixture
def admin_headers():
    return {
        "X-Role": "admin",
        "X-Test-Role": "admin",
        "X-Actor-Id": "admin_001",
        "X-Test-User-Id": "admin_001",
    }


@pytest.fixture
def operator_headers():
    return {
        "X-Role": "operator",
        "X-Test-Role": "operator",
        "X-Actor-Id": "operator_001",
        "X-Test-User-Id": "operator_001",
    }


@pytest.fixture
def webhook_headers():
    return {
        "X-Webhook-Token": "dev-webhook-secret",
        "X-Test-Webhook-Token": "dev-webhook-secret",
    }


def create_uploaded_asset(client: TestClient, headers: dict[str, str], merchant_id: str) -> str:
    asset_response = client.post(
        "/api/v1/assets/upload-init",
        json={
            "merchant_id": merchant_id,
            "filename": "menu-photo.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 204800,
        },
        headers=headers,
    )
    asset_id = asset_response.json()["asset_id"]
    upload_response = client.post(
        f"/api/v1/assets/{asset_id}/binary",
        files={"file": ("menu-photo.jpg", b"fake-jpeg-binary", "image/jpeg")},
        headers=headers,
    )
    assert upload_response.status_code == 200
    return asset_id


@pytest.fixture
def uploaded_asset_factory(client: TestClient):
    return lambda headers, merchant_id: create_uploaded_asset(client, headers, merchant_id)
