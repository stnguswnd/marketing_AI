def test_merchant_can_save_and_read_masked_nano_banana_key(client, merchant_headers):
    response = client.put(
        "/api/v1/merchant-settings/nano-banana",
        json={
            "merchant_id": merchant_headers["X-Test-Merchant-Id"],
            "api_key": "nb_test_secret_1234",
        },
        headers=merchant_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["merchant_id"] == merchant_headers["X-Test-Merchant-Id"]
    assert payload["has_api_key"] is True
    assert payload["masked_api_key"].endswith("1234")
    assert "*" in payload["masked_api_key"]

    fetch_response = client.get(
        f"/api/v1/merchant-settings/nano-banana?merchant_id={merchant_headers['X-Test-Merchant-Id']}",
        headers=merchant_headers,
    )

    assert fetch_response.status_code == 200
    fetched = fetch_response.json()
    assert fetched["has_api_key"] is True
    assert fetched["masked_api_key"] == payload["masked_api_key"]


def test_merchant_cannot_read_other_merchant_setting(client, merchant_headers):
    response = client.get(
        "/api/v1/merchant-settings/nano-banana?merchant_id=m_other",
        headers=merchant_headers,
    )

    assert response.status_code == 403
