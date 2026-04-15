from typing import Optional

from pydantic import BaseModel


class MerchantSummaryResponse(BaseModel):
    merchant_id: str
    content_count: int
    pending_content_count: int
    approved_content_count: int
    review_count: int
    pending_review_count: int
    asset_count: int
    report_count: int
    latest_activity_at: Optional[str] = None


class MerchantSummaryListResponse(BaseModel):
    items: list[MerchantSummaryResponse]
