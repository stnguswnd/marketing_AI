def test_review_webhook_and_reply(client, webhook_headers, admin_headers):
    webhook_payload = {
        "platform": "google_business",
        "external_review_id": "rv_123",
        "merchant_id": "m_123",
        "author_name": "guest",
        "rating": 2,
        "language": "ja",
        "review_text": "서비스가 아쉬웠어요.",
        "reviewed_at": "2026-04-15T12:00:00Z",
    }
    response = client.post("/api/v1/webhooks/reviews", json=webhook_payload, headers=webhook_headers)
    assert response.status_code == 202
    review_id = response.json()["review_id"]

    detail = client.get("/api/v1/reviews/%s" % review_id, headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["escalated"] is True
    assert detail.json()["reply_draft"]

    approve = client.post(
        "/api/v1/reviews/%s/approve-reply" % review_id,
        json={"approver_id": "admin_001", "reply_text": "죄송합니다. 확인하겠습니다."},
        headers=admin_headers,
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"


def test_monthly_report_and_job_lookup(client, admin_headers):
    response = client.post(
        "/api/v1/reports/monthly/generate",
        json={"scope_type": "merchant", "scope_id": "m_123", "year": 2026, "month": 4},
        headers=admin_headers,
    )
    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "succeeded"
    job_id = payload["job_id"]

    job = client.get("/api/v1/jobs/%s" % job_id, headers=admin_headers)
    assert job.status_code == 200
    assert job.json()["job_id"] == job_id
    assert job.json()["status"] == "succeeded"


def test_job_not_found(client, admin_headers):
    response = client.get("/api/v1/jobs/job_missing", headers=admin_headers)
    assert response.status_code == 404
    assert response.json()["error_code"] == "JOB_NOT_FOUND"
