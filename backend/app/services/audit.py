from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.core.auth import RequestContext
from app.core.permissions import ensure_roles
from app.repositories.database import db_repository
from app.schemas.audit import AuditLogListResponse, AuditLogResponse


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class AuditService:
    def record(
        self,
        *,
        action: str,
        resource_type: str,
        resource_id: str,
        context: Optional[RequestContext],
        merchant_id: Optional[str] = None,
        status: str = "succeeded",
        metadata: Optional[dict[str, object]] = None,
    ) -> str:
        audit_log_id = f"audit_{uuid4().hex[:10]}"
        db_repository.create_audit_log({
            "audit_log_id": audit_log_id,
            "request_id": context.request_id if context else None,
            "actor_id": context.user_id if context else None,
            "actor_role": context.role if context else "system",
            "merchant_id": merchant_id if merchant_id is not None else (context.merchant_id if context else None),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status": status,
            "metadata": metadata or {},
            "created_at": now_utc(),
        })
        return audit_log_id

    def list(
        self,
        context: RequestContext,
        *,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> AuditLogListResponse:
        ensure_roles(context, "operator", "admin", error_code="FORBIDDEN_AUDIT_ACCESS", message="감사 로그 접근 권한이 없습니다.")

        items = []
        for item in db_repository.list_audit_logs():
            if action and item["action"] != action:
                continue
            if resource_type and item["resource_type"] != resource_type:
                continue
            if actor_id and item["actor_id"] != actor_id:
                continue
            items.append(AuditLogResponse(**item))

        items.sort(key=lambda item: item.created_at, reverse=True)
        return AuditLogListResponse(items=items)


audit_service = AuditService()
