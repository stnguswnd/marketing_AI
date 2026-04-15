from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from app.core.errors import AppError
from app.core.security import hash_password, verify_password
from app.db.session import SessionLocal
from app.models.membership import MembershipModel
from app.models.merchant import MerchantModel
from app.models.user import UserModel
from app.schemas.auth import AuthSessionResponse, LoginRequest, TestAccountListResponse, TestAccountResponse


def _fallback_accounts() -> list[dict[str, str | None]]:
    return [
        {
            "user_id": "user_admin_001",
            "email": "test1@email.com",
            "display_name": "테스트 관리자 1",
            "role": "admin",
            "merchant_id": None,
            "merchant_name": None,
            "profile_image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
            "password_hash": hash_password("12345678"),
        },
        {
            "user_id": "user_merchant_002",
            "email": "test2@email.com",
            "display_name": "테스트 점주 2",
            "role": "merchant",
            "merchant_id": "m_002",
            "merchant_name": "테스트 카페 2",
            "profile_image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
            "password_hash": hash_password("12345678"),
        },
        {
            "user_id": "user_merchant_003",
            "email": "test3@email.com",
            "display_name": "테스트 점주 3",
            "role": "merchant",
            "merchant_id": "m_003",
            "merchant_name": "테스트 베이커리 3",
            "profile_image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=400&q=80",
            "password_hash": hash_password("12345678"),
        },
        {
            "user_id": "user_merchant_004",
            "email": "test4@email.com",
            "display_name": "테스트 점주 4",
            "role": "merchant",
            "merchant_id": "m_004",
            "merchant_name": "테스트 식당 4",
            "profile_image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=400&q=80",
            "password_hash": hash_password("12345678"),
        },
    ]


class AuthService:
    def _login_from_fallback(self, payload: LoginRequest) -> AuthSessionResponse:
        for account in _fallback_accounts():
            if account["email"] != payload.email:
                continue
            if not verify_password(payload.password, str(account["password_hash"])):
                break
            return AuthSessionResponse(
                user_id=str(account["user_id"]),
                email=str(account["email"]),
                display_name=str(account["display_name"]),
                role=str(account["role"]),
                merchant_id=account["merchant_id"],
                merchant_name=account["merchant_name"],
                profile_image_url=str(account["profile_image_url"]),
            )
        raise AppError(status_code=401, error_code="INVALID_CREDENTIALS", message="이메일 또는 비밀번호가 올바르지 않습니다.")

    def _list_fallback_accounts(self) -> TestAccountListResponse:
        return TestAccountListResponse(
            items=[
                TestAccountResponse(
                    email=str(account["email"]),
                    display_name=str(account["display_name"]),
                    role=str(account["role"]),
                    merchant_id=account["merchant_id"],
                    merchant_name=account["merchant_name"],
                    profile_image_url=str(account["profile_image_url"]),
                )
                for account in _fallback_accounts()
            ]
        )

    def login(self, payload: LoginRequest) -> AuthSessionResponse:
        try:
            with SessionLocal() as session:
                user = session.scalar(select(UserModel).where(UserModel.email == payload.email))
                if not user or not verify_password(payload.password, user.password_hash):
                    raise AppError(status_code=401, error_code="INVALID_CREDENTIALS", message="이메일 또는 비밀번호가 올바르지 않습니다.")

                merchant_id = None
                merchant_name = None
                if user.role == "merchant":
                    membership = session.scalar(select(MembershipModel).where(MembershipModel.user_id == user.user_id))
                    if membership is None:
                        raise AppError(status_code=403, error_code="MERCHANT_MEMBERSHIP_NOT_FOUND", message="점주 계정에 연결된 점포가 없습니다.")
                    merchant = session.get(MerchantModel, membership.merchant_id)
                    merchant_id = membership.merchant_id
                    merchant_name = merchant.name if merchant else None

                return AuthSessionResponse(
                    user_id=user.user_id,
                    email=user.email,
                    display_name=user.display_name,
                    role=user.role,
                    merchant_id=merchant_id,
                    merchant_name=merchant_name,
                    profile_image_url=user.profile_image_url,
                )
        except OperationalError:
            return self._login_from_fallback(payload)

    def list_test_accounts(self) -> TestAccountListResponse:
        try:
            with SessionLocal() as session:
                users = session.scalars(select(UserModel).order_by(UserModel.email)).all()
                items: list[TestAccountResponse] = []
                for user in users:
                    merchant_id = None
                    merchant_name = None
                    if user.role == "merchant":
                        membership = session.scalar(select(MembershipModel).where(MembershipModel.user_id == user.user_id))
                        if membership is not None:
                            merchant = session.get(MerchantModel, membership.merchant_id)
                            merchant_id = membership.merchant_id
                            merchant_name = merchant.name if merchant else None
                    items.append(
                        TestAccountResponse(
                            email=user.email,
                            display_name=user.display_name,
                            role=user.role,
                            merchant_id=merchant_id,
                            merchant_name=merchant_name,
                            profile_image_url=user.profile_image_url,
                        )
                    )
                return TestAccountListResponse(items=items)
        except OperationalError:
            return self._list_fallback_accounts()


auth_service = AuthService()
