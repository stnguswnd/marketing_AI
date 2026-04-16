from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.common import (
    ContentGoal,
    ContentStatus,
    CountryCode,
    ImageVariantProvider,
    PlatformType,
    ToneType,
)


class ContentGenerateRequest(BaseModel):
    merchant_id: str = Field(min_length=1)
    target_country: CountryCode
    platform: PlatformType
    goal: ContentGoal
    input_brief: str = Field(min_length=10, max_length=500)
    website_url: Optional[HttpUrl] = None
    tone: Optional[ToneType] = None
    must_include: list[str] = Field(default_factory=list, max_length=10)
    must_avoid: list[str] = Field(default_factory=list, max_length=10)
    uploaded_asset_ids: list[str] = Field(default_factory=list, max_length=5)
    apply_image_variant: bool = False
    image_variant_provider: ImageVariantProvider = ImageVariantProvider.NONE
    publish_mode: str = Field(pattern="^draft$")


class ContentGenerateResponse(BaseModel):
    content_id: str
    merchant_id: str
    status: ContentStatus
    approval_required: bool
    job_id: str
    message: str
    image_variant_job_id: Optional[str] = None
    variant_asset_ids: list[str] = Field(default_factory=list)


class ContentDetailResponse(BaseModel):
    content_id: str
    merchant_id: str
    target_country: CountryCode
    platform: PlatformType
    goal: ContentGoal
    status: ContentStatus
    title: str
    body: str
    hashtags: list[str]
    must_include: list[str]
    must_avoid: list[str]
    uploaded_asset_ids: list[str]
    apply_image_variant: bool
    image_variant_provider: ImageVariantProvider
    image_variant_job_id: Optional[str] = None
    selected_variant_asset_id: Optional[str] = None
    overlay_headline: Optional[str] = None
    overlay_subheadline: Optional[str] = None
    overlay_cta: Optional[str] = None
    publish_job_id: Optional[str] = None
    latest_publish_result_id: Optional[str] = None
    publish_result_ids: list[str] = Field(default_factory=list)
    variant_asset_ids: list[str] = Field(default_factory=list)
    approval_required: bool
    created_at: datetime
    updated_at: datetime


class ContentApproveRequest(BaseModel):
    approver_id: str = Field(min_length=1)
    comment: Optional[str] = None


class ContentRejectRequest(BaseModel):
    reviewer_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class ContentPublishRequest(BaseModel):
    publish_at: Optional[datetime] = None
    apply_image_variant: bool = False
    image_variant_provider: ImageVariantProvider = ImageVariantProvider.NONE
    source_asset_ids: list[str] = Field(default_factory=list, max_length=5)
    selected_variant_asset_id: Optional[str] = None


class ContentOverlayUpdateRequest(BaseModel):
    selected_variant_asset_id: Optional[str] = None
    overlay_headline: Optional[str] = Field(default=None, max_length=255)
    overlay_subheadline: Optional[str] = Field(default=None, max_length=1000)
    overlay_cta: Optional[str] = Field(default=None, max_length=255)


class ContentImageRegenerateRequest(BaseModel):
    source_asset_ids: list[str] = Field(default_factory=list, max_length=5)


class ContentOverlayResponse(BaseModel):
    content_id: str
    selected_variant_asset_id: Optional[str] = None
    overlay_headline: Optional[str] = None
    overlay_subheadline: Optional[str] = None
    overlay_cta: Optional[str] = None
    image_variant_job_id: Optional[str] = None
    variant_asset_ids: list[str] = Field(default_factory=list)


class ContentStatusChangeResponse(BaseModel):
    content_id: str
    status: ContentStatus
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    reason: Optional[str] = None


class ContentPublishResponse(BaseModel):
    content_id: str
    status: ContentStatus
    job_id: str
    publish_at: Optional[datetime] = None
    image_variant_job_id: Optional[str] = None
    image_variant_provider: Optional[ImageVariantProvider] = None
    publish_result_id: Optional[str] = None


class ContentDeleteResponse(BaseModel):
    content_id: str
    deleted: bool
    message: str


class ContentListItemResponse(BaseModel):
    content_id: str
    merchant_id: str
    target_country: CountryCode
    platform: PlatformType
    goal: ContentGoal
    status: ContentStatus
    apply_image_variant: bool
    image_variant_provider: ImageVariantProvider
    variant_asset_ids: list[str] = Field(default_factory=list)
    latest_publish_result_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ContentListResponse(BaseModel):
    items: list[ContentListItemResponse]
