from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import RequestContext, get_request_context
from app.schemas.report import MonthlyReportGenerateRequest, MonthlyReportGenerateResponse, ReportListResponse
from app.services.report import report_service


router = APIRouter(prefix="/reports")


@router.post("/monthly/generate", response_model=MonthlyReportGenerateResponse, status_code=202)
def generate_monthly_report(
    payload: MonthlyReportGenerateRequest,
    context: RequestContext = Depends(get_request_context),
) -> MonthlyReportGenerateResponse:
    return report_service.generate(payload, context)


@router.get("", response_model=ReportListResponse)
def list_reports(
    scope_type: Optional[str] = Query(default=None),
    scope_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    context: RequestContext = Depends(get_request_context),
) -> ReportListResponse:
    return report_service.list(context, scope_type=scope_type, scope_id=scope_id, status=status)
