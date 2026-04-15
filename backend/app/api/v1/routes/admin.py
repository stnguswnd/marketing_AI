from fastapi import APIRouter, Depends

from app.core.auth import RequestContext, get_request_context
from app.schemas.admin import MerchantSummaryListResponse
from app.services.admin import admin_service


router = APIRouter(prefix="/admin")


@router.get("/merchants", response_model=MerchantSummaryListResponse)
def list_merchants(
    context: RequestContext = Depends(get_request_context),
) -> MerchantSummaryListResponse:
    return admin_service.list_merchants(context)
