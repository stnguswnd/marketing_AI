import time
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.errors import AppError, build_error_payload
from app.core.settings import get_settings
from app.db.bootstrap import create_database_schema
from app.repositories.database import db_repository
from app.services.mock_seed import seed_demo_repository


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    create_database_schema()
    if settings.app_env != "test":
        seed_demo_repository()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.backend_cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or f"req_{uuid4().hex[:10]}"
        request.state.request_id = request_id
        started_at = time.perf_counter()

        response = await call_next(request)

        duration_ms = int((time.perf_counter() - started_at) * 1000)
        db_repository.create_request_log({
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "actor_role": request.headers.get("X-Test-Role") or request.headers.get("X-Role"),
            "actor_id": request.headers.get("X-Test-User-Id") or request.headers.get("X-Actor-Id"),
            "merchant_id": request.headers.get("X-Test-Merchant-Id") or request.headers.get("X-Merchant-Id"),
            "created_at": datetime.now(timezone.utc),
        })
        response.headers["X-Request-Id"] = request_id
        return response

    @app.get("/")
    def root_health() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_payload(exc.error_code, exc.message, exc.field_errors),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        field_errors: dict[str, list[str]] = {}
        for error in exc.errors():
            loc = [part for part in error.get("loc", []) if part != "body"]
            if not loc:
                continue
            field = str(loc[-1])
            field_errors.setdefault(field, []).append(error.get("msg", "Invalid value"))

        return JSONResponse(
            status_code=400,
            content=build_error_payload(
                "VALIDATION_ERROR",
                "입력값을 확인해 주세요.",
                field_errors or None,
            ),
        )

    return app


app = create_app()
