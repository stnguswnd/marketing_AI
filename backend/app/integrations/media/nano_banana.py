from uuid import uuid4


class NanoBananaAdapter:
    """Stub adapter for input-image based variant generation."""

    provider_name = "nano_banana"

    def create_variant(self, source_asset_ids: list[str]) -> dict[str, object]:
        variant_asset_ids = [f"variant_{uuid4().hex[:8]}" for _ in source_asset_ids]
        return {
            "provider": self.provider_name,
            "variant_asset_ids": variant_asset_ids,
        }


nano_banana_adapter = NanoBananaAdapter()
