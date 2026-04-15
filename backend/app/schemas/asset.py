from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AssetUploadInitRequest(BaseModel):
    merchant_id: str = Field(min_length=1)
    filename: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    size_bytes: int = Field(gt=0, le=10 * 1024 * 1024)


class AssetUploadInitResponse(BaseModel):
    asset_id: str
    upload_url: str
    asset_type: str


class AssetDetailResponse(BaseModel):
    asset_id: str
    merchant_id: str
    filename: str
    content_type: str
    size_bytes: int
    asset_type: str
    status: str
    provider: Optional[str] = None
    generated_by_job_id: Optional[str] = None
    source_asset_ids: list[str] = Field(default_factory=list)
    preview_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AssetListItemResponse(BaseModel):
    asset_id: str
    merchant_id: str
    filename: str
    content_type: str
    size_bytes: int
    asset_type: str
    status: str
    provider: Optional[str] = None
    generated_by_job_id: Optional[str] = None
    source_asset_ids: list[str] = Field(default_factory=list)
    preview_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AssetListResponse(BaseModel):
    items: list[AssetListItemResponse]
