from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import RequestContext, get_request_context
from app.schemas.asset import AssetDetailResponse, AssetListResponse, AssetUploadInitRequest, AssetUploadInitResponse
from app.services.asset import asset_service


router = APIRouter(prefix="/assets")


@router.post("/upload-init", response_model=AssetUploadInitResponse, status_code=201)
def init_asset_upload(
    payload: AssetUploadInitRequest,
    context: RequestContext = Depends(get_request_context),
) -> AssetUploadInitResponse:
    return asset_service.init_upload(payload, context)


@router.get("/{asset_id}", response_model=AssetDetailResponse)
def get_asset(
    asset_id: str,
    context: RequestContext = Depends(get_request_context),
) -> AssetDetailResponse:
    return asset_service.get(asset_id, context)


@router.get("", response_model=AssetListResponse)
def list_assets(
    merchant_id: Optional[str] = Query(default=None),
    asset_type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    context: RequestContext = Depends(get_request_context),
) -> AssetListResponse:
    return asset_service.list(context, merchant_id=merchant_id, asset_type=asset_type, status=status)
