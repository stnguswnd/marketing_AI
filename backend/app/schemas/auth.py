from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class AuthSessionResponse(BaseModel):
    user_id: str
    email: str
    display_name: str
    role: str
    merchant_id: Optional[str] = None
    merchant_name: Optional[str] = None
    profile_image_url: str


class TestAccountResponse(BaseModel):
    email: str
    display_name: str
    role: str
    merchant_id: Optional[str] = None
    merchant_name: Optional[str] = None
    profile_image_url: str


class TestAccountListResponse(BaseModel):
    items: list[TestAccountResponse]
