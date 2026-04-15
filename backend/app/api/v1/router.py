from fastapi import APIRouter

from app.api.v1.routes import admin, asset, audit, auth, content, health, job, observability, publish, report, review


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(asset.router, tags=["asset"])
api_router.include_router(content.router, tags=["content"])
api_router.include_router(review.router, tags=["review"])
api_router.include_router(report.router, tags=["report"])
api_router.include_router(job.router, tags=["job"])
api_router.include_router(publish.router, tags=["publish"])
api_router.include_router(audit.router, tags=["audit"])
api_router.include_router(observability.router, tags=["observability"])
