from __future__ import annotations

from datetime import datetime, timezone

from app.repositories.memory import repository
from app.schemas.common import ContentStatus, CountryCode, PlatformType, ReviewStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


def seed_demo_repository() -> None:
    if repository.contents:
        return

    now = _now()
    demo_assets = [
        {
            "asset_id": "asset_demo_002",
            "merchant_id": "m_002",
            "filename": "matcha-latte.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 420000,
            "asset_type": "source",
            "status": "uploaded",
            "provider": None,
            "generated_by_job_id": None,
            "source_asset_ids": [],
            "preview_url": "https://images.unsplash.com/photo-1515823064-d6e0c04616a7?auto=format&fit=crop&w=1200&q=80",
            "created_at": now,
            "updated_at": now,
        },
        {
            "asset_id": "asset_demo_003",
            "merchant_id": "m_003",
            "filename": "bakery-window.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 390000,
            "asset_type": "source",
            "status": "uploaded",
            "provider": None,
            "generated_by_job_id": None,
            "source_asset_ids": [],
            "preview_url": "https://images.unsplash.com/photo-1517433670267-08bbd4be890f?auto=format&fit=crop&w=1200&q=80",
            "created_at": now,
            "updated_at": now,
        },
        {
            "asset_id": "asset_demo_004",
            "merchant_id": "m_004",
            "filename": "restaurant-table.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 410000,
            "asset_type": "source",
            "status": "uploaded",
            "provider": None,
            "generated_by_job_id": None,
            "source_asset_ids": [],
            "preview_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80",
            "created_at": now,
            "updated_at": now,
        },
    ]
    for asset in demo_assets:
        repository.assets[asset["asset_id"]] = asset

    demo_contents = [
        {
            "content_id": "content_demo_002",
            "merchant_id": "m_002",
            "target_country": CountryCode.JP,
            "platform": PlatformType.INSTAGRAM,
            "goal": "store_visit",
            "status": ContentStatus.PUBLISHED,
            "title": "벚꽃 시즌 부산 카페 스팟",
            "body": "벚꽃 시즌 부산 여행 중이라면 말차라떼와 푸딩이 있는 테스트 카페 2를 들러보세요. 부드러운 말차 향과 창가석 무드가 일본 관광객에게 잘 맞는 톤으로 정리된 예시 포스팅입니다.",
            "hashtags": ["#부산카페", "#말차라떼", "#벚꽃여행"],
            "must_include": ["말차라떼", "부산 여행"],
            "must_avoid": ["최고", "무조건"],
            "uploaded_asset_ids": ["asset_demo_002"],
            "apply_image_variant": False,
            "image_variant_provider": "none",
            "image_variant_job_id": None,
            "publish_job_id": "job_demo_publish_002",
            "latest_publish_result_id": "publish_demo_002",
            "publish_result_ids": ["publish_demo_002"],
            "variant_asset_ids": [],
            "approval_required": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "content_id": "content_demo_003",
            "merchant_id": "m_003",
            "target_country": CountryCode.US,
            "platform": PlatformType.BLOG,
            "goal": "awareness",
            "status": ContentStatus.PUBLISHED,
            "title": "Busan bakery morning route",
            "body": "Fresh baked salt bread, butter scent, and an easy morning route for visitors staying near the station. This is a seeded blog-style sample post for merchant 3.",
            "hashtags": ["#busanbakery", "#morningroute", "#saltbread"],
            "must_include": ["salt bread", "Busan"],
            "must_avoid": ["best ever"],
            "uploaded_asset_ids": ["asset_demo_003"],
            "apply_image_variant": True,
            "image_variant_provider": "nano_banana",
            "image_variant_job_id": "job_demo_variant_003",
            "publish_job_id": "job_demo_publish_003",
            "latest_publish_result_id": "publish_demo_003",
            "publish_result_ids": ["publish_demo_003"],
            "variant_asset_ids": ["asset_variant_demo_003"],
            "approval_required": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "content_id": "content_demo_004",
            "merchant_id": "m_004",
            "target_country": CountryCode.HK,
            "platform": PlatformType.GOOGLE_BUSINESS,
            "goal": "review_response",
            "status": ContentStatus.APPROVED,
            "title": "Late-night seafood stop in Busan",
            "body": "Sample approved copy for merchant 4 showing how a ready-to-publish post looks before the owner triggers publish.",
            "hashtags": ["#부산맛집", "#야식코스", "#해산물"],
            "must_include": ["Busan", "seafood"],
            "must_avoid": ["no.1"],
            "uploaded_asset_ids": ["asset_demo_004"],
            "apply_image_variant": False,
            "image_variant_provider": "none",
            "image_variant_job_id": None,
            "publish_job_id": None,
            "latest_publish_result_id": None,
            "publish_result_ids": [],
            "variant_asset_ids": [],
            "approval_required": True,
            "created_at": now,
            "updated_at": now,
        },
    ]
    for content in demo_contents:
        repository.contents[content["content_id"]] = content

    repository.assets["asset_variant_demo_003"] = {
        "asset_id": "asset_variant_demo_003",
        "merchant_id": "m_003",
        "filename": "bakery-window-variant.jpg",
        "content_type": "image/jpeg",
        "size_bytes": 310000,
        "asset_type": "variant",
        "status": "generated",
        "provider": "nano_banana",
        "generated_by_job_id": "job_demo_variant_003",
        "source_asset_ids": ["asset_demo_003"],
        "preview_url": "https://images.unsplash.com/photo-1483695028939-5bb13f8648b0?auto=format&fit=crop&w=1200&q=80",
        "created_at": now,
        "updated_at": now,
    }

    publish_results = [
        {
            "publish_result_id": "publish_demo_002",
            "content_id": "content_demo_002",
            "channel": PlatformType.INSTAGRAM,
            "adapter_name": "instagram_stub",
            "status": "published",
            "external_post_id": "ig_demo_002",
            "external_url": "https://instagram.com/p/demo-002",
            "publish_at": now,
            "source_asset_ids": ["asset_demo_002"],
            "variant_asset_ids": [],
            "image_variant_provider": "none",
            "thumbnail_url": "https://images.unsplash.com/photo-1515823064-d6e0c04616a7?auto=format&fit=crop&w=1200&q=80",
            "title": "벚꽃 시즌 부산 카페 스팟",
            "caption_preview": "말차라떼와 푸딩이 있는 부산 여행 코스를 일본 관광객 대상 톤으로 정리한 예시 포스팅",
            "created_at": now,
            "updated_at": now,
        },
        {
            "publish_result_id": "publish_demo_003",
            "content_id": "content_demo_003",
            "channel": PlatformType.BLOG,
            "adapter_name": "blog_stub",
            "status": "published",
            "external_post_id": "blog_demo_003",
            "external_url": "https://blog.example.com/posts/demo-003",
            "publish_at": now,
            "source_asset_ids": ["asset_demo_003"],
            "variant_asset_ids": ["asset_variant_demo_003"],
            "image_variant_provider": "nano_banana",
            "thumbnail_url": "https://images.unsplash.com/photo-1517433670267-08bbd4be890f?auto=format&fit=crop&w=1200&q=80",
            "title": "Busan bakery morning route",
            "caption_preview": "salt bread 중심으로 관광객용 morning route를 소개하는 블로그 예시",
            "created_at": now,
            "updated_at": now,
        },
    ]
    for result in publish_results:
        repository.publish_results[result["publish_result_id"]] = result

    repository.reviews["review_demo_004"] = {
        "review_id": "review_demo_004",
        "merchant_id": "m_004",
        "platform": PlatformType.GOOGLE_BUSINESS,
        "rating": 2,
        "language": "ja",
        "review_text": "해산물은 좋았지만 대기 시간이 길었습니다.",
        "sensitivity": "medium",
        "status": ReviewStatus.DRAFT,
        "reply_draft": "기다리게 해드려 죄송합니다. 다음 방문 때 더 나은 경험을 드릴 수 있도록 개선하겠습니다.",
        "escalated": True,
        "created_at": now,
    }

    repository.jobs["job_demo_publish_002"] = {
        "job_id": "job_demo_publish_002",
        "job_type": "content_publish",
        "status": "succeeded",
        "resource_type": "content",
        "resource_id": "content_demo_002",
        "created_at": now,
        "updated_at": now,
    }
    repository.jobs["job_demo_publish_003"] = {
        "job_id": "job_demo_publish_003",
        "job_type": "content_publish",
        "status": "succeeded",
        "resource_type": "content",
        "resource_id": "content_demo_003",
        "created_at": now,
        "updated_at": now,
    }
    repository.jobs["job_demo_variant_003"] = {
        "job_id": "job_demo_variant_003",
        "job_type": "image_variant_generate",
        "status": "succeeded",
        "resource_type": "content",
        "resource_id": "content_demo_003",
        "created_at": now,
        "updated_at": now,
    }
    repository.reports["report_demo_002"] = {
        "report_id": "report_demo_002",
        "scope_type": "merchant",
        "scope_id": "m_002",
        "year": 2026,
        "month": 4,
        "status": "succeeded",
        "created_at": now,
    }
