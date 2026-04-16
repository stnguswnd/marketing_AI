from __future__ import annotations

from datetime import datetime, timezone
import base64
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.core.auth import RequestContext
from app.core.errors import AppError
from app.core.settings import get_settings
from app.integrations.media.nano_banana import nano_banana_adapter
from app.repositories.database import db_repository
from app.schemas.common import ImageVariantProvider
from app.services.audit import audit_service
from app.services.image_card import image_card_service
from app.services.merchant_setting import merchant_setting_service


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class ImageVariantService:
    def _load_source_assets(self, merchant_id: str, asset_ids: list[str]) -> list[dict[str, Any]]:
        source_assets: list[dict[str, Any]] = []
        for asset_id in asset_ids:
            asset = db_repository.get_asset(asset_id)
            if not asset or asset["merchant_id"] != merchant_id:
                raise AppError(
                    status_code=422,
                    error_code="INVALID_ASSET_REFERENCE",
                    message="유효하지 않은 asset 참조입니다.",
                )
            source_assets.append(asset)
        return source_assets

    def _generated_asset_file_path(self, asset_id: str, filename: str) -> Path:
        storage_dir = Path(get_settings().asset_storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(filename).suffix or ".bin"
        return storage_dir / f"{asset_id}{suffix.lower()}"

    def _source_asset_file_path(self, asset: dict[str, Any]) -> Path:
        storage_dir = Path(get_settings().asset_storage_dir)
        suffix = Path(str(asset["filename"])).suffix or ".bin"
        return storage_dir / f"{asset['asset_id']}{suffix.lower()}"

    def _encode_source_images(self, source_assets: list[dict[str, Any]]) -> list[dict[str, str]]:
        encoded_images: list[dict[str, str]] = []
        for asset in source_assets:
            file_path = self._source_asset_file_path(asset)
            if not file_path.exists():
                continue
            encoded_images.append(
                {
                    "mime_type": str(asset.get("content_type") or "image/png"),
                    "data": base64.b64encode(file_path.read_bytes()).decode("ascii"),
                }
            )
        return encoded_images

    def _store_generated_asset_binary(
        self,
        *,
        asset_id: str,
        filename: str,
        binary_bytes: bytes,
    ) -> tuple[int, str]:
        file_path = self._generated_asset_file_path(asset_id, filename)
        file_path.write_bytes(binary_bytes)
        preview_url = f"{get_settings().public_api_base_url}/assets/{asset_id}/binary"
        return len(binary_bytes), preview_url

    def create_variants_for_content(
        self,
        *,
        content_id: str,
        content: dict[str, Any],
        source_asset_ids: list[str],
        immediate_publish: bool,
        context: RequestContext,
    ) -> tuple[str, ImageVariantProvider, list[str]]:
        source_assets = self._load_source_assets(content["merchant_id"], source_asset_ids)
        api_key = merchant_setting_service.get_nano_banana_api_key(content["merchant_id"])
        if not api_key:
            raise AppError(
                status_code=409,
                error_code="NANO_BANANA_API_KEY_MISSING",
                message="Nano Banana API key가 설정되지 않았습니다.",
            )

        image_variant_job_id = f"job_image_{uuid4().hex[:8]}"
        card_request = image_card_service.build_nano_banana_request(content=content, source_assets=source_assets)
        source_images = self._encode_source_images(source_assets)
        variant_result = nano_banana_adapter.create_variant(
            api_key=api_key,
            source_asset_ids=source_asset_ids,
            source_images=source_images,
            card_request=card_request,
        )
        created_at = now_utc()
        outputs = list(variant_result.get("outputs", []))
        variant_asset_ids = list(variant_result["variant_asset_ids"])

        for index, output in enumerate(outputs, start=1):
            variant_asset_id = str(output["asset_id"])
            filename = str(output.get("filename") or f"{content_id}_instagram_card_{index}.png")
            content_type = str(output.get("content_type") or "image/png")
            binary_bytes = output.get("binary_bytes")
            if not isinstance(binary_bytes, bytes) or len(binary_bytes) == 0:
                raise AppError(
                    status_code=502,
                    error_code="NANO_BANANA_EMPTY_IMAGE",
                    message="Nano Banana API returned an empty generated image.",
                )
            size_bytes, preview_url = self._store_generated_asset_binary(
                asset_id=variant_asset_id,
                filename=filename,
                binary_bytes=binary_bytes,
            )
            db_repository.create_asset({
                "asset_id": variant_asset_id,
                "merchant_id": content["merchant_id"],
                "filename": filename,
                "content_type": content_type,
                "size_bytes": size_bytes,
                "asset_type": "variant",
                "status": "generated",
                "provider": variant_result["provider"],
                "generated_by_job_id": image_variant_job_id,
                "source_asset_ids": source_asset_ids,
                "preview_url": preview_url,
                "created_at": created_at,
                "updated_at": created_at,
            })

        db_repository.create_job({
            "job_id": image_variant_job_id,
            "job_type": "image_variant_generate",
            "status": "succeeded" if immediate_publish else "queued",
            "resource_type": "content",
            "resource_id": content_id,
            "created_at": created_at,
            "updated_at": created_at,
        })
        audit_service.record(
            action="content.image_variant_plan",
            resource_type="content",
            resource_id=content_id,
            context=context,
            merchant_id=content["merchant_id"],
            metadata={
                "provider": variant_result["provider"],
                "variant_count": len(variant_asset_ids),
                "source_asset_ids": source_asset_ids,
                "card_spec": card_request["card_spec"],
            },
        )
        return image_variant_job_id, ImageVariantProvider.NANO_BANANA, variant_asset_ids


image_variant_service = ImageVariantService()
