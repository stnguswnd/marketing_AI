from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PublishResultModel(Base):
    __tablename__ = "publish_results"

    publish_result_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    content_id: Mapped[str] = mapped_column(String(64), index=True)
    channel: Mapped[str] = mapped_column(String(64), index=True)
    adapter_name: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), index=True)
    external_post_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    external_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publish_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_asset_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    variant_asset_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    image_variant_provider: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    caption_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
