def test_asset_upload_init_success(client, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    response = client.post(
        "/api/v1/assets/upload-init",
        json={
            "merchant_id": merchant_id,
            "filename": "menu-photo.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 204800,
        },
        headers=merchant_headers,
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["asset_id"].startswith("asset_")
    assert payload["asset_type"] == "source"
    assert payload["upload_url"]

    detail = client.get(f"/api/v1/assets/{payload['asset_id']}", headers=merchant_headers)
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert detail_payload["asset_id"] == payload["asset_id"]
    assert detail_payload["merchant_id"] == merchant_id
    assert detail_payload["asset_type"] == "source"
    assert detail_payload["status"] == "pending_upload"


def test_asset_binary_upload_success(client, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    created = client.post(
        "/api/v1/assets/upload-init",
        json={
            "merchant_id": merchant_id,
            "filename": "menu-photo.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 204800,
        },
        headers=merchant_headers,
    )
    asset_id = created.json()["asset_id"]

    upload = client.post(
        f"/api/v1/assets/{asset_id}/binary",
        files={"file": ("menu-photo.jpg", b"fake-jpeg-binary", "image/jpeg")},
        headers=merchant_headers,
    )
    assert upload.status_code == 200
    assert upload.json()["status"] == "uploaded"
    assert upload.json()["preview_url"]

    detail = client.get(f"/api/v1/assets/{asset_id}", headers=merchant_headers)
    assert detail.status_code == 200
    assert detail.json()["status"] == "uploaded"
    assert detail.json()["preview_url"]

    binary = client.get(f"/api/v1/assets/{asset_id}/binary", headers=merchant_headers)
    assert binary.status_code == 200
    assert binary.content == b"fake-jpeg-binary"


def test_asset_upload_init_rejects_unsupported_type(client, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    response = client.post(
        "/api/v1/assets/upload-init",
        json={
            "merchant_id": merchant_id,
            "filename": "menu.gif",
            "content_type": "image/gif",
            "size_bytes": 204800,
        },
        headers=merchant_headers,
    )

    assert response.status_code == 415
    assert response.json()["error_code"] == "UNSUPPORTED_ASSET_TYPE"


def test_asset_detail_forbidden_for_other_merchant(client, merchant_headers):
    merchant_id = merchant_headers["X-Test-Merchant-Id"]
    created = client.post(
        "/api/v1/assets/upload-init",
        json={
            "merchant_id": merchant_id,
            "filename": "menu-photo.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 204800,
        },
        headers=merchant_headers,
    )
    asset_id = created.json()["asset_id"]

    other_headers = {
        **merchant_headers,
        "X-Merchant-Id": "m_other",
        "X-Test-Merchant-Id": "m_other",
    }
    response = client.get(f"/api/v1/assets/{asset_id}", headers=other_headers)

    assert response.status_code == 403
    assert response.json()["error_code"] == "FORBIDDEN_ASSET_ACCESS"
