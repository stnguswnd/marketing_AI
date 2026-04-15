from __future__ import annotations

from collections import Counter

from app.core.auth import RequestContext
from app.core.permissions import ensure_roles
from app.repositories.database import db_repository
from app.schemas.observability import ObservabilitySummaryResponse, RequestLogListResponse, RequestLogResponse


class ObservabilityService:
    def list_requests(self, context: RequestContext) -> RequestLogListResponse:
        ensure_roles(context, "operator", "admin", error_code="FORBIDDEN_OBSERVABILITY_ACCESS", message="관측 로그 접근 권한이 없습니다.")
        items = [RequestLogResponse(**item) for item in db_repository.list_request_logs()]
        items.sort(key=lambda item: item.created_at, reverse=True)
        return RequestLogListResponse(items=items)

    def summary(self, context: RequestContext) -> ObservabilitySummaryResponse:
        ensure_roles(context, "operator", "admin", error_code="FORBIDDEN_OBSERVABILITY_ACCESS", message="관측 로그 접근 권한이 없습니다.")
        request_logs = db_repository.list_request_logs()
        status_counts = Counter(str(item["status_code"]) for item in request_logs)
        path_counts = Counter(item["path"] for item in request_logs)
        recent_request_ids = [item["request_id"] for item in sorted(request_logs, key=lambda item: item["created_at"], reverse=True)[:5]]
        return ObservabilitySummaryResponse(
            total_requests=len(request_logs),
            status_counts=dict(status_counts),
            path_counts=dict(path_counts),
            recent_request_ids=recent_request_ids,
        )


observability_service = ObservabilityService()
