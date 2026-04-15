from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MerchantModel(Base):
    __tablename__ = "merchants"

    merchant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    country_code: Mapped[str] = mapped_column(String(8), default="KR")
    business_category: Mapped[str] = mapped_column(String(128))
    profile_image_url: Mapped[str] = mapped_column(String(512))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
