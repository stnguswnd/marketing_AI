import os
import importlib

import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def app():
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = "sqlite+pysqlite:////tmp/harness_framework_test.db"

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

    os.environ.pop("APP_ENV", None)
    os.environ.pop("DATABASE_URL", None)
    get_settings.cache_clear()
    return app_instance


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
