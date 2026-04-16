from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.core.auth import RequestContext
from app.core.errors import AppError
from app.core.permissions import ensure_authenticated_actor, ensure_merchant_scope, ensure_roles
from app.domain.status_rules import ensure_content_transition
from app.graphs.content import run_content_graph
from app.repositories.database import db_repository
from app.schemas.common import ContentStatus, CountryCode, PlatformType
from app.schemas.content import (
    ContentApproveRequest,
    ContentDeleteResponse,
    ContentDetailResponse,
    ContentGenerateRequest,
    ContentGenerateResponse,
    ContentImageRegenerateRequest,
    ContentListItemResponse,
    ContentListResponse,
    ContentOverlayResponse,
    ContentOverlayUpdateRequest,
    ContentPublishRequest,
    ContentPublishResponse,
    ContentRejectRequest,
    ContentStatusChangeResponse,
)
from app.services.audit import audit_service
from app.services.image_variant import image_variant_service
from app.services.publish import publish_service


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class ContentService:
    def _ensure_not_deleted(self, content: dict) -> None:
        if content["status"] == ContentStatus.DELETED:
            raise AppError(status_code=404, error_code="CONTENT_NOT_FOUND", message="콘텐츠를 찾을 수 없습니다.")

    def _validate_asset_ownership(self, merchant_id: str, asset_ids: list[str]) -> None:
        for asset_id in asset_ids:
            asset = db_repository.get_asset(asset_id)
            if not asset or asset["merchant_id"] != merchant_id:
                raise AppError(
                    status_code=422,
                    error_code="INVALID_ASSET_REFERENCE",
                    message="유효하지 않은 asset 참조입니다.",
                )
            if asset["status"] != "uploaded":
                raise AppError(
                    status_code=422,
                    error_code="ASSET_NOT_UPLOADED",
                    message="업로드가 완료된 asset만 사용할 수 있습니다.",
                )

    def generate(self, payload: ContentGenerateRequest, context: RequestContext) -> ContentGenerateResponse:
        ensure_roles(context, "merchant", "operator", "admin")
        ensure_authenticated_actor(context)
        ensure_merchant_scope(context, payload.merchant_id)

        if payload.target_country == CountryCode.JP and payload.platform == PlatformType.XIAOHONGSHU:
            raise AppError(
                status_code=409,
                error_code="INVALID_PLATFORM_COMBINATION",
                message="선택한 국가와 플랫폼 조합은 현재 지원하지 않습니다.",
            )

        self._validate_asset_ownership(payload.merchant_id, payload.uploaded_asset_ids)
        if payload.apply_image_variant and not payload.uploaded_asset_ids:
            raise AppError(
                status_code=400,
                error_code="MISSING_SOURCE_ASSET",
                message="이미지 변형을 사용하려면 먼저 이미지를 업로드해 주세요.",
            )

        created_at = now_utc()
        content_id = f"content_{uuid4().hex[:8]}"
        job_id = f"job_{uuid4().hex[:8]}"
        graph_result = run_content_graph(
            {
                "merchant_id": payload.merchant_id,
                "target_country": payload.target_country,
                "platform": payload.platform,
                "goal": payload.goal,
                "input_brief": payload.input_brief,
                "tone": payload.tone.value if payload.tone else None,
                "must_include": payload.must_include,
                "must_avoid": payload.must_avoid,
                "uploaded_asset_ids": payload.uploaded_asset_ids,
                "status": ContentStatus.DRAFT,
            }
        )
        title = graph_result["title"]
        body = graph_result["body"]
        hashtags = graph_result["hashtags"]
        variant_asset_ids: list[str] = []
        image_variant_job_id: str | None = None
        overlay_headline = title[:48]
        overlay_subheadline = body[:120]
        overlay_cta = "지금 확인하기"

        db_repository.create_content({
            "content_id": content_id,
            "merchant_id": payload.merchant_id,
            "target_country": payload.target_country,
            "platform": payload.platform,
            "goal": payload.goal,
            "status": ContentStatus.DRAFT,
            "title": title,
            "body": body,
            "hashtags": hashtags,
            "must_include": payload.must_include,
            "must_avoid": payload.must_avoid,
            "uploaded_asset_ids": payload.uploaded_asset_ids,
            "apply_image_variant": payload.apply_image_variant,
            "image_variant_provider": payload.image_variant_provider,
            "image_variant_job_id": None,
            "selected_variant_asset_id": None,
            "overlay_headline": overlay_headline,
            "overlay_subheadline": overlay_subheadline,
            "overlay_cta": overlay_cta,
            "publish_job_id": None,
            "latest_publish_result_id": None,
            "publish_result_ids": [],
            "variant_asset_ids": [],
            "approval_required": True,
            "created_at": created_at,
            "updated_at": created_at,
        })

        content_record = db_repository.get_content(content_id)
        if payload.apply_image_variant and payload.image_variant_provider.value == "nano_banana" and content_record:
            image_variant_job_id, _, variant_asset_ids = image_variant_service.create_variants_for_content(
                content_id=content_id,
                content=content_record,
                source_asset_ids=payload.uploaded_asset_ids,
                immediate_publish=False,
                context=context,
            )
            db_repository.update_content(
                content_id,
                image_variant_job_id=image_variant_job_id,
                selected_variant_asset_id=variant_asset_ids[0] if variant_asset_ids else None,
                variant_asset_ids=variant_asset_ids,
                updated_at=now_utc(),
            )

        db_repository.create_job({
            "job_id": job_id,
            "job_type": "content_generate",
            "status": "succeeded",
            "resource_type": "content",
            "resource_id": content_id,
            "created_at": created_at,
            "updated_at": created_at,
        })
        audit_service.record(
            action="content.generate",
            resource_type="content",
            resource_id=content_id,
            context=context,
            merchant_id=payload.merchant_id,
            metadata={
                "platform": payload.platform.value,
                "goal": payload.goal.value,
                "image_variant_job_id": image_variant_job_id or "",
                "variant_asset_count": len(variant_asset_ids),
            },
        )

        return ContentGenerateResponse(
            content_id=content_id,
            merchant_id=payload.merchant_id,
            status=ContentStatus.DRAFT,
            approval_required=True,
            job_id=job_id,
            message="콘텐츠 초안을 생성했습니다.",
            image_variant_job_id=image_variant_job_id,
            variant_asset_ids=variant_asset_ids,
        )

    def get(self, content_id: str, context: RequestContext) -> ContentDetailResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_CONTENT_ACCESS", message="콘텐츠 접근 권한이 없습니다.")
        content = db_repository.get_content(content_id)
        if not content:
            raise AppError(status_code=404, error_code="CONTENT_NOT_FOUND", message="콘텐츠를 찾을 수 없습니다.")
        self._ensure_not_deleted(content)
        ensure_merchant_scope(context, content["merchant_id"], error_code="FORBIDDEN_CONTENT_ACCESS", message="콘텐츠 접근 권한이 없습니다.")
        return ContentDetailResponse(**content)

    def list(
        self,
        context: RequestContext,
        merchant_id: str | None = None,
        status: str | None = None,
        platform: str | None = None,
    ) -> ContentListResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_CONTENT_ACCESS", message="콘텐츠 접근 권한이 없습니다.")
        if context.role == "merchant":
            merchant_id = context.merchant_id

        items = []
        for content in db_repository.list_contents():
            if content["status"] == ContentStatus.DELETED:
                continue
            if merchant_id and content["merchant_id"] != merchant_id:
                continue
            if status and content["status"] != status:
                continue
            if platform and str(content["platform"]) != platform:
                continue
            items.append(ContentListItemResponse(**content))

        items.sort(key=lambda item: item.created_at, reverse=True)
        return ContentListResponse(items=items)

    def approve(self, content_id: str, payload: ContentApproveRequest, context: RequestContext) -> ContentStatusChangeResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_APPROVAL", message="승인 권한이 없습니다.")
        ensure_authenticated_actor(context)
        content = db_repository.get_content(content_id)
        if not content:
            raise AppError(status_code=404, error_code="CONTENT_NOT_FOUND", message="콘텐츠를 찾을 수 없습니다.")
        self._ensure_not_deleted(content)
        ensure_merchant_scope(context, content["merchant_id"], error_code="FORBIDDEN_APPROVAL", message="승인 권한이 없습니다.")
        ensure_content_transition(content["status"], ContentStatus.APPROVED, "승인")

        approved_at = now_utc()
        db_repository.update_content(content_id, status=ContentStatus.APPROVED, updated_at=approved_at)
        audit_service.record(
            action="content.approve",
            resource_type="content",
            resource_id=content_id,
            context=context,
            merchant_id=content["merchant_id"],
            metadata={"approved_by": payload.approver_id, "comment": payload.comment or ""},
        )
        return ContentStatusChangeResponse(
            content_id=content_id,
            status=ContentStatus.APPROVED,
            approved_by=payload.approver_id,
            approved_at=approved_at,
        )

    def reject(self, content_id: str, payload: ContentRejectRequest, context: RequestContext) -> ContentStatusChangeResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_REJECTION", message="반려 권한이 없습니다.")
        ensure_authenticated_actor(context)
        content = db_repository.get_content(content_id)
        if not content:
            raise AppError(status_code=404, error_code="CONTENT_NOT_FOUND", message="콘텐츠를 찾을 수 없습니다.")
        self._ensure_not_deleted(content)
        ensure_merchant_scope(context, content["merchant_id"], error_code="FORBIDDEN_REJECTION", message="반려 권한이 없습니다.")
        ensure_content_transition(content["status"], ContentStatus.REJECTED, "반려")

        rejected_at = now_utc()
        db_repository.update_content(content_id, status=ContentStatus.REJECTED, updated_at=rejected_at)
        audit_service.record(
            action="content.reject",
            resource_type="content",
            resource_id=content_id,
            context=context,
            merchant_id=content["merchant_id"],
            metadata={"reviewer_id": payload.reviewer_id, "reason": payload.reason},
        )
        return ContentStatusChangeResponse(
            content_id=content_id,
            status=ContentStatus.REJECTED,
            rejected_by=payload.reviewer_id,
            reason=payload.reason,
        )

    def publish(self, content_id: str, payload: ContentPublishRequest, context: RequestContext) -> ContentPublishResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_PUBLISH", message="게시 권한이 없습니다.")
        ensure_authenticated_actor(context)
        return publish_service.publish_content(content_id, payload, context)

    def update_overlay(self, content_id: str, payload: ContentOverlayUpdateRequest, context: RequestContext) -> ContentOverlayResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_CONTENT_ACCESS", message="콘텐츠 수정 권한이 없습니다.")
        ensure_authenticated_actor(context)
        content = db_repository.get_content(content_id)
        if not content:
            raise AppError(status_code=404, error_code="CONTENT_NOT_FOUND", message="콘텐츠를 찾을 수 없습니다.")
        self._ensure_not_deleted(content)
        ensure_merchant_scope(context, content["merchant_id"], error_code="FORBIDDEN_CONTENT_ACCESS", message="콘텐츠 수정 권한이 없습니다.")

        if payload.selected_variant_asset_id and payload.selected_variant_asset_id not in content.get("variant_asset_ids", []):
            raise AppError(status_code=422, error_code="INVALID_VARIANT_ASSET", message="선택한 생성 이미지를 찾을 수 없습니다.")

        updated = db_repository.update_content(
            content_id,
            selected_variant_asset_id=payload.selected_variant_asset_id,
            overlay_headline=payload.overlay_headline,
            overlay_subheadline=payload.overlay_subheadline,
            overlay_cta=payload.overlay_cta,
            updated_at=now_utc(),
        )
        audit_service.record(
            action="content.overlay_update",
            resource_type="content",
            resource_id=content_id,
            context=context,
            merchant_id=content["merchant_id"],
            metadata={"selected_variant_asset_id": payload.selected_variant_asset_id or ""},
        )
        return ContentOverlayResponse(**(updated or content))

    def regenerate_image(
        self,
        content_id: str,
        payload: ContentImageRegenerateRequest,
        context: RequestContext,
    ) -> ContentOverlayResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_CONTENT_ACCESS", message="콘텐츠 수정 권한이 없습니다.")
        ensure_authenticated_actor(context)
        content = db_repository.get_content(content_id)
        if not content:
            raise AppError(status_code=404, error_code="CONTENT_NOT_FOUND", message="콘텐츠를 찾을 수 없습니다.")
        self._ensure_not_deleted(content)
        ensure_merchant_scope(context, content["merchant_id"], error_code="FORBIDDEN_CONTENT_ACCESS", message="콘텐츠 수정 권한이 없습니다.")

        if not content.get("apply_image_variant") or content.get("image_variant_provider") != "nano_banana":
            raise AppError(status_code=409, error_code="IMAGE_VARIANT_DISABLED", message="이미지 생성이 활성화된 콘텐츠가 아닙니다.")

        source_asset_ids = payload.source_asset_ids or content.get("uploaded_asset_ids", [])
        self._validate_asset_ownership(content["merchant_id"], source_asset_ids)
        image_variant_job_id, _, variant_asset_ids = image_variant_service.create_variants_for_content(
            content_id=content_id,
            content=content,
            source_asset_ids=source_asset_ids,
            immediate_publish=False,
            context=context,
        )
        updated = db_repository.update_content(
            content_id,
            image_variant_job_id=image_variant_job_id,
            selected_variant_asset_id=variant_asset_ids[0] if variant_asset_ids else None,
            variant_asset_ids=variant_asset_ids,
            updated_at=now_utc(),
        )
        audit_service.record(
            action="content.image_regenerate",
            resource_type="content",
            resource_id=content_id,
            context=context,
            merchant_id=content["merchant_id"],
            metadata={"variant_asset_count": len(variant_asset_ids)},
        )
        return ContentOverlayResponse(**(updated or content))

    def delete(self, content_id: str, context: RequestContext) -> ContentDeleteResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_DELETE", message="삭제 권한이 없습니다.")
        ensure_authenticated_actor(context)
        content = db_repository.get_content(content_id)
        if not content:
            raise AppError(status_code=404, error_code="CONTENT_NOT_FOUND", message="콘텐츠를 찾을 수 없습니다.")
        self._ensure_not_deleted(content)
        ensure_merchant_scope(context, content["merchant_id"], error_code="FORBIDDEN_DELETE", message="삭제 권한이 없습니다.")
        ensure_content_transition(content["status"], ContentStatus.DELETED, "삭제")
        deleted_at = now_utc()
        db_repository.update_content(content_id, status=ContentStatus.DELETED, updated_at=deleted_at)
        audit_service.record(
            action="content.delete",
            resource_type="content",
            resource_id=content_id,
            context=context,
            merchant_id=content["merchant_id"],
            metadata={"previous_status": content["status"], "next_status": ContentStatus.DELETED.value},
        )
        return ContentDeleteResponse(
            content_id=content_id,
            deleted=True,
            message="콘텐츠 초안을 삭제했습니다.",
        )


content_service = ContentService()
