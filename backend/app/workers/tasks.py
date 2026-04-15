from __future__ import annotations

from app.workers.celery_app import celery_app


@celery_app.task(name="content.publish")
def publish_content_job(content_id: str) -> dict[str, str]:
    return {"job": "content.publish", "content_id": content_id, "status": "stubbed"}


@celery_app.task(name="report.generate_monthly")
def generate_monthly_report_job(report_id: str) -> dict[str, str]:
    return {"job": "report.generate_monthly", "report_id": report_id, "status": "stubbed"}


@celery_app.task(name="media.generate_variant")
def generate_variant_job(content_id: str) -> dict[str, str]:
    return {"job": "media.generate_variant", "content_id": content_id, "status": "stubbed"}
