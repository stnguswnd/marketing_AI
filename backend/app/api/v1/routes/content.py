from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import RequestContext, get_request_context
from app.schemas.content import (
    ContentApproveRequest,
    ContentDeleteResponse,
    ContentDetailResponse,
    ContentListResponse,
    ContentGenerateRequest,
    ContentGenerateResponse,
    ContentPublishRequest,
    ContentPublishResponse,
    ContentRejectRequest,
    ContentStatusChangeResponse,
)
from app.services.content import content_service


router = APIRouter(prefix="/contents")


@router.post("/generate", response_model=ContentGenerateResponse, status_code=201)
def generate_content(
    payload: ContentGenerateRequest,
    context: RequestContext = Depends(get_request_context),
) -> ContentGenerateResponse:
    return content_service.generate(payload, context)


@router.get("/{content_id}", response_model=ContentDetailResponse)
def get_content(
    content_id: str,
    context: RequestContext = Depends(get_request_context),
) -> ContentDetailResponse:
    return content_service.get(content_id, context)


@router.get("", response_model=ContentListResponse)
def list_contents(
    merchant_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    platform: Optional[str] = Query(default=None),
    context: RequestContext = Depends(get_request_context),
) -> ContentListResponse:
    return content_service.list(context, merchant_id=merchant_id, status=status, platform=platform)


@router.post("/{content_id}/approve", response_model=ContentStatusChangeResponse)
def approve_content(
    content_id: str,
    payload: ContentApproveRequest,
    context: RequestContext = Depends(get_request_context),
) -> ContentStatusChangeResponse:
    return content_service.approve(content_id, payload, context)


@router.post("/{content_id}/reject", response_model=ContentStatusChangeResponse)
def reject_content(
    content_id: str,
    payload: ContentRejectRequest,
    context: RequestContext = Depends(get_request_context),
) -> ContentStatusChangeResponse:
    return content_service.reject(content_id, payload, context)


@router.post("/{content_id}/publish", response_model=ContentPublishResponse, status_code=202)
def publish_content(
    content_id: str,
    payload: ContentPublishRequest,
    context: RequestContext = Depends(get_request_context),
) -> ContentPublishResponse:
    return content_service.publish(content_id, payload, context)


@router.delete("/{content_id}", response_model=ContentDeleteResponse)
def delete_content(
    content_id: str,
    context: RequestContext = Depends(get_request_context),
) -> ContentDeleteResponse:
    return content_service.delete(content_id, context)
