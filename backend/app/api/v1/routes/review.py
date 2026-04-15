from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import RequestContext, get_request_context, verify_webhook_secret
from app.schemas.review import (
    ReviewApproveReplyRequest,
    ReviewApproveReplyResponse,
    ReviewDetailResponse,
    ReviewListResponse,
    ReviewWebhookRequest,
    ReviewWebhookResponse,
)
from app.services.review import review_service


router = APIRouter()


@router.post(
    "/webhooks/reviews",
    response_model=ReviewWebhookResponse,
    status_code=202,
    dependencies=[Depends(verify_webhook_secret)],
)
def ingest_review_webhook(payload: ReviewWebhookRequest) -> ReviewWebhookResponse:
    return review_service.ingest(payload)


@router.get(
    "/reviews/{review_id}",
    response_model=ReviewDetailResponse,
)
def get_review(
    review_id: str,
    context: RequestContext = Depends(get_request_context),
) -> ReviewDetailResponse:
    return review_service.get(review_id, context)


@router.get("/reviews", response_model=ReviewListResponse)
def list_reviews(
    merchant_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    sensitivity: Optional[str] = Query(default=None),
    context: RequestContext = Depends(get_request_context),
) -> ReviewListResponse:
    return review_service.list(context, merchant_id=merchant_id, status=status, sensitivity=sensitivity)


@router.post(
    "/reviews/{review_id}/approve-reply",
    response_model=ReviewApproveReplyResponse,
)
def approve_review_reply(
    review_id: str,
    payload: ReviewApproveReplyRequest,
    context: RequestContext = Depends(get_request_context),
) -> ReviewApproveReplyResponse:
    return review_service.approve_reply(review_id, payload, context)
