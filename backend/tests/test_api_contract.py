from __future__ import annotations

from uuid import uuid4

import pytest


def _unique_merchant_id() -> str:
    return f"m_{uuid4().hex[:8]}"


def _content_payload(merchant_id: str, **overrides):
    payload = {
        "merchant_id": merchant_id,
        "target_country": "JP",
        "platform": "instagram",
        "goal": "store_visit",
        "input_brief": "벚꽃 시즌에 맞춰 말차라떼와 푸딩을 강조하고 싶어요.",
        "website_url": "https://example.com",
        "tone": "friendly",
        "must_include": ["말차라떼", "부산 여행"],
        "must_avoid": ["최고", "무조건"],
        "uploaded_asset_ids": ["asset_1", "asset_2"],
        "publish_mode": "draft",
    }
    payload.update(overrides)
    return payload


def test_health_check_returns_ok(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_content_generate_success_creates_draft(client, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    asset_response = client.post(
        "/api/v1/assets/upload-init",
        json={
            "merchant_id": merchant_id,
            "filename": "menu-photo.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 204800,
        },
        headers=merchant_headers,
    )
    asset_id = asset_response.json()["asset_id"]
    response = client.post(
        "/api/v1/contents/generate",
        json=_content_payload(merchant_id, uploaded_asset_ids=[asset_id]),
        headers=merchant_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["merchant_id"] == merchant_id
    assert data["status"] == "draft"
    assert data["approval_required"] is True
    assert data["content_id"]
    assert data["job_id"]


def test_content_generate_rejects_invalid_platform_combination(client, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    response = client.post(
        "/api/v1/contents/generate",
        json=_content_payload(merchant_id, target_country="JP", platform="xiaohongshu"),
        headers=merchant_headers,
    )

    assert response.status_code == 409
    body = response.json()
    assert body["error_code"] == "INVALID_PLATFORM_COMBINATION"


def test_content_generate_rejects_missing_required_field(client, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    payload = _content_payload(merchant_id)
    payload.pop("input_brief")

    response = client.post(
        "/api/v1/contents/generate",
        json=payload,
        headers=merchant_headers,
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert "input_brief" in body["field_errors"]


def test_content_detail_approve_and_publish_flow(client, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    asset_response = client.post(
        "/api/v1/assets/upload-init",
        json={
            "merchant_id": merchant_id,
            "filename": "menu-photo.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 204800,
        },
        headers=merchant_headers,
    )
    asset_id = asset_response.json()["asset_id"]
    create_response = client.post(
        "/api/v1/contents/generate",
        json=_content_payload(
            merchant_id,
            uploaded_asset_ids=[asset_id],
            apply_image_variant=True,
            image_variant_provider="nano_banana",
        ),
        headers=merchant_headers,
    )
    content_id = create_response.json()["content_id"]

    detail_response = client.get(
        f"/api/v1/contents/{content_id}",
        headers=merchant_headers,
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["content_id"] == content_id

    publish_before_approval = client.post(
        f"/api/v1/contents/{content_id}/publish",
        json={"publish_at": "2026-04-16T09:00:00Z"},
        headers=merchant_headers,
    )
    assert publish_before_approval.status_code == 409
    assert publish_before_approval.json()["error_code"] == "CONTENT_NOT_APPROVED"

    approve_response = client.post(
        f"/api/v1/contents/{content_id}/approve",
        json={"approver_id": merchant_headers["X-Test-User-Id"], "comment": "문구 확인 완료"},
        headers=merchant_headers,
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    publish_response = client.post(
        f"/api/v1/contents/{content_id}/publish",
        json={
            "publish_at": "2026-04-16T09:00:00Z",
            "apply_image_variant": True,
            "image_variant_provider": "nano_banana",
            "source_asset_ids": [asset_id],
        },
        headers=merchant_headers,
    )
    assert publish_response.status_code == 202
    assert publish_response.json()["status"] == "scheduled"
    assert publish_response.json()["image_variant_provider"] == "nano_banana"
    assert publish_response.json()["image_variant_job_id"]


def test_content_reject_allows_merchant_on_own_content(client, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    asset_response = client.post(
        "/api/v1/assets/upload-init",
        json={
            "merchant_id": merchant_id,
            "filename": "menu-photo.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 204800,
        },
        headers=merchant_headers,
    )
    asset_id = asset_response.json()["asset_id"]
    create_response = client.post(
        "/api/v1/contents/generate",
        json=_content_payload(merchant_id, uploaded_asset_ids=[asset_id]),
        headers=merchant_headers,
    )
    content_id = create_response.json()["content_id"]

    reject_response = client.post(
        f"/api/v1/contents/{content_id}/reject",
        json={"reviewer_id": merchant_headers["X-Test-User-Id"], "reason": "검토 필요"},
        headers=merchant_headers,
    )

    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"


def test_content_generate_rejects_image_variant_without_assets(client, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    response = client.post(
        "/api/v1/contents/generate",
        json=_content_payload(
            merchant_id,
            apply_image_variant=True,
            image_variant_provider="nano_banana",
            uploaded_asset_ids=[],
        ),
        headers=merchant_headers,
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "MISSING_SOURCE_ASSET"


def test_webhook_review_flow_and_reply_approval(client, webhook_headers, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    webhook_response = client.post(
        "/api/v1/webhooks/reviews",
        json={
            "platform": "google_business",
            "external_review_id": f"rv_{uuid4().hex[:8]}",
            "merchant_id": merchant_id,
            "author_name": "guest",
            "rating": 2,
            "language": "ja",
            "review_text": "서비스가 아쉬웠어요.",
            "reviewed_at": "2026-04-15T12:00:00Z",
        },
        headers=webhook_headers,
    )

    assert webhook_response.status_code == 202
    webhook_body = webhook_response.json()
    review_id = webhook_body["review_id"]
    assert webhook_body["status"] == "queued"
    assert webhook_body["job_id"]

    detail_response = client.get(
        f"/api/v1/reviews/{review_id}",
        headers=merchant_headers,
    )
    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["review_id"] == review_id
    assert detail_body["sensitivity"] in {"low", "medium", "high"}

    approve_response = client.post(
        f"/api/v1/reviews/{review_id}/approve-reply",
        json={
            "approver_id": merchant_headers["X-Test-User-Id"],
            "reply_text": "불편을 드려 죄송합니다. 말씀 주신 내용을 확인해 개선하겠습니다.",
        },
        headers=merchant_headers,
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    approve_again_response = client.post(
        f"/api/v1/reviews/{review_id}/approve-reply",
        json={
            "approver_id": merchant_headers["X-Test-User-Id"],
            "reply_text": "다시 승인",
        },
        headers=merchant_headers,
    )
    assert approve_again_response.status_code == 409
    assert approve_again_response.json()["error_code"] == "INVALID_REVIEW_STATUS_TRANSITION"


def test_webhook_review_requires_secret(client):
    response = client.post(
        "/api/v1/webhooks/reviews",
        json={
            "platform": "google_business",
            "external_review_id": f"rv_{uuid4().hex[:8]}",
            "merchant_id": _unique_merchant_id(),
            "author_name": "guest",
            "rating": 4,
            "language": "ja",
            "review_text": "좋았어요.",
            "reviewed_at": "2026-04-15T12:00:00Z",
        },
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_WEBHOOK_SIGNATURE"


def test_monthly_report_generate_and_job_lookup(client, admin_headers):
    response = client.post(
        "/api/v1/reports/monthly/generate",
        json={
            "scope_type": "merchant",
            "scope_id": _unique_merchant_id(),
            "year": 2026,
            "month": 4,
        },
        headers=admin_headers,
    )

    assert response.status_code == 202
    body = response.json()
    assert body["report_id"]
    assert body["job_id"]
    assert body["status"] == "queued"

    job_response = client.get(f"/api/v1/jobs/{body['job_id']}", headers=admin_headers)
    assert job_response.status_code == 200
    job_body = job_response.json()
    assert job_body["job_id"] == body["job_id"]
    assert job_body["status"] in {"queued", "running", "succeeded", "failed"}


def test_job_lookup_missing_job_returns_not_found(client, admin_headers):
    response = client.get("/api/v1/jobs/job_missing", headers=admin_headers)

    assert response.status_code == 404
    assert response.json()["error_code"] == "JOB_NOT_FOUND"


def test_merchant_can_access_own_review_endpoint(client, merchant_headers, webhook_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    review_response = client.post(
        "/api/v1/webhooks/reviews",
        json={
            "platform": "google_business",
            "external_review_id": f"rv_{uuid4().hex[:8]}",
            "merchant_id": merchant_id,
            "author_name": "guest",
            "rating": 5,
            "language": "ja",
            "review_text": "좋았습니다.",
            "reviewed_at": "2026-04-15T12:00:00Z",
        },
        headers=webhook_headers,
    )
    review_id = review_response.json()["review_id"]

    response = client.get(f"/api/v1/reviews/{review_id}", headers=merchant_headers)

    assert response.status_code == 200
    assert response.json()["review_id"] == review_id


def test_admin_can_list_merchant_summaries(client, admin_headers, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    asset_response = client.post(
        "/api/v1/assets/upload-init",
        json={
            "merchant_id": merchant_id,
            "filename": "menu-photo.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 204800,
        },
        headers=merchant_headers,
    )
    asset_id = asset_response.json()["asset_id"]
    client.post(
        "/api/v1/contents/generate",
        json=_content_payload(merchant_id, uploaded_asset_ids=[asset_id]),
        headers=merchant_headers,
    )

    response = client.get("/api/v1/admin/merchants", headers=admin_headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert any(item["merchant_id"] == merchant_id for item in items)
