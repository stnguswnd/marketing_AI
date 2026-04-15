from __future__ import annotations

from app.core.auth import RequestContext
from app.core.errors import AppError
from app.core.permissions import ensure_merchant_scope, ensure_roles
from app.repositories.memory import repository
from app.schemas.publish import PublishResultListItemResponse, PublishResultListResponse, PublishResultResponse


class PublishResultService:
    def get(self, publish_result_id: str, context: RequestContext) -> PublishResultResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_PUBLISH_ACCESS", message="발행 결과 접근 권한이 없습니다.")
        publish_result = repository.publish_results.get(publish_result_id)
        if not publish_result:
            raise AppError(status_code=404, error_code="PUBLISH_RESULT_NOT_FOUND", message="발행 결과를 찾을 수 없습니다.")
        content = repository.contents.get(publish_result["content_id"])
        if content:
            ensure_merchant_scope(context, content["merchant_id"], error_code="FORBIDDEN_PUBLISH_ACCESS", message="발행 결과 접근 권한이 없습니다.")
        return PublishResultResponse(**publish_result)

    def list(self, context: RequestContext) -> PublishResultListResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_PUBLISH_ACCESS", message="발행 결과 접근 권한이 없습니다.")
        items = []
        for item in repository.publish_results.values():
            content = repository.contents.get(item["content_id"])
            if context.role == "merchant" and content and context.merchant_id != content["merchant_id"]:
                continue
            items.append(item)
        items.sort(key=lambda item: item["created_at"], reverse=True)
        return PublishResultListResponse(items=[PublishResultListItemResponse(**item) for item in items])


publish_result_service = PublishResultService()
