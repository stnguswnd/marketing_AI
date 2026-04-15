from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    audit_log_id: str
    request_id: Optional[str] = None
    actor_id: Optional[str] = None
    actor_role: Optional[str] = None
    merchant_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: str
    status: str
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
