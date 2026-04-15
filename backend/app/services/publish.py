from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.core.auth import RequestContext
from app.core.errors import AppError
from app.core.permissions import ensure_merchant_scope
from app.domain.status_rules import ensure_content_transition
from app.integrations.social.blog import blog_publish_adapter
from app.integrations.media.nano_banana import nano_banana_adapter
from app.repositories.database import db_repository
from app.schemas.common import ContentStatus, ImageVariantProvider
from app.schemas.content import ContentPublishRequest, ContentPublishResponse
from app.services.audit import audit_service


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class PublishService:
    def _validate_asset_ownership(self, merchant_id: str, asset_ids: list[str]) -> None:
        for asset_id in asset_ids:
            asset = db_repository.get_asset(asset_id)
            if not asset or asset["merchant_id"] != merchant_id:
                raise AppError(
                    status_code=422,
                    error_code="INVALID_ASSET_REFERENCE",
                    message="유효하지 않은 asset 참조입니다.",
                )

    def publish_content(self, content_id: str, payload: ContentPublishRequest, context: RequestContext) -> ContentPublishResponse:
        content = db_repository.get_content(content_id)
        if not content:
            raise AppError(status_code=404, error_code="CONTENT_NOT_FOUND", message="콘텐츠를 찾을 수 없습니다.")
        if content["status"] == ContentStatus.DELETED:
            raise AppError(status_code=404, error_code="CONTENT_NOT_FOUND", message="콘텐츠를 찾을 수 없습니다.")
        ensure_merchant_scope(context, content["merchant_id"], error_code="FORBIDDEN_PUBLISH", message="게시 권한이 없습니다.")
        if content["status"] != ContentStatus.APPROVED:
            raise AppError(
                status_code=409,
                error_code="CONTENT_NOT_APPROVED",
                message="승인된 콘텐츠만 게시할 수 있습니다.",
            )
        ensure_content_transition(content["status"], ContentStatus.SCHEDULED, "게시 요청")

        publish_at = payload.publish_at or now_utc()
        immediate_publish = publish_at <= now_utc()
        publish_job_id = f"job_publish_{uuid4().hex[:8]}"
        publish_result_id = f"publish_{uuid4().hex[:8]}"
        source_asset_ids = payload.source_asset_ids or content["uploaded_asset_ids"]
        image_variant_job_id = None
        image_variant_provider = None
        external_post = {
            "adapter_name": "internal_stub",
            "external_post_id": None,
            "external_url": None,
            "status": "published" if immediate_publish else "queued",
        }

        if payload.apply_image_variant:
            if not source_asset_ids:
                raise AppError(
                    status_code=422,
                    error_code="INVALID_SOURCE_ASSET_REFERENCE",
                    message="이미지 변형을 위한 source asset이 없습니다.",
                )
            self._validate_asset_ownership(content["merchant_id"], source_asset_ids)
            if payload.image_variant_provider == ImageVariantProvider.NANO_BANANA:
                image_variant_job_id = f"job_image_{uuid4().hex[:8]}"
                variant_result = nano_banana_adapter.create_variant(source_asset_ids)
                created_at = now_utc()
                for variant_asset_id in variant_result["variant_asset_ids"]:
                    db_repository.create_asset({
                        "asset_id": variant_asset_id,
                        "merchant_id": content["merchant_id"],
                        "filename": f"{variant_asset_id}.jpg",
                        "content_type": "image/jpeg",
                        "size_bytes": 0,
                        "asset_type": "variant",
                        "status": "generated",
                        "provider": variant_result["provider"],
                        "generated_by_job_id": image_variant_job_id,
                        "source_asset_ids": source_asset_ids,
                        "preview_url": None,
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
                content["variant_asset_ids"] = variant_result["variant_asset_ids"]
                image_variant_provider = ImageVariantProvider.NANO_BANANA

        if content["platform"] == "blog":
            external_post = blog_publish_adapter.publish_post(
                content_id=content_id,
                title=content["title"],
                body=content["body"],
                hashtags=content["hashtags"],
            )

        updated_at = now_utc()
        next_content_status = ContentStatus.PUBLISHED if immediate_publish else ContentStatus.SCHEDULED
        publish_job_status = "succeeded" if immediate_publish else "queued"
        db_repository.update_content(
            content_id,
            status=next_content_status,
            updated_at=updated_at,
            publish_job_id=publish_job_id,
            image_variant_job_id=image_variant_job_id,
            latest_publish_result_id=publish_result_id,
            publish_result_ids=[*content.get("publish_result_ids", []), publish_result_id],
            variant_asset_ids=content.get("variant_asset_ids", []),
        )
        db_repository.create_job({
            "job_id": publish_job_id,
            "job_type": "content_publish",
            "status": publish_job_status,
            "resource_type": "content",
            "resource_id": content_id,
            "created_at": updated_at,
            "updated_at": updated_at,
        })
        db_repository.create_publish_result({
            "publish_result_id": publish_result_id,
            "content_id": content_id,
            "channel": content["platform"],
            "adapter_name": external_post["adapter_name"],
            "status": external_post["status"],
            "external_post_id": external_post["external_post_id"],
            "external_url": external_post["external_url"],
            "publish_at": publish_at,
            "source_asset_ids": source_asset_ids,
            "variant_asset_ids": content.get("variant_asset_ids", []),
            "image_variant_provider": image_variant_provider,
            "thumbnail_url": None,
            "title": content["title"],
            "caption_preview": content["body"][:140],
            "created_at": updated_at,
            "updated_at": updated_at,
        })
        audit_service.record(
            action="content.publish_request",
            resource_type="content",
            resource_id=content_id,
            context=context,
            merchant_id=content["merchant_id"],
            metadata={
                "publish_result_id": publish_result_id,
                "channel": str(content["platform"]),
                "adapter_name": external_post["adapter_name"],
                "image_variant_job_id": image_variant_job_id or "",
            },
        )
        return ContentPublishResponse(
            content_id=content_id,
            status=next_content_status,
            job_id=publish_job_id,
            publish_at=publish_at,
            image_variant_job_id=image_variant_job_id,
            image_variant_provider=image_variant_provider,
            publish_result_id=publish_result_id,
        )


publish_service = PublishService()
