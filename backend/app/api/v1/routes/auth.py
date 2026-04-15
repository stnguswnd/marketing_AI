from fastapi import APIRouter

from app.schemas.auth import AuthSessionResponse, LoginRequest, TestAccountListResponse
from app.services.auth import auth_service


router = APIRouter(prefix="/auth")


@router.post("/login", response_model=AuthSessionResponse)
def login(payload: LoginRequest) -> AuthSessionResponse:
    return auth_service.login(payload)


@router.get("/test-accounts", response_model=TestAccountListResponse)
def list_test_accounts() -> TestAccountListResponse:
    return auth_service.list_test_accounts()
