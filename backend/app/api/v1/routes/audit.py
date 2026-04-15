from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import RequestContext, get_request_context
from app.schemas.audit import AuditLogListResponse
from app.services.audit import audit_service


router = APIRouter(prefix="/audit-logs")


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    action: Optional[str] = Query(default=None),
    resource_type: Optional[str] = Query(default=None),
    actor_id: Optional[str] = Query(default=None),
    context: RequestContext = Depends(get_request_context),
) -> AuditLogListResponse:
    return audit_service.list(context, action=action, resource_type=resource_type, actor_id=actor_id)
