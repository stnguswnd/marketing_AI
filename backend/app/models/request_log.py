from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RequestLogModel(Base):
    __tablename__ = "request_logs"

    request_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    method: Mapped[str] = mapped_column(String(16))
    path: Mapped[str] = mapped_column(String(255), index=True)
    status_code: Mapped[int] = mapped_column(Integer, index=True)
    duration_ms: Mapped[int] = mapped_column(Integer)
    actor_role: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    actor_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    merchant_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
