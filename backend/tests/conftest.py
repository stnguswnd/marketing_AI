import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def app():
    return create_app()


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
