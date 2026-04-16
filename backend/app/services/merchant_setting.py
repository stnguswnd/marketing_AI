from __future__ import annotations

from datetime import datetime, timezone

from app.core.auth import RequestContext
from app.core.settings import get_settings
from app.core.permissions import ensure_authenticated_actor, ensure_merchant_scope, ensure_roles
from app.repositories.database import db_repository
from app.schemas.merchant_setting import MerchantNanoBananaSettingRequest, MerchantNanoBananaSettingResponse
from app.services.audit import audit_service


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def mask_secret(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 4:
        return "*" * len(value)
    return "*" * (len(value) - 4) + value[-4:]


class MerchantSettingService:
    def get_nano_banana_api_key(self, merchant_id: str) -> str:
        setting = db_repository.get_merchant_setting(merchant_id)
        if setting and setting.get("nano_banana_api_key"):
            return str(setting["nano_banana_api_key"])
        settings = get_settings()
        if settings.nano_banana_api_key:
            return settings.nano_banana_api_key
        if settings.app_env == "test":
            return "nano_banana_test_key"
        return ""

    def get_nano_banana_setting(
        self,
        merchant_id: str,
        context: RequestContext,
    ) -> MerchantNanoBananaSettingResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_MERCHANT_SETTINGS")
        ensure_authenticated_actor(context)
        ensure_merchant_scope(context, merchant_id, error_code="FORBIDDEN_MERCHANT_SETTINGS")

        setting = db_repository.get_merchant_setting(merchant_id)
        return MerchantNanoBananaSettingResponse(
            merchant_id=merchant_id,
            has_api_key=bool(setting and setting.get("nano_banana_api_key")),
            masked_api_key=mask_secret(setting.get("nano_banana_api_key") if setting else None),
            updated_at=setting.get("updated_at") if setting else None,
        )

    def save_nano_banana_setting(
        self,
        payload: MerchantNanoBananaSettingRequest,
        context: RequestContext,
    ) -> MerchantNanoBananaSettingResponse:
        ensure_roles(context, "merchant", "operator", "admin", error_code="FORBIDDEN_MERCHANT_SETTINGS")
        ensure_authenticated_actor(context)
        ensure_merchant_scope(context, payload.merchant_id, error_code="FORBIDDEN_MERCHANT_SETTINGS")

        updated_at = now_utc()
        setting = db_repository.upsert_merchant_setting(
            merchant_id=payload.merchant_id,
            nano_banana_api_key=payload.api_key,
            updated_at=updated_at,
        )
        audit_service.record(
            action="merchant_setting.nano_banana.save",
            resource_type="merchant_setting",
            resource_id=payload.merchant_id,
            context=context,
            merchant_id=payload.merchant_id,
            metadata={"provider": "nano_banana", "has_api_key": True},
        )
        return MerchantNanoBananaSettingResponse(
            merchant_id=payload.merchant_id,
            has_api_key=True,
            masked_api_key=mask_secret(setting.get("nano_banana_api_key")),
            updated_at=setting.get("updated_at"),
        )


merchant_setting_service = MerchantSettingService()
