from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.core.auth import RequestContext
from app.core.errors import AppError
from app.core.permissions import ensure_authenticated_actor, ensure_merchant_scope, ensure_roles
from app.repositories.memory import repository
from app.schemas.asset import AssetDetailResponse, AssetListItemResponse, AssetListResponse, AssetUploadInitRequest, AssetUploadInitResponse
from app.services.audit import audit_service


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class AssetService:
    def init_upload(self, payload: AssetUploadInitRequest, context: RequestContext) -> AssetUploadInitResponse:
        ensure_roles(context, "merchant", "operator", "admin")
        ensure_authenticated_actor(context)
        ensure_merchant_scope(context, payload.merchant_id)
        if payload.content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise AppError(
                status_code=415,
                error_code="UNSUPPORTED_ASSET_TYPE",
                message="지원하지 않는 파일 형식입니다.",
            )

        asset_id = f"asset_{uuid4().hex[:8]}"
        created_at = now_utc()
        repository.assets[asset_id] = {
            "asset_id": asset_id,
            "merchant_id": payload.merchant_id,
            "filename": payload.filename,
            "content_type": payload.content_type,
            "size_bytes": payload.size_bytes,
            "asset_type": "source",
            "status": "uploaded",
            "provider": None,
            "generated_by_job_id": None,
            "source_asset_ids": [],
            "created_at": created_at,
            "updated_at": created_at,
        }
        audit_service.record(
            action="asset.upload_init",
            resource_type="asset",
            resource_id=asset_id,
            context=context,
            merchant_id=payload.merchant_id,
            metadata={"filename": payload.filename, "content_type": payload.content_type},
        )
        return AssetUploadInitResponse(
            asset_id=asset_id,
            upload_url=f"https://upload.example.com/{asset_id}",
            asset_type="source",
        )

    def get(self, asset_id: str, context: RequestContext) -> AssetDetailResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_ASSET_ACCESS", message="자산 접근 권한이 없습니다.")

        asset = repository.assets.get(asset_id)
        if not asset:
            raise AppError(status_code=404, error_code="ASSET_NOT_FOUND", message="자산을 찾을 수 없습니다.")

        ensure_merchant_scope(context, asset["merchant_id"], error_code="FORBIDDEN_ASSET_ACCESS", message="자산 접근 권한이 없습니다.")

        return AssetDetailResponse(**asset)

    def list(
        self,
        context: RequestContext,
        merchant_id: Optional[str] = None,
        asset_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> AssetListResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_ASSET_ACCESS", message="자산 접근 권한이 없습니다.")
        if context.role == "merchant":
            merchant_id = context.merchant_id

        items = []
        for asset in repository.assets.values():
            if merchant_id and asset["merchant_id"] != merchant_id:
                continue
            if asset_type and asset["asset_type"] != asset_type:
                continue
            if status and asset["status"] != status:
                continue
            items.append(AssetListItemResponse(**asset))

        items.sort(key=lambda item: item.created_at, reverse=True)
        return AssetListResponse(items=items)


asset_service = AssetService()
