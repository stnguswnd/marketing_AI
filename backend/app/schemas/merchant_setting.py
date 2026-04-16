from datetime import datetime

from pydantic import BaseModel, Field


class MerchantNanoBananaSettingRequest(BaseModel):
    merchant_id: str = Field(min_length=1)
    api_key: str = Field(min_length=1, max_length=255)


class MerchantNanoBananaSettingResponse(BaseModel):
    merchant_id: str
    has_api_key: bool
    masked_api_key: str | None = None
    updated_at: datetime | None = None
