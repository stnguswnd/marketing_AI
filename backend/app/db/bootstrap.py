from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.models import AssetModel, AuditLogModel, ContentModel, JobModel, MerchantModel, MembershipModel, RequestLogModel, UserModel


def create_database_schema() -> None:
    Base.metadata.create_all(bind=engine)


def reset_database_schema() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def ping_database(session: Session) -> None:
    session.execute(text("SELECT 1"))
