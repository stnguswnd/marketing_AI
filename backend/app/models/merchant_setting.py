from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MerchantSettingModel(Base):
    __tablename__ = "merchant_settings"

    merchant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nano_banana_api_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
