from typing import List, Optional

from typing_extensions import TypedDict

from app.schemas.common import ContentGoal, ContentStatus, CountryCode, PlatformType, ReviewSensitivity


class ContentGraphState(TypedDict, total=False):
    merchant_id: str
    target_country: CountryCode
    platform: PlatformType
    goal: ContentGoal
    input_brief: str
    tone: Optional[str]
    must_include: List[str]
    must_avoid: List[str]
    uploaded_asset_ids: List[str]
    status: ContentStatus
    strategy_notes: str
    title: str
    body: str
    hashtags: List[str]
    validated: bool


class ReviewGraphState(TypedDict, total=False):
    merchant_id: str
    platform: str
    review_text: str
    rating: int
    sensitivity: ReviewSensitivity
    escalated: bool
    reply_draft: str


class ReportGraphState(TypedDict, total=False):
    scope_type: str
    scope_id: str
    year: int
    month: int
