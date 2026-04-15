# Phase 8 Log

## Completed
- `X-Request-Id`를 응답 헤더로 돌려주는 request tracing middleware를 추가했다.
- 메모리 저장소에 `request_logs`, `audit_logs`를 추가하고 API로 조회할 수 있게 했다.
- `GET /api/v1/observability/requests`, `GET /api/v1/observability/summary`, `GET /api/v1/audit-logs`를 추가했다.
- 관리자 화면에서 request trace, observability summary, audit log를 바로 확인할 수 있게 연결했다.
- 민감 액션인 자산 등록, 콘텐츠 생성/승인/반려/발행 요청, 리뷰 승인, 리포트 생성에 audit log를 남기도록 바꿨다.
- `.env.example`, `app/core/settings.py`, `app/workers/`, `infra/docker-compose.yml`을 추가해 운영 인프라 스캐폴드를 만들었다.
- SQLAlchemy 모델과 DB 세션 골격을 `app/db/`, `app/models/` 아래에 추가했다.
- `tests/test_settings.py`를 추가했고 전체 테스트가 `32 passed`로 통과했다.

## Errors
- observability 프론트 타입이 초기엔 백엔드 응답과 맞지 않아 summary/request 필드명을 다시 맞췄다.
- 관리자 화면 build 중 `variant_asset_ids` optional 타입 오류가 있어 optional 처리로 정리했다.
- 운영 인프라 스캐폴드는 현재 실행 중인 앱에 강제로 연결하지 않고, 테스트 런타임을 깨지 않도록 파일 단위로 분리했다.

## Remaining
- 현재 관측 데이터는 in-memory 저장이라 프로세스 재시작 시 사라진다.
- Celery/Redis/PostgreSQL과 같은 실제 운영 인프라 연결은 아직 없다.
- alerting, metrics export, long-running worker trace는 다음 단계에서 외부 스택과 붙여야 한다.
