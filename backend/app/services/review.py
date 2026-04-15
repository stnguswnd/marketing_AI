from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.core.auth import RequestContext
from app.core.errors import AppError
from app.core.permissions import ensure_authenticated_actor, ensure_merchant_scope, ensure_roles
from app.domain.status_rules import ensure_review_transition
from app.graphs.review import run_review_graph
from app.repositories.memory import repository
from app.schemas.common import ReviewStatus
from app.schemas.review import (
    ReviewApproveReplyRequest,
    ReviewApproveReplyResponse,
    ReviewDetailResponse,
    ReviewListItemResponse,
    ReviewListResponse,
    ReviewWebhookRequest,
    ReviewWebhookResponse,
)
from app.services.audit import audit_service


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class ReviewService:
    def ingest(self, payload: ReviewWebhookRequest) -> ReviewWebhookResponse:
        review_id = f"review_{uuid4().hex[:8]}"
        job_id = f"job_review_{uuid4().hex[:8]}"
        created_at = now_utc()
        graph_result = run_review_graph(
            {
                "merchant_id": payload.merchant_id,
                "platform": payload.platform.value,
                "review_text": payload.review_text,
                "rating": payload.rating,
            }
        )
        repository.reviews[review_id] = {
            "review_id": review_id,
            "merchant_id": payload.merchant_id,
            "platform": payload.platform,
            "rating": payload.rating,
            "language": payload.language,
            "review_text": payload.review_text,
            "sensitivity": graph_result["sensitivity"],
            "status": ReviewStatus.DRAFT,
            "reply_draft": graph_result["reply_draft"],
            "escalated": graph_result["escalated"],
            "created_at": created_at,
        }
        repository.jobs[job_id] = {
            "job_id": job_id,
            "job_type": "review_ingest",
            "status": "queued",
            "resource_type": "review",
            "resource_id": review_id,
            "created_at": created_at,
            "updated_at": created_at,
        }
        audit_service.record(
            action="review.ingest_webhook",
            resource_type="review",
            resource_id=review_id,
            context=None,
            merchant_id=payload.merchant_id,
            metadata={"platform": payload.platform.value, "rating": payload.rating},
        )
        return ReviewWebhookResponse(review_id=review_id, job_id=job_id, status="queued")

    def get(self, review_id: str, context: RequestContext) -> ReviewDetailResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_REVIEW_ACCESS", message="리뷰 접근 권한이 없습니다.")
        review = repository.reviews.get(review_id)
        if not review:
            raise AppError(status_code=404, error_code="REVIEW_NOT_FOUND", message="리뷰를 찾을 수 없습니다.")
        ensure_merchant_scope(context, review["merchant_id"], error_code="FORBIDDEN_REVIEW_ACCESS", message="리뷰 접근 권한이 없습니다.")
        return ReviewDetailResponse(**review)

    def list(
        self,
        context: RequestContext,
        merchant_id: Optional[str] = None,
        status: Optional[str] = None,
        sensitivity: Optional[str] = None,
    ) -> ReviewListResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_REVIEW_ACCESS", message="리뷰 접근 권한이 없습니다.")
        if context.role == "merchant":
            merchant_id = context.merchant_id

        items = []
        for review in repository.reviews.values():
            if merchant_id and review["merchant_id"] != merchant_id:
                continue
            if status and review["status"] != status:
                continue
            if sensitivity and review["sensitivity"] != sensitivity:
                continue
            items.append(ReviewListItemResponse(**review))

        items.sort(key=lambda item: item.created_at, reverse=True)
        return ReviewListResponse(items=items)

    def approve_reply(
        self,
        review_id: str,
        payload: ReviewApproveReplyRequest,
        context: RequestContext,
    ) -> ReviewApproveReplyResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_REVIEW_APPROVAL", message="리뷰 승인 권한이 없습니다.")
        ensure_authenticated_actor(context)
        review = repository.reviews.get(review_id)
        if not review:
            raise AppError(status_code=404, error_code="REVIEW_NOT_FOUND", message="리뷰를 찾을 수 없습니다.")
        ensure_merchant_scope(context, review["merchant_id"], error_code="FORBIDDEN_REVIEW_APPROVAL", message="리뷰 승인 권한이 없습니다.")
        approved_reply = payload.reply_text or review["reply_draft"]
        ensure_review_transition(review["status"], ReviewStatus.APPROVED, "리뷰 답글 승인")
        review["status"] = ReviewStatus.APPROVED
        review["reply_draft"] = approved_reply
        audit_service.record(
            action="review.approve_reply",
            resource_type="review",
            resource_id=review_id,
            context=context,
            merchant_id=review["merchant_id"],
            metadata={"approver_id": payload.approver_id},
        )
        return ReviewApproveReplyResponse(
            review_id=review_id,
            status=ReviewStatus.APPROVED,
            approved_reply_text=approved_reply,
        )


review_service = ReviewService()
