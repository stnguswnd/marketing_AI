from __future__ import annotations


def test_request_id_header_and_observability_logs(client, admin_headers):
    response = client.get("/api/v1/health", headers=admin_headers)

    assert response.status_code == 200
    assert response.headers["X-Request-Id"].startswith("req_")

    request_logs = client.get("/api/v1/observability/requests", headers=admin_headers)
    assert request_logs.status_code == 200
    assert any(item["path"] == "/api/v1/health" for item in request_logs.json()["items"])

    summary = client.get("/api/v1/observability/summary", headers=admin_headers)
    assert summary.status_code == 200
    assert summary.json()["total_requests"] >= 1
    assert "/api/v1/health" in summary.json()["path_counts"]


def test_audit_logs_capture_sensitive_actions(client, merchant_headers, admin_headers, uploaded_asset_factory):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    asset_id = uploaded_asset_factory(merchant_headers, merchant_id)

    generate_response = client.post(
        "/api/v1/contents/generate",
        json={
            "merchant_id": merchant_id,
            "target_country": "JP",
            "platform": "blog",
            "goal": "store_visit",
            "input_brief": "벚꽃 시즌에 맞춰 말차라떼와 푸딩을 강조하고 싶어요.",
            "website_url": "https://example.com",
            "tone": "friendly",
            "must_include": ["말차라떼"],
            "must_avoid": ["최고"],
            "uploaded_asset_ids": [asset_id],
            "publish_mode": "draft",
        },
        headers=merchant_headers,
    )
    content_id = generate_response.json()["content_id"]

    approve_response = client.post(
        f"/api/v1/contents/{content_id}/approve",
        json={"approver_id": "admin_001", "comment": "ok"},
        headers=admin_headers,
    )
    assert approve_response.status_code == 200

    publish_response = client.post(
        f"/api/v1/contents/{content_id}/publish",
        json={
            "apply_image_variant": True,
            "image_variant_provider": "nano_banana",
            "source_asset_ids": [asset_id],
        },
        headers=admin_headers,
    )
    assert publish_response.status_code == 202

    audit_logs = client.get("/api/v1/audit-logs", headers=admin_headers)
    assert audit_logs.status_code == 200
    actions = {item["action"] for item in audit_logs.json()["items"]}
    assert "asset.upload_init" in actions
    assert "content.generate" in actions
    assert "content.approve" in actions
    assert "content.publish_request" in actions


def test_audit_and_observability_require_privileged_role(client, merchant_headers):
    audit_response = client.get("/api/v1/audit-logs", headers=merchant_headers)
    assert audit_response.status_code == 403
    assert audit_response.json()["error_code"] == "FORBIDDEN_AUDIT_ACCESS"

    observability_response = client.get("/api/v1/observability/summary", headers=merchant_headers)
    assert observability_response.status_code == 403
    assert observability_response.json()["error_code"] == "FORBIDDEN_OBSERVABILITY_ACCESS"
