from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MembershipModel(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "merchant_id", name="uq_membership_user_merchant"),)

    membership_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.merchant_id", ondelete="CASCADE"), index=True)
    membership_role: Mapped[str] = mapped_column(String(32), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
