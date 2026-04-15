from __future__ import annotations

from app.core.auth import RequestContext
from app.core.errors import AppError


def ensure_roles(context: RequestContext, *roles: str, error_code: str = "FORBIDDEN", message: str = "권한이 없습니다.") -> None:
    if context.role not in roles:
        raise AppError(status_code=403, error_code=error_code, message=message)


def ensure_authenticated_actor(
    context: RequestContext,
    error_code: str = "AUTHENTICATION_REQUIRED",
    message: str = "인증된 사용자 정보가 필요합니다.",
) -> None:
    if not context.user_id:
        raise AppError(status_code=401, error_code=error_code, message=message)


def ensure_merchant_scope(
    context: RequestContext,
    merchant_id: str,
    error_code: str = "FORBIDDEN_MERCHANT_ACCESS",
    message: str = "점포 접근 권한이 없습니다.",
) -> None:
    if context.role == "merchant" and context.merchant_id != merchant_id:
        raise AppError(status_code=403, error_code=error_code, message=message)
