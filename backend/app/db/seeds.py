from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.membership import MembershipModel
from app.models.merchant import MerchantModel
from app.models.user import UserModel


@dataclass(frozen=True)
class SeedUser:
    user_id: str
    email: str
    display_name: str
    role: str
    profile_image_url: str


@dataclass(frozen=True)
class SeedMerchant:
    merchant_id: str
    name: str
    slug: str
    business_category: str
    profile_image_url: str
    description: str


@dataclass(frozen=True)
class SeedMembership:
    membership_id: str
    user_id: str
    merchant_id: str
    membership_role: str


def _now() -> datetime:
    return datetime.now(timezone.utc)


def build_seed_blueprint() -> tuple[list[SeedUser], list[SeedMerchant], list[SeedMembership]]:
    users = [
        SeedUser(
            user_id="user_admin_001",
            email="test1@email.com",
            display_name="테스트 관리자 1",
            role="admin",
            profile_image_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
        ),
        SeedUser(
            user_id="user_merchant_002",
            email="test2@email.com",
            display_name="테스트 점주 2",
            role="merchant",
            profile_image_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
        ),
        SeedUser(
            user_id="user_merchant_003",
            email="test3@email.com",
            display_name="테스트 점주 3",
            role="merchant",
            profile_image_url="https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=400&q=80",
        ),
        SeedUser(
            user_id="user_merchant_004",
            email="test4@email.com",
            display_name="테스트 점주 4",
            role="merchant",
            profile_image_url="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=400&q=80",
        ),
    ]
    merchants = [
        SeedMerchant(
            merchant_id="m_002",
            name="테스트 카페 2",
            slug="test-cafe-2",
            business_category="cafe",
            profile_image_url="https://images.unsplash.com/photo-1445116572660-236099ec97a0?auto=format&fit=crop&w=640&q=80",
            description="벚꽃 시즌 디저트를 강조하는 테스트 카페 계정입니다.",
        ),
        SeedMerchant(
            merchant_id="m_003",
            name="테스트 베이커리 3",
            slug="test-bakery-3",
            business_category="bakery",
            profile_image_url="https://images.unsplash.com/photo-1517433670267-08bbd4be890f?auto=format&fit=crop&w=640&q=80",
            description="해외 관광객 대상 베이커리 마케팅 테스트 점포입니다.",
        ),
        SeedMerchant(
            merchant_id="m_004",
            name="테스트 식당 4",
            slug="test-restaurant-4",
            business_category="restaurant",
            profile_image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=640&q=80",
            description="리뷰 대응과 발행 테스트를 위한 식당 점포입니다.",
        ),
    ]
    memberships = [
        SeedMembership(
            membership_id="membership_002",
            user_id="user_merchant_002",
            merchant_id="m_002",
            membership_role="owner",
        ),
        SeedMembership(
            membership_id="membership_003",
            user_id="user_merchant_003",
            merchant_id="m_003",
            membership_role="owner",
        ),
        SeedMembership(
            membership_id="membership_004",
            user_id="user_merchant_004",
            merchant_id="m_004",
            membership_role="owner",
        ),
    ]
    return users, merchants, memberships


def _upsert_users(session: Session, users: Iterable[SeedUser], password: str) -> None:
    now = _now()
    for seed in users:
        existing = session.scalar(select(UserModel).where(UserModel.email == seed.email))
        if existing:
            existing.display_name = seed.display_name
            existing.role = seed.role
            existing.profile_image_url = seed.profile_image_url
            existing.password_hash = hash_password(password)
            existing.updated_at = now
            continue

        session.add(
            UserModel(
                user_id=seed.user_id,
                email=seed.email,
                password_hash=hash_password(password),
                display_name=seed.display_name,
                role=seed.role,
                profile_image_url=seed.profile_image_url,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )


def _upsert_merchants(session: Session, merchants: Iterable[SeedMerchant]) -> None:
    now = _now()
    for seed in merchants:
        existing = session.get(MerchantModel, seed.merchant_id)
        if existing:
            existing.name = seed.name
            existing.slug = seed.slug
            existing.business_category = seed.business_category
            existing.profile_image_url = seed.profile_image_url
            existing.description = seed.description
            existing.updated_at = now
            continue

        session.add(
            MerchantModel(
                merchant_id=seed.merchant_id,
                name=seed.name,
                slug=seed.slug,
                country_code="KR",
                business_category=seed.business_category,
                profile_image_url=seed.profile_image_url,
                description=seed.description,
                created_at=now,
                updated_at=now,
            )
        )


def _upsert_memberships(session: Session, memberships: Iterable[SeedMembership]) -> None:
    now = _now()
    for seed in memberships:
        existing = session.get(MembershipModel, seed.membership_id)
        if existing:
            existing.user_id = seed.user_id
            existing.merchant_id = seed.merchant_id
            existing.membership_role = seed.membership_role
            existing.updated_at = now
            continue

        session.add(
            MembershipModel(
                membership_id=seed.membership_id,
                user_id=seed.user_id,
                merchant_id=seed.merchant_id,
                membership_role=seed.membership_role,
                created_at=now,
                updated_at=now,
            )
        )


def seed_mock_data(session: Session, password: str = "12345678") -> None:
    users, merchants, memberships = build_seed_blueprint()
    _upsert_users(session, users, password)
    _upsert_merchants(session, merchants)
    session.flush()
    _upsert_memberships(session, memberships)
    session.commit()
