from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import UploadFile
from fastapi.responses import FileResponse

from app.core.auth import RequestContext
from app.core.errors import AppError
from app.core.permissions import ensure_authenticated_actor, ensure_merchant_scope, ensure_roles
from app.core.settings import get_settings
from app.repositories.database import db_repository
from app.schemas.asset import (
    AssetDetailResponse,
    AssetListItemResponse,
    AssetListResponse,
    AssetUploadBinaryResponse,
    AssetUploadInitRequest,
    AssetUploadInitResponse,
)
from app.services.audit import audit_service


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class AssetService:
    def _storage_dir(self) -> Path:
        storage_dir = Path(get_settings().asset_storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)
        return storage_dir

    def _stored_file_path(self, asset: dict) -> Path:
        suffix = Path(asset["filename"]).suffix or ".bin"
        return self._storage_dir() / f"{asset['asset_id']}{suffix.lower()}"

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
        db_repository.create_asset({
            "asset_id": asset_id,
            "merchant_id": payload.merchant_id,
            "filename": payload.filename,
            "content_type": payload.content_type,
            "size_bytes": payload.size_bytes,
            "asset_type": "source",
            "status": "pending_upload",
            "provider": None,
            "generated_by_job_id": None,
            "source_asset_ids": [],
            "preview_url": None,
            "created_at": created_at,
            "updated_at": created_at,
        })
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
            upload_url=f"{get_settings().public_api_base_url}/assets/{asset_id}/binary",
            asset_type="source",
        )

    def upload_binary(self, asset_id: str, file: UploadFile, context: RequestContext) -> AssetUploadBinaryResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_ASSET_ACCESS", message="자산 업로드 권한이 없습니다.")
        ensure_authenticated_actor(context)
        asset = db_repository.get_asset(asset_id)
        if not asset:
            raise AppError(status_code=404, error_code="ASSET_NOT_FOUND", message="자산을 찾을 수 없습니다.")
        ensure_merchant_scope(context, asset["merchant_id"], error_code="FORBIDDEN_ASSET_ACCESS", message="자산 업로드 권한이 없습니다.")
        if file.content_type != asset["content_type"]:
            raise AppError(status_code=415, error_code="UNSUPPORTED_ASSET_TYPE", message="등록한 파일 형식과 실제 업로드 형식이 다릅니다.")

        file_path = self._stored_file_path(asset)
        contents = file.file.read()
        if len(contents) == 0:
            raise AppError(status_code=400, error_code="EMPTY_ASSET_FILE", message="빈 파일은 업로드할 수 없습니다.")
        if len(contents) > 10 * 1024 * 1024:
            raise AppError(status_code=413, error_code="ASSET_TOO_LARGE", message="파일 크기가 제한을 초과했습니다.")

        file_path.write_bytes(contents)
        updated_at = now_utc()
        preview_url = f"{get_settings().public_api_base_url}/assets/{asset_id}/binary"
        db_repository.update_asset(
            asset_id,
            size_bytes=len(contents),
            status="uploaded",
            preview_url=preview_url,
            updated_at=updated_at,
        )
        audit_service.record(
            action="asset.upload_binary",
            resource_type="asset",
            resource_id=asset_id,
            context=context,
            merchant_id=asset["merchant_id"],
            metadata={"filename": asset["filename"], "size_bytes": len(contents)},
        )
        return AssetUploadBinaryResponse(
            asset_id=asset_id,
            status="uploaded",
            preview_url=preview_url,
            updated_at=updated_at,
        )

    def get(self, asset_id: str, context: RequestContext) -> AssetDetailResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_ASSET_ACCESS", message="자산 접근 권한이 없습니다.")

        asset = db_repository.get_asset(asset_id)
        if not asset:
            raise AppError(status_code=404, error_code="ASSET_NOT_FOUND", message="자산을 찾을 수 없습니다.")

        ensure_merchant_scope(context, asset["merchant_id"], error_code="FORBIDDEN_ASSET_ACCESS", message="자산 접근 권한이 없습니다.")

        return AssetDetailResponse(**asset)

    def get_binary(self, asset_id: str, context: RequestContext) -> FileResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_ASSET_ACCESS", message="자산 접근 권한이 없습니다.")
        asset = db_repository.get_asset(asset_id)
        if not asset:
            raise AppError(status_code=404, error_code="ASSET_NOT_FOUND", message="자산을 찾을 수 없습니다.")
        ensure_merchant_scope(context, asset["merchant_id"], error_code="FORBIDDEN_ASSET_ACCESS", message="자산 접근 권한이 없습니다.")
        file_path = self._stored_file_path(asset)
        if not file_path.exists():
            raise AppError(status_code=404, error_code="ASSET_FILE_NOT_FOUND", message="업로드된 파일을 찾을 수 없습니다.")
        return FileResponse(path=file_path, media_type=asset["content_type"], filename=asset["filename"])

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
        for asset in db_repository.list_assets():
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
