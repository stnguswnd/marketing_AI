from fastapi import APIRouter, Depends

from app.core.auth import RequestContext, get_request_context
from app.schemas.publish import PublishResultListResponse, PublishResultResponse
from app.services.publish_result import publish_result_service


router = APIRouter(prefix="/publish-results")


@router.get("", response_model=PublishResultListResponse)
def list_publish_results(context: RequestContext = Depends(get_request_context)) -> PublishResultListResponse:
    return publish_result_service.list(context)


@router.get("/{publish_result_id}", response_model=PublishResultResponse)
def get_publish_result(
    publish_result_id: str,
    context: RequestContext = Depends(get_request_context),
) -> PublishResultResponse:
    return publish_result_service.get(publish_result_id, context)
