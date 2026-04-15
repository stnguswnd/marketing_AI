from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Text, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ContentModel(Base):
    __tablename__ = "contents"

    content_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(64), index=True)
    target_country: Mapped[str] = mapped_column(String(8), index=True)
    platform: Mapped[str] = mapped_column(String(64), index=True)
    goal: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    hashtags_json: Mapped[str] = mapped_column(Text, default="[]")
    must_include_json: Mapped[str] = mapped_column(Text, default="[]")
    must_avoid_json: Mapped[str] = mapped_column(Text, default="[]")
    uploaded_asset_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    apply_image_variant: Mapped[bool] = mapped_column(Boolean, default=False)
    image_variant_provider: Mapped[str] = mapped_column(String(64), default="none")
    image_variant_job_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    publish_job_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    latest_publish_result_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    publish_result_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    variant_asset_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    approval_required: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
