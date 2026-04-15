from __future__ import annotations

from uuid import uuid4


def _merchant_headers(base_headers: dict[str, str], merchant_id: str) -> dict[str, str]:
    return {
        **base_headers,
        "X-Merchant-Id": merchant_id,
        "X-Test-Merchant-Id": merchant_id,
        "X-Actor-Id": f"user_{merchant_id}",
        "X-Test-User-Id": f"user_{merchant_id}",
    }

def test_admin_list_endpoints_and_publish_results(client, merchant_headers, admin_headers, uploaded_asset_factory):
    merchant_id = f"m_{uuid4().hex[:8]}"
    headers = _merchant_headers(merchant_headers, merchant_id)
    asset_id = uploaded_asset_factory(headers, merchant_id)

    asset_list = client.get("/api/v1/assets", headers=headers)
    assert asset_list.status_code == 200
    assert any(item["asset_id"] == asset_id for item in asset_list.json()["items"])

    content_response = client.post(
        "/api/v1/contents/generate",
        json={
            "merchant_id": merchant_id,
            "target_country": "JP",
            "platform": "blog",
            "goal": "store_visit",
            "input_brief": "벚꽃 시즌에 맞춰 말차라떼와 푸딩을 강조하고 싶어요.",
            "website_url": "https://example.com",
            "tone": "friendly",
            "must_include": ["말차라떼", "부산 여행"],
            "must_avoid": ["최고", "무조건"],
            "uploaded_asset_ids": [asset_id],
            "apply_image_variant": True,
            "image_variant_provider": "nano_banana",
            "publish_mode": "draft",
        },
        headers=headers,
    )
    content_id = content_response.json()["content_id"]

    content_list = client.get("/api/v1/contents", headers=headers)
    assert content_list.status_code == 200
    assert any(item["content_id"] == content_id for item in content_list.json()["items"])

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
    publish_result_id = publish_response.json()["publish_result_id"]
    variant_job_id = publish_response.json()["image_variant_job_id"]

    content_detail = client.get(f"/api/v1/contents/{content_id}", headers=headers)
    detail_payload = content_detail.json()
    assert detail_payload["latest_publish_result_id"] == publish_result_id
    assert publish_result_id in detail_payload["publish_result_ids"]
    assert detail_payload["image_variant_job_id"] == variant_job_id
    assert detail_payload["status"] == "published"
    assert detail_payload["variant_asset_ids"]

    publish_results = client.get("/api/v1/publish-results", headers=admin_headers)
    assert publish_results.status_code == 200
    assert any(item["publish_result_id"] == publish_result_id for item in publish_results.json()["items"])

    publish_result_detail = client.get(f"/api/v1/publish-results/{publish_result_id}", headers=admin_headers)
    assert publish_result_detail.status_code == 200
    assert publish_result_detail.json()["adapter_name"] == "blog_stub"
    assert publish_result_detail.json()["status"] == "published"
    assert publish_result_detail.json()["external_url"]

    variant_asset_id = detail_payload["variant_asset_ids"][0]
    variant_asset_detail = client.get(f"/api/v1/assets/{variant_asset_id}", headers=admin_headers)
    assert variant_asset_detail.status_code == 200
    assert variant_asset_detail.json()["asset_type"] == "variant"
    assert variant_asset_detail.json()["generated_by_job_id"] == variant_job_id
    assert variant_asset_detail.json()["provider"] == "nano_banana"

    job_list = client.get("/api/v1/jobs", headers=admin_headers)
    assert job_list.status_code == 200
    assert any(item["resource_id"] == content_id for item in job_list.json()["items"])


def test_review_report_and_job_lists(client, admin_headers, webhook_headers, merchant_headers):
    merchant_id = f"m_{uuid4().hex[:8]}"

    review_response = client.post(
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
    assert review_response.status_code == 202
    review_id = review_response.json()["review_id"]

    review_list = client.get("/api/v1/reviews", headers=admin_headers)
    assert review_list.status_code == 200
    assert any(item["review_id"] == review_id for item in review_list.json()["items"])

    report_response = client.post(
        "/api/v1/reports/monthly/generate",
        json={
            "scope_type": "merchant",
            "scope_id": merchant_id,
            "year": 2026,
            "month": 4,
        },
        headers=admin_headers,
    )
    assert report_response.status_code == 202
    report_id = report_response.json()["report_id"]

    report_list = client.get("/api/v1/reports", headers=admin_headers)
    assert report_list.status_code == 200
    assert any(item["report_id"] == report_id for item in report_list.json()["items"])

    job_list = client.get("/api/v1/jobs?resource_type=report", headers=admin_headers)
    assert job_list.status_code == 200
    assert any(item["resource_id"] == report_id for item in job_list.json()["items"])
