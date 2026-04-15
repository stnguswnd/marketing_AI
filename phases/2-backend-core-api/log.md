# Phase 2 Log

## Completed
- `GET /api/v1/assets/{asset_id}` 조회 API와 응답 스키마를 추가했다.
- asset 저장 데이터에 `created_at`, `updated_at`, `provider`, `source_asset_ids`를 포함시켰다.
- 콘텐츠 publish 처리 로직을 `app/services/publish.py`로 분리했다.
- 콘텐츠/리뷰 상태 전이 규칙을 `app/domain/status_rules.py`로 분리했다.
- asset 상세 조회 성공/권한 실패 테스트를 추가했다.
- 상태 전이 실패 케이스 테스트를 추가했다.
- 전체 `pytest`를 다시 실행했고 `26 passed`를 확인했다.

## Errors
- Python 3.9 환경에서 `str | None` 타입 표기가 실패해 `Optional[str]`로 수정했다.

## Remaining
- publish service는 분리됐지만 실제 외부 채널 adapter 연결은 아직 없다.
- 외부 발행 결과 저장 구조는 Phase 7에서 adapter와 함께 확장하는 편이 맞다.
