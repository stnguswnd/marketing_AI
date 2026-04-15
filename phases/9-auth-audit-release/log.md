# Phase 9 Log

## Completed
- `app/core/permissions.py`를 추가해 role, actor, merchant scope 검사를 공통 함수로 분리했다.
- 서비스 일부가 직접 role 문자열을 비교하던 구조를 permission helper 기반으로 정리했다.
- 감사 로그 API와 관리자 UI를 통해 운영자가 승인/발행/리포트 생성 흔적을 추적할 수 있게 했다.
- 이후 역할 모델을 다시 정리해 점주는 자기 merchant scope 안에서 approve/reject/publish/review-reply를 직접 수행하도록 변경했다.
- 관리자 권한은 merchant summary, audit, observability 중심으로 축소하고 admin-only summary API를 추가했다.
- release 기준을 [release-checklist.md](/Users/guswnd0432389/Desktop/harness_framework/phases/9-auth-audit-release/release-checklist.md) 로 남겼다.
- `.env.example`과 settings 계층을 추가해 운영 환경 변수 기준을 코드에 명시했다.
- backend `pytest`, `py_compile`, frontend `lint/build`를 다시 실행해 현재 배포 전 기준이 유지되는지 확인했다.

## Errors
- 기존 프론트 observability 타입은 백엔드 응답과 다르게 설계돼 있었고, 실제 request/audit 응답 구조에 맞춰 다시 정리했다.
- Python 3.9 런타임에서 `| None` 타입 표기가 import 단계에서 실패해 `Optional[...]` 기반으로 되돌렸다.
- release checklist만으로는 실제 보안 요건이 충족되지 않으므로, 현재 phase는 완료가 아니라 운영 준비 중 상태로 남겨뒀다.

## Remaining
- 현재 인증은 테스트 헤더 기반이라 실제 배포용 인증 계층은 아직 없다.
- webhook secret과 운영 시크릿은 환경변수 기반 설정으로 옮겨야 한다.
- release checklist는 초안 수준이며 CI/CD, secret manager, backup policy와 더 연결해야 한다.
