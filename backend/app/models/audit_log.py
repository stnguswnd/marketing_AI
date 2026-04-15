from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    audit_log_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    actor_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    actor_role: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    merchant_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(128), index=True)
    resource_type: Mapped[str] = mapped_column(String(64), index=True)
    resource_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32))
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
