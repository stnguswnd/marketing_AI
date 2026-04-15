from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.core.auth import RequestContext
from app.core.permissions import ensure_roles
from app.repositories.database import db_repository
from app.schemas.admin import MerchantSummaryListResponse, MerchantSummaryResponse
from app.schemas.common import ContentStatus, ReviewStatus


def _latest_timestamp(current: Optional[datetime], *values: Optional[datetime]) -> Optional[datetime]:
    candidates = [value for value in (current, *values) if value is not None]
    if not candidates:
        return None
    return max(candidates)


class AdminService:
    def list_merchants(self, context: RequestContext) -> MerchantSummaryListResponse:
        ensure_roles(context, "admin", error_code="FORBIDDEN_ADMIN_ACCESS", message="관리자 접근 권한이 없습니다.")

        summaries: dict[str, dict[str, object]] = {}

        def ensure_summary(merchant_id: str) -> dict[str, object]:
            if merchant_id not in summaries:
                summaries[merchant_id] = {
                    "merchant_id": merchant_id,
                    "content_count": 0,
                    "pending_content_count": 0,
                    "approved_content_count": 0,
                    "review_count": 0,
                    "pending_review_count": 0,
                    "asset_count": 0,
                    "report_count": 0,
                    "latest_activity_at": None,
                }
            return summaries[merchant_id]

        for content in db_repository.list_contents():
            if content["status"] == ContentStatus.DELETED:
                continue
            summary = ensure_summary(content["merchant_id"])
            summary["content_count"] = int(summary["content_count"]) + 1
            if content["status"] == ContentStatus.DRAFT:
                summary["pending_content_count"] = int(summary["pending_content_count"]) + 1
            if content["status"] == ContentStatus.APPROVED:
                summary["approved_content_count"] = int(summary["approved_content_count"]) + 1
            summary["latest_activity_at"] = _latest_timestamp(
                summary["latest_activity_at"],
                content.get("updated_at"),
                content.get("created_at"),
            )

        for review in db_repository.list_reviews():
            summary = ensure_summary(review["merchant_id"])
            summary["review_count"] = int(summary["review_count"]) + 1
            if review["status"] == ReviewStatus.DRAFT:
                summary["pending_review_count"] = int(summary["pending_review_count"]) + 1
            summary["latest_activity_at"] = _latest_timestamp(
                summary["latest_activity_at"],
                review.get("created_at"),
            )

        for asset in db_repository.list_assets():
            summary = ensure_summary(asset["merchant_id"])
            summary["asset_count"] = int(summary["asset_count"]) + 1
            summary["latest_activity_at"] = _latest_timestamp(
                summary["latest_activity_at"],
                asset.get("updated_at"),
                asset.get("created_at"),
            )

        for report in db_repository.list_reports():
            if report["scope_type"] != "merchant":
                continue
            summary = ensure_summary(report["scope_id"])
            summary["report_count"] = int(summary["report_count"]) + 1
            summary["latest_activity_at"] = _latest_timestamp(
                summary["latest_activity_at"],
                report.get("created_at"),
            )

        items = [
            MerchantSummaryResponse(
                **{
                    **summary,
                    "latest_activity_at": summary["latest_activity_at"].isoformat()
                    if summary["latest_activity_at"] is not None
                    else None,
                }
            )
            for summary in summaries.values()
        ]
        items.sort(
            key=lambda item: (item.latest_activity_at or "", item.merchant_id),
            reverse=True,
        )
        return MerchantSummaryListResponse(items=items)


admin_service = AdminService()
