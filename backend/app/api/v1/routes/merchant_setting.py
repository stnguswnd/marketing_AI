from fastapi import APIRouter, Depends, Query

from app.core.auth import RequestContext, get_request_context
from app.schemas.merchant_setting import MerchantNanoBananaSettingRequest, MerchantNanoBananaSettingResponse
from app.services.merchant_setting import merchant_setting_service


router = APIRouter(prefix="/merchant-settings")


@router.get("/nano-banana", response_model=MerchantNanoBananaSettingResponse)
def get_nano_banana_setting(
    merchant_id: str = Query(min_length=1),
    context: RequestContext = Depends(get_request_context),
) -> MerchantNanoBananaSettingResponse:
    return merchant_setting_service.get_nano_banana_setting(merchant_id, context)


@router.put("/nano-banana", response_model=MerchantNanoBananaSettingResponse)
def save_nano_banana_setting(
    payload: MerchantNanoBananaSettingRequest,
    context: RequestContext = Depends(get_request_context),
) -> MerchantNanoBananaSettingResponse:
    return merchant_setting_service.save_nano_banana_setting(payload, context)
