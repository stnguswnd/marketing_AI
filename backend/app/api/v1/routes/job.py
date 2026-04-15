from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import RequestContext, get_request_context
from app.schemas.job import JobListResponse, JobStatusResponse
from app.services.job import job_service


router = APIRouter(prefix="/jobs")


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job(
    job_id: str,
    context: RequestContext = Depends(get_request_context),
) -> JobStatusResponse:
    return job_service.get(job_id, context)


@router.get("", response_model=JobListResponse)
def list_jobs(
    resource_type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    context: RequestContext = Depends(get_request_context),
) -> JobListResponse:
    return job_service.list(context, resource_type=resource_type, status=status)
