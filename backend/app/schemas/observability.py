from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RequestLogResponse(BaseModel):
    request_id: str
    method: str
    path: str
    status_code: int
    duration_ms: int
    actor_role: Optional[str] = None
    actor_id: Optional[str] = None
    merchant_id: Optional[str] = None
    created_at: datetime


class RequestLogListResponse(BaseModel):
    items: list[RequestLogResponse]


class ObservabilitySummaryResponse(BaseModel):
    total_requests: int
    status_counts: dict[str, int] = Field(default_factory=dict)
    path_counts: dict[str, int] = Field(default_factory=dict)
    recent_request_ids: list[str] = Field(default_factory=list)
