from enum import Enum


class CountryCode(str, Enum):
    JP = "JP"
    US = "US"
    CN = "CN"
    TW = "TW"
    HK = "HK"


class PlatformType(str, Enum):
    INSTAGRAM = "instagram"
    GOOGLE_BUSINESS = "google_business"
    XIAOHONGSHU = "xiaohongshu"
    BLOG = "blog"


class ContentGoal(str, Enum):
    STORE_VISIT = "store_visit"
    AWARENESS = "awareness"
    SEASONAL_PROMOTION = "seasonal_promotion"
    REVIEW_RESPONSE = "review_response"


class ToneType(str, Enum):
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    TRENDY = "trendy"
    CALM = "calm"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    REJECTED = "rejected"
    DELETED = "deleted"


class ReviewSensitivity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ImageVariantProvider(str, Enum):
    NONE = "none"
    NANO_BANANA = "nano_banana"
