import os

from app.core.settings import get_settings
from app.integrations.media.nano_banana import nano_banana_adapter


def test_nano_banana_adapter_builds_mock_variant_response():
    previous_app_env = os.environ.get("APP_ENV")
    os.environ["APP_ENV"] = "test"
    get_settings.cache_clear()
    try:
        response = nano_banana_adapter.create_variant(
            api_key="nb_test_secret",
            source_asset_ids=["asset_001"],
            card_request={
                "variant_count": 3,
                "output_format": "jpeg",
                "prompt": "make instagram card",
                "negative_prompt": "avoid distortion",
                "card_spec": {"aspect_ratio": "4:5"},
                "source_assets": [{"asset_id": "asset_001"}],
            },
        )
    finally:
        if previous_app_env is None:
            os.environ.pop("APP_ENV", None)
        else:
            os.environ["APP_ENV"] = previous_app_env
        get_settings.cache_clear()

    assert response["provider"] == "nano_banana"
    assert len(response["variant_asset_ids"]) == 3
    assert response["api_key_present"] is True
    assert response["raw_response"]["status"] == "mocked"
