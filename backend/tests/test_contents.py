def _generate_payload(asset_id: str):
    return {
        "merchant_id": "m_123",
        "target_country": "JP",
        "platform": "instagram",
        "goal": "store_visit",
        "input_brief": "벚꽃 시즌에 맞춰 말차라떼와 푸딩을 강조하고 싶어요.",
        "website_url": "https://example.com",
        "tone": "friendly",
        "must_include": ["말차라떼", "부산 여행"],
        "must_avoid": ["최고", "무조건"],
        "uploaded_asset_ids": [asset_id],
        "publish_mode": "draft",
    }

def test_generate_content_success(client, merchant_headers, uploaded_asset_factory):
    asset_id = uploaded_asset_factory(merchant_headers, "m_123")
    response = client.post("/api/v1/contents/generate", json=_generate_payload(asset_id), headers=merchant_headers)
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "draft"
    assert payload["approval_required"] is True
    assert payload["job_id"].startswith("job_")


def test_generate_content_validation_error(client, merchant_headers, uploaded_asset_factory):
    asset_id = uploaded_asset_factory(merchant_headers, "m_123")
    payload = _generate_payload(asset_id)
    del payload["platform"]
    response = client.post("/api/v1/contents/generate", json=payload, headers=merchant_headers)
    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert "platform" in body["field_errors"]


def test_generate_content_invalid_combination(client, merchant_headers, uploaded_asset_factory):
    asset_id = uploaded_asset_factory(merchant_headers, "m_123")
    payload = _generate_payload(asset_id)
    payload["platform"] = "xiaohongshu"
    response = client.post("/api/v1/contents/generate", json=payload, headers=merchant_headers)
    assert response.status_code == 409
    body = response.json()
    assert body["error_code"] == "INVALID_PLATFORM_COMBINATION"


def test_content_approval_and_publish_flow(client, merchant_headers, uploaded_asset_factory):
    asset_id = uploaded_asset_factory(merchant_headers, "m_123")
    generate = client.post("/api/v1/contents/generate", json=_generate_payload(asset_id), headers=merchant_headers)
    content_id = generate.json()["content_id"]

    approve = client.post(
        f"/api/v1/contents/{content_id}/approve",
        json={"approver_id": "merchant_owner", "comment": "ok"},
        headers=merchant_headers,
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    publish = client.post(
        f"/api/v1/contents/{content_id}/publish",
        json={"apply_image_variant": True, "image_variant_provider": "nano_banana"},
        headers=merchant_headers,
    )
    assert publish.status_code == 202
    assert publish.json()["status"] == "published"
    assert publish.json()["image_variant_provider"] == "nano_banana"
    assert publish.json()["image_variant_job_id"].startswith("job_image_")


def test_content_reject_flow(client, merchant_headers, uploaded_asset_factory):
    asset_id = uploaded_asset_factory(merchant_headers, "m_123")
    generate = client.post("/api/v1/contents/generate", json=_generate_payload(asset_id), headers=merchant_headers)
    content_id = generate.json()["content_id"]
    reject = client.post(
        f"/api/v1/contents/{content_id}/reject",
        json={"reviewer_id": "merchant_owner", "reason": "needs adjustment"},
        headers=merchant_headers,
    )
    assert reject.status_code == 200
    assert reject.json()["status"] == "rejected"


def test_content_delete_draft_flow(client, merchant_headers, uploaded_asset_factory):
    asset_id = uploaded_asset_factory(merchant_headers, "m_123")
    generate = client.post("/api/v1/contents/generate", json=_generate_payload(asset_id), headers=merchant_headers)
    content_id = generate.json()["content_id"]

    delete_response = client.delete(f"/api/v1/contents/{content_id}", headers=merchant_headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True

    detail_response = client.get(f"/api/v1/contents/{content_id}", headers=merchant_headers)
    assert detail_response.status_code == 404

    list_response = client.get("/api/v1/contents", headers=merchant_headers)
    assert all(item["content_id"] != content_id for item in list_response.json()["items"])


def test_content_delete_after_approval_returns_invalid_transition(client, merchant_headers, uploaded_asset_factory):
    asset_id = uploaded_asset_factory(merchant_headers, "m_123")
    generate = client.post("/api/v1/contents/generate", json=_generate_payload(asset_id), headers=merchant_headers)
    content_id = generate.json()["content_id"]

    approve = client.post(
        f"/api/v1/contents/{content_id}/approve",
        json={"approver_id": "merchant_owner", "comment": "ok"},
        headers=merchant_headers,
    )
    assert approve.status_code == 200

    delete_response = client.delete(f"/api/v1/contents/{content_id}", headers=merchant_headers)
    assert delete_response.status_code == 409
    assert delete_response.json()["error_code"] == "INVALID_CONTENT_STATUS_TRANSITION"


def test_content_reject_after_approval_returns_invalid_transition(client, merchant_headers, uploaded_asset_factory):
    asset_id = uploaded_asset_factory(merchant_headers, "m_123")
    generate = client.post("/api/v1/contents/generate", json=_generate_payload(asset_id), headers=merchant_headers)
    content_id = generate.json()["content_id"]

    approve = client.post(
        f"/api/v1/contents/{content_id}/approve",
        json={"approver_id": "merchant_owner", "comment": "ok"},
        headers=merchant_headers,
    )
    assert approve.status_code == 200

    reject = client.post(
        f"/api/v1/contents/{content_id}/reject",
        json={"reviewer_id": "merchant_owner", "reason": "too late"},
        headers=merchant_headers,
    )
    assert reject.status_code == 409
    assert reject.json()["error_code"] == "INVALID_CONTENT_STATUS_TRANSITION"
