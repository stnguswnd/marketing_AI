# Phase 4 Log

## Completed
- 관리자 화면이 사용할 `content`, `asset`, `review`, `report`, `job`, `publish-result` 목록/상세 API를 추가했다.
- publish 결과를 저장할 수 있는 백엔드 구조를 정리하고, 리스트 조회 엔드포인트를 노출했다.
- 관리자 프론트 화면을 list API 기반 큐, 발행 결과, variant asset 뷰로 교체했다.
- 이후 권한 모델을 점주 중심으로 재설계하면서 관리자 화면의 approve/reject/publish/review 액션을 제거했다.
- `GET /api/v1/admin/merchants`를 추가해 점포별 운영 요약을 집계하도록 바꿨다.
- 관리자 화면을 merchant summary, audit log, observability 중심 모니터링 뷰로 다시 정리했다.

## Remaining
- 고급 필터, 정렬, 페이지네이션은 아직 없다.
- 실제 점주 계정 생성/비활성화 같은 관리 기능은 아직 없다.
