from fastapi import APIRouter, Depends

from app.core.auth import RequestContext, get_request_context
from app.schemas.observability import ObservabilitySummaryResponse, RequestLogListResponse
from app.services.observability import observability_service


router = APIRouter(prefix="/observability")


@router.get("/requests", response_model=RequestLogListResponse)
def list_request_logs(context: RequestContext = Depends(get_request_context)) -> RequestLogListResponse:
    return observability_service.list_requests(context)


@router.get("/summary", response_model=ObservabilitySummaryResponse)
def get_observability_summary(context: RequestContext = Depends(get_request_context)) -> ObservabilitySummaryResponse:
    return observability_service.summary(context)
