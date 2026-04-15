from __future__ import annotations

import json
from contextlib import contextmanager
from enum import Enum
from typing import Any, Iterator, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.asset import AssetModel
from app.models.audit_log import AuditLogModel
from app.models.content import ContentModel
from app.models.job import JobModel
from app.models.publish_result import PublishResultModel
from app.models.report import ReportModel
from app.models.request_log import RequestLogModel
from app.models.review import ReviewModel


def _normalize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _normalize_value(item) for key, item in value.items()}
    return value


def _as_json(value: Any) -> str:
    return json.dumps(_normalize_value(value), ensure_ascii=False)


def _from_json_list(value: Optional[str]) -> list[Any]:
    if not value:
        return []
    return json.loads(value)


def _from_json_dict(value: Optional[str]) -> dict[str, Any]:
    if not value:
        return {}
    return json.loads(value)


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class DatabaseRepository:
    def _asset_to_dict(self, model: AssetModel) -> dict[str, Any]:
        return {
            "asset_id": model.asset_id,
            "merchant_id": model.merchant_id,
            "filename": model.filename,
            "content_type": model.content_type,
            "size_bytes": model.size_bytes,
            "asset_type": model.asset_type,
            "status": model.status,
            "provider": model.provider,
            "generated_by_job_id": model.generated_by_job_id,
            "source_asset_ids": _from_json_list(model.source_asset_ids_json),
            "preview_url": model.preview_url,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }

    def _content_to_dict(self, model: ContentModel) -> dict[str, Any]:
        return {
            "content_id": model.content_id,
            "merchant_id": model.merchant_id,
            "target_country": model.target_country,
            "platform": model.platform,
            "goal": model.goal,
            "status": model.status,
            "title": model.title,
            "body": model.body,
            "hashtags": _from_json_list(model.hashtags_json),
            "must_include": _from_json_list(model.must_include_json),
            "must_avoid": _from_json_list(model.must_avoid_json),
            "uploaded_asset_ids": _from_json_list(model.uploaded_asset_ids_json),
            "apply_image_variant": model.apply_image_variant,
            "image_variant_provider": model.image_variant_provider,
            "image_variant_job_id": model.image_variant_job_id,
            "publish_job_id": model.publish_job_id,
            "latest_publish_result_id": model.latest_publish_result_id,
            "publish_result_ids": _from_json_list(model.publish_result_ids_json),
            "variant_asset_ids": _from_json_list(model.variant_asset_ids_json),
            "approval_required": model.approval_required,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }

    def _review_to_dict(self, model: ReviewModel) -> dict[str, Any]:
        return {
            "review_id": model.review_id,
            "merchant_id": model.merchant_id,
            "platform": model.platform,
            "rating": model.rating,
            "language": model.language,
            "review_text": model.review_text,
            "sensitivity": model.sensitivity,
            "status": model.status,
            "reply_draft": model.reply_draft,
            "escalated": model.escalated,
            "created_at": model.created_at,
        }

    def _report_to_dict(self, model: ReportModel) -> dict[str, Any]:
        return {
            "report_id": model.report_id,
            "scope_type": model.scope_type,
            "scope_id": model.scope_id,
            "year": model.year,
            "month": model.month,
            "status": model.status,
            "created_at": model.created_at,
        }

    def _job_to_dict(self, model: JobModel) -> dict[str, Any]:
        return {
            "job_id": model.job_id,
            "job_type": model.job_type,
            "status": model.status,
            "resource_type": model.resource_type,
            "resource_id": model.resource_id,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }

    def _publish_result_to_dict(self, model: PublishResultModel) -> dict[str, Any]:
        return {
            "publish_result_id": model.publish_result_id,
            "content_id": model.content_id,
            "channel": model.channel,
            "adapter_name": model.adapter_name,
            "status": model.status,
            "external_post_id": model.external_post_id,
            "external_url": model.external_url,
            "publish_at": model.publish_at,
            "source_asset_ids": _from_json_list(model.source_asset_ids_json),
            "variant_asset_ids": _from_json_list(model.variant_asset_ids_json),
            "image_variant_provider": model.image_variant_provider,
            "thumbnail_url": model.thumbnail_url,
            "title": model.title,
            "caption_preview": model.caption_preview,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }

    def _audit_log_to_dict(self, model: AuditLogModel) -> dict[str, Any]:
        return {
            "audit_log_id": model.audit_log_id,
            "request_id": model.request_id,
            "actor_id": model.actor_id,
            "actor_role": model.actor_role,
            "merchant_id": model.merchant_id,
            "action": model.action,
            "resource_type": model.resource_type,
            "resource_id": model.resource_id,
            "status": model.status,
            "metadata": _from_json_dict(model.metadata_json),
            "created_at": model.created_at,
        }

    def _request_log_to_dict(self, model: RequestLogModel) -> dict[str, Any]:
        return {
            "request_id": model.request_id,
            "method": model.method,
            "path": model.path,
            "status_code": model.status_code,
            "duration_ms": model.duration_ms,
            "actor_role": model.actor_role,
            "actor_id": model.actor_id,
            "merchant_id": model.merchant_id,
            "created_at": model.created_at,
        }

    def create_asset(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            model = AssetModel(
                asset_id=data["asset_id"],
                merchant_id=data["merchant_id"],
                filename=data["filename"],
                content_type=data["content_type"],
                size_bytes=data["size_bytes"],
                asset_type=_normalize_value(data["asset_type"]),
                status=_normalize_value(data["status"]),
                provider=_normalize_value(data.get("provider")),
                generated_by_job_id=data.get("generated_by_job_id"),
                source_asset_ids_json=_as_json(data.get("source_asset_ids", [])),
                preview_url=data.get("preview_url"),
                created_at=data["created_at"],
                updated_at=data["updated_at"],
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return self._asset_to_dict(model)

    def update_asset(self, asset_id: str, **updates: Any) -> Optional[dict[str, Any]]:
        with session_scope() as session:
            model = session.get(AssetModel, asset_id)
            if model is None:
                return None
            for field, value in updates.items():
                if field == "source_asset_ids":
                    model.source_asset_ids_json = _as_json(value)
                else:
                    setattr(model, field, _normalize_value(value))
            session.flush()
            session.refresh(model)
            return self._asset_to_dict(model)

    def get_asset(self, asset_id: str) -> Optional[dict[str, Any]]:
        with session_scope() as session:
            model = session.get(AssetModel, asset_id)
            return self._asset_to_dict(model) if model else None

    def list_assets(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            return [self._asset_to_dict(item) for item in session.scalars(select(AssetModel)).all()]

    def create_content(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            model = ContentModel(
                content_id=data["content_id"],
                merchant_id=data["merchant_id"],
                target_country=_normalize_value(data["target_country"]),
                platform=_normalize_value(data["platform"]),
                goal=_normalize_value(data["goal"]),
                status=_normalize_value(data["status"]),
                title=data["title"],
                body=data["body"],
                hashtags_json=_as_json(data.get("hashtags", [])),
                must_include_json=_as_json(data.get("must_include", [])),
                must_avoid_json=_as_json(data.get("must_avoid", [])),
                uploaded_asset_ids_json=_as_json(data.get("uploaded_asset_ids", [])),
                apply_image_variant=bool(data.get("apply_image_variant", False)),
                image_variant_provider=_normalize_value(data.get("image_variant_provider", "none")),
                image_variant_job_id=data.get("image_variant_job_id"),
                publish_job_id=data.get("publish_job_id"),
                latest_publish_result_id=data.get("latest_publish_result_id"),
                publish_result_ids_json=_as_json(data.get("publish_result_ids", [])),
                variant_asset_ids_json=_as_json(data.get("variant_asset_ids", [])),
                approval_required=bool(data.get("approval_required", True)),
                created_at=data["created_at"],
                updated_at=data["updated_at"],
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return self._content_to_dict(model)

    def update_content(self, content_id: str, **updates: Any) -> Optional[dict[str, Any]]:
        with session_scope() as session:
            model = session.get(ContentModel, content_id)
            if model is None:
                return None
            json_fields = {
                "hashtags": "hashtags_json",
                "must_include": "must_include_json",
                "must_avoid": "must_avoid_json",
                "uploaded_asset_ids": "uploaded_asset_ids_json",
                "publish_result_ids": "publish_result_ids_json",
                "variant_asset_ids": "variant_asset_ids_json",
            }
            for field, value in updates.items():
                if field in json_fields:
                    setattr(model, json_fields[field], _as_json(value))
                else:
                    setattr(model, field, _normalize_value(value))
            session.flush()
            session.refresh(model)
            return self._content_to_dict(model)

    def get_content(self, content_id: str) -> Optional[dict[str, Any]]:
        with session_scope() as session:
            model = session.get(ContentModel, content_id)
            return self._content_to_dict(model) if model else None

    def list_contents(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            return [self._content_to_dict(item) for item in session.scalars(select(ContentModel)).all()]

    def create_review(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            model = ReviewModel(
                review_id=data["review_id"],
                merchant_id=data["merchant_id"],
                platform=_normalize_value(data["platform"]),
                rating=data["rating"],
                language=data["language"],
                review_text=data["review_text"],
                sensitivity=_normalize_value(data["sensitivity"]),
                status=_normalize_value(data["status"]),
                reply_draft=data["reply_draft"],
                escalated=bool(data["escalated"]),
                created_at=data["created_at"],
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return self._review_to_dict(model)

    def update_review(self, review_id: str, **updates: Any) -> Optional[dict[str, Any]]:
        with session_scope() as session:
            model = session.get(ReviewModel, review_id)
            if model is None:
                return None
            for field, value in updates.items():
                setattr(model, field, _normalize_value(value))
            session.flush()
            session.refresh(model)
            return self._review_to_dict(model)

    def get_review(self, review_id: str) -> Optional[dict[str, Any]]:
        with session_scope() as session:
            model = session.get(ReviewModel, review_id)
            return self._review_to_dict(model) if model else None

    def list_reviews(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            return [self._review_to_dict(item) for item in session.scalars(select(ReviewModel)).all()]

    def create_report(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            model = ReportModel(
                report_id=data["report_id"],
                scope_type=data["scope_type"],
                scope_id=data["scope_id"],
                year=data["year"],
                month=data["month"],
                status=data["status"],
                created_at=data["created_at"],
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return self._report_to_dict(model)

    def get_report(self, report_id: str) -> Optional[dict[str, Any]]:
        with session_scope() as session:
            model = session.get(ReportModel, report_id)
            return self._report_to_dict(model) if model else None

    def list_reports(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            return [self._report_to_dict(item) for item in session.scalars(select(ReportModel)).all()]

    def create_job(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            model = JobModel(
                job_id=data["job_id"],
                job_type=data["job_type"],
                status=_normalize_value(data["status"]),
                resource_type=data["resource_type"],
                resource_id=data["resource_id"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return self._job_to_dict(model)

    def update_job(self, job_id: str, **updates: Any) -> Optional[dict[str, Any]]:
        with session_scope() as session:
            model = session.get(JobModel, job_id)
            if model is None:
                return None
            for field, value in updates.items():
                setattr(model, field, _normalize_value(value))
            session.flush()
            session.refresh(model)
            return self._job_to_dict(model)

    def get_job(self, job_id: str) -> Optional[dict[str, Any]]:
        with session_scope() as session:
            model = session.get(JobModel, job_id)
            return self._job_to_dict(model) if model else None

    def list_jobs(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            return [self._job_to_dict(item) for item in session.scalars(select(JobModel)).all()]

    def create_publish_result(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            model = PublishResultModel(
                publish_result_id=data["publish_result_id"],
                content_id=data["content_id"],
                channel=_normalize_value(data["channel"]),
                adapter_name=data["adapter_name"],
                status=data["status"],
                external_post_id=data.get("external_post_id"),
                external_url=data.get("external_url"),
                publish_at=data.get("publish_at"),
                source_asset_ids_json=_as_json(data.get("source_asset_ids", [])),
                variant_asset_ids_json=_as_json(data.get("variant_asset_ids", [])),
                image_variant_provider=_normalize_value(data.get("image_variant_provider")),
                thumbnail_url=data.get("thumbnail_url"),
                title=data.get("title"),
                caption_preview=data.get("caption_preview"),
                created_at=data["created_at"],
                updated_at=data["updated_at"],
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return self._publish_result_to_dict(model)

    def get_publish_result(self, publish_result_id: str) -> Optional[dict[str, Any]]:
        with session_scope() as session:
            model = session.get(PublishResultModel, publish_result_id)
            return self._publish_result_to_dict(model) if model else None

    def list_publish_results(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            return [self._publish_result_to_dict(item) for item in session.scalars(select(PublishResultModel)).all()]

    def create_audit_log(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            model = AuditLogModel(
                audit_log_id=data["audit_log_id"],
                request_id=data.get("request_id"),
                actor_id=data.get("actor_id"),
                actor_role=data.get("actor_role"),
                merchant_id=data.get("merchant_id"),
                action=data["action"],
                resource_type=data["resource_type"],
                resource_id=data["resource_id"],
                status=data["status"],
                metadata_json=_as_json(data.get("metadata", {})),
                created_at=data["created_at"],
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return self._audit_log_to_dict(model)

    def list_audit_logs(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            return [self._audit_log_to_dict(item) for item in session.scalars(select(AuditLogModel)).all()]

    def create_request_log(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            model = RequestLogModel(
                request_id=data["request_id"],
                method=data["method"],
                path=data["path"],
                status_code=data["status_code"],
                duration_ms=data["duration_ms"],
                actor_role=data.get("actor_role"),
                actor_id=data.get("actor_id"),
                merchant_id=data.get("merchant_id"),
                created_at=data["created_at"],
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return self._request_log_to_dict(model)

    def list_request_logs(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            return [self._request_log_to_dict(item) for item in session.scalars(select(RequestLogModel)).all()]


db_repository = DatabaseRepository()
