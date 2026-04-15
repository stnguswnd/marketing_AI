from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Request

from app.core.errors import AppError


@dataclass(frozen=True)
class RequestContext:
    role: str
    user_id: Optional[str]
    merchant_id: Optional[str]
    request_id: Optional[str]


def _read_header(request: Request, *names: str) -> Optional[str]:
    for name in names:
        value = request.headers.get(name)
        if value:
            return value
    return None


def get_request_context(request: Request) -> RequestContext:
    role = _read_header(request, "X-Test-Role", "X-Role") or "anonymous"
    user_id = _read_header(request, "X-Test-User-Id", "X-Actor-Id")
    merchant_id = _read_header(request, "X-Test-Merchant-Id", "X-Merchant-Id")
    request_id = getattr(request.state, "request_id", None)
    return RequestContext(role=role, user_id=user_id, merchant_id=merchant_id, request_id=request_id)


def require_roles(*roles: str):
    def dependency(context: RequestContext = Depends(get_request_context)) -> RequestContext:
        if context.role not in roles:
            raise AppError(status_code=403, error_code="FORBIDDEN", message="권한이 없습니다.")
        return context

    return dependency


def verify_webhook_secret(request: Request) -> None:
    secret = _read_header(request, "X-Webhook-Secret", "X-Webhook-Token", "X-Test-Webhook-Token")
    if secret not in {"test-secret", "dev-webhook-secret"}:
        raise AppError(
            status_code=401,
            error_code="INVALID_WEBHOOK_SIGNATURE",
            message="유효하지 않은 webhook 서명입니다.",
        )
