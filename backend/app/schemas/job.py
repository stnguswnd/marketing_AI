from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import JobStatus


class JobStatusResponse(BaseModel):
    job_id: str
    job_type: str
    status: JobStatus
    resource_type: str
    resource_id: str
    created_at: datetime
    updated_at: datetime


class JobListItemResponse(BaseModel):
    job_id: str
    job_type: str
    status: JobStatus
    resource_type: str
    resource_id: str
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    items: list[JobListItemResponse]
