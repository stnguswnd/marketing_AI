from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PlatformType, ReviewSensitivity, ReviewStatus


class ReviewWebhookRequest(BaseModel):
    platform: PlatformType
    external_review_id: str = Field(min_length=1)
    merchant_id: str = Field(min_length=1)
    author_name: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)
    language: str = Field(min_length=2, max_length=10)
    review_text: str = Field(min_length=1)
    reviewed_at: datetime


class ReviewWebhookResponse(BaseModel):
    review_id: str
    job_id: str
    status: str


class ReviewDetailResponse(BaseModel):
    review_id: str
    merchant_id: str
    platform: PlatformType
    rating: int
    language: str
    review_text: str
    sensitivity: ReviewSensitivity
    status: ReviewStatus
    reply_draft: str
    escalated: bool
    created_at: datetime


class ReviewListItemResponse(BaseModel):
    review_id: str
    merchant_id: str
    platform: PlatformType
    rating: int
    sensitivity: ReviewSensitivity
    status: ReviewStatus
    escalated: bool
    created_at: datetime


class ReviewListResponse(BaseModel):
    items: list[ReviewListItemResponse]


class ReviewApproveReplyRequest(BaseModel):
    approver_id: str = Field(min_length=1)
    reply_text: Optional[str] = None


class ReviewApproveReplyResponse(BaseModel):
    review_id: str
    status: ReviewStatus
    approved_reply_text: str
