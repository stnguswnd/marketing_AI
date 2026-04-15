from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import ImageVariantProvider, PlatformType


class PublishResultResponse(BaseModel):
    publish_result_id: str
    content_id: str
    channel: PlatformType
    adapter_name: str
    status: str
    external_post_id: Optional[str] = None
    external_url: Optional[str] = None
    publish_at: Optional[datetime] = None
    source_asset_ids: list[str] = Field(default_factory=list)
    variant_asset_ids: list[str] = Field(default_factory=list)
    image_variant_provider: Optional[ImageVariantProvider] = None
    thumbnail_url: Optional[str] = None
    title: Optional[str] = None
    caption_preview: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PublishResultListItemResponse(BaseModel):
    publish_result_id: str
    content_id: str
    channel: PlatformType
    adapter_name: str
    status: str
    external_post_id: Optional[str] = None
    external_url: Optional[str] = None
    publish_at: Optional[datetime] = None
    thumbnail_url: Optional[str] = None
    title: Optional[str] = None
    caption_preview: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PublishResultListResponse(BaseModel):
    items: list[PublishResultListItemResponse]
