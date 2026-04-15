from __future__ import annotations

from app.core.errors import AppError
from app.schemas.common import ContentStatus, ReviewStatus


CONTENT_TRANSITIONS: dict[ContentStatus, set[ContentStatus]] = {
    ContentStatus.DRAFT: {ContentStatus.APPROVED, ContentStatus.REJECTED},
    ContentStatus.APPROVED: {ContentStatus.SCHEDULED},
    ContentStatus.SCHEDULED: {ContentStatus.PUBLISHED},
    ContentStatus.PUBLISHED: set(),
    ContentStatus.REJECTED: set(),
}

REVIEW_TRANSITIONS: dict[ReviewStatus, set[ReviewStatus]] = {
    ReviewStatus.DRAFT: {ReviewStatus.APPROVED},
    ReviewStatus.APPROVED: set(),
}


def ensure_content_transition(current: ContentStatus, target: ContentStatus, action_label: str) -> None:
    if target not in CONTENT_TRANSITIONS.get(current, set()):
        raise AppError(
            status_code=409,
            error_code="INVALID_CONTENT_STATUS_TRANSITION",
            message=f"현재 상태에서는 {action_label}할 수 없습니다.",
        )


def ensure_review_transition(current: ReviewStatus, target: ReviewStatus, action_label: str) -> None:
    if target not in REVIEW_TRANSITIONS.get(current, set()):
        raise AppError(
            status_code=409,
            error_code="INVALID_REVIEW_STATUS_TRANSITION",
            message=f"현재 상태에서는 {action_label}할 수 없습니다.",
        )
