from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.core.auth import RequestContext
from app.core.errors import AppError
from app.core.permissions import ensure_authenticated_actor, ensure_merchant_scope, ensure_roles
from app.repositories.database import db_repository
from app.schemas.report import MonthlyReportGenerateRequest, MonthlyReportGenerateResponse, ReportListItemResponse, ReportListResponse
from app.services.audit import audit_service


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class ReportService:
    def generate(
        self,
        payload: MonthlyReportGenerateRequest,
        context: RequestContext,
    ) -> MonthlyReportGenerateResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_REPORT_ACCESS", message="리포트 접근 권한이 없습니다.")
        ensure_authenticated_actor(context)
        if context.role == "merchant":
            if payload.scope_type != "merchant":
                raise AppError(status_code=403, error_code="FORBIDDEN_REPORT_ACCESS", message="리포트 접근 권한이 없습니다.")
            ensure_merchant_scope(context, payload.scope_id, error_code="FORBIDDEN_REPORT_ACCESS", message="리포트 접근 권한이 없습니다.")
        report_id = f"report_{uuid4().hex[:8]}"
        job_id = f"job_report_{uuid4().hex[:8]}"
        created_at = now_utc()
        report_status = "succeeded"
        db_repository.create_report({
            "report_id": report_id,
            "scope_type": payload.scope_type,
            "scope_id": payload.scope_id,
            "year": payload.year,
            "month": payload.month,
            "status": report_status,
            "created_at": created_at,
        })
        db_repository.create_job({
            "job_id": job_id,
            "job_type": "monthly_report_generate",
            "status": report_status,
            "resource_type": "report",
            "resource_id": report_id,
            "created_at": created_at,
            "updated_at": created_at,
        })
        audit_service.record(
            action="report.generate_monthly",
            resource_type="report",
            resource_id=report_id,
            context=context,
            metadata={"scope_type": payload.scope_type, "scope_id": payload.scope_id, "year": payload.year, "month": payload.month},
        )
        return MonthlyReportGenerateResponse(report_id=report_id, job_id=job_id, status=report_status)

    def list(
        self,
        context: RequestContext,
        scope_type: Optional[str] = None,
        scope_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> ReportListResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_REPORT_ACCESS", message="리포트 접근 권한이 없습니다.")
        if context.role == "merchant":
            scope_type = "merchant"
            scope_id = context.merchant_id

        items = []
        for report in db_repository.list_reports():
            if scope_type and report["scope_type"] != scope_type:
                continue
            if scope_id and report["scope_id"] != scope_id:
                continue
            if status and report["status"] != status:
                continue
            items.append(ReportListItemResponse(**report))

        items.sort(key=lambda item: item.created_at, reverse=True)
        return ReportListResponse(items=items)


report_service = ReportService()
