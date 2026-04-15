from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AssetModel(Base):
    __tablename__ = "assets"

    asset_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(64), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(128))
    size_bytes: Mapped[int] = mapped_column(Integer)
    asset_type: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    provider: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    generated_by_job_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    source_asset_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
