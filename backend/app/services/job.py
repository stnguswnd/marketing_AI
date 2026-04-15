from typing import Optional

from app.core.auth import RequestContext
from app.core.errors import AppError
from app.core.permissions import ensure_merchant_scope, ensure_roles
from app.repositories.memory import repository
from app.schemas.job import JobListItemResponse, JobListResponse, JobStatusResponse


class JobService:
    def _job_merchant_id(self, job: dict) -> Optional[str]:
        resource_type = job["resource_type"]
        resource_id = job["resource_id"]
        if resource_type == "content":
            content = repository.contents.get(resource_id)
            return content["merchant_id"] if content else None
        if resource_type == "review":
            review = repository.reviews.get(resource_id)
            return review["merchant_id"] if review else None
        if resource_type == "report":
            report = repository.reports.get(resource_id)
            if report and report["scope_type"] == "merchant":
                return report["scope_id"]
        if resource_type == "asset":
            asset = repository.assets.get(resource_id)
            return asset["merchant_id"] if asset else None
        return None

    def get(self, job_id: str, context: RequestContext) -> JobStatusResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_JOB_ACCESS", message="작업 접근 권한이 없습니다.")
        job = repository.jobs.get(job_id)
        if not job:
            raise AppError(status_code=404, error_code="JOB_NOT_FOUND", message="작업을 찾을 수 없습니다.")
        merchant_id = self._job_merchant_id(job)
        if merchant_id:
            ensure_merchant_scope(context, merchant_id, error_code="FORBIDDEN_JOB_ACCESS", message="작업 접근 권한이 없습니다.")
        return JobStatusResponse(**job)

    def list(
        self,
        context: RequestContext,
        resource_type: str = None,
        status: str = None,
    ) -> JobListResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_JOB_ACCESS", message="작업 접근 권한이 없습니다.")

        items = []
        for job in repository.jobs.values():
            if resource_type and job["resource_type"] != resource_type:
                continue
            if status and job["status"] != status:
                continue
            merchant_id = self._job_merchant_id(job)
            if context.role == "merchant" and merchant_id and context.merchant_id != merchant_id:
                continue
            items.append(JobListItemResponse(**job))

        items.sort(key=lambda item: item.created_at, reverse=True)
        return JobListResponse(items=items)


job_service = JobService()
