# Release Checklist

## Security
- 테스트 헤더 기반 인증을 운영 인증 계층으로 교체할 것
- webhook secret을 환경변수/secret manager로 이동할 것
- 운영 권한 role matrix를 문서와 코드에 같이 고정할 것

## Data
- in-memory 저장소를 PostgreSQL 기반 영속 저장소로 교체할 것
- audit log와 request trace 보존 기간 정책을 정의할 것
- object storage와 업로드 보존 정책을 정할 것

## Workers
- Celery worker와 beat를 실제 배포 구성을 기준으로 분리할 것
- retry 정책과 dead-letter 처리 기준을 정할 것
- long-running publish/image variant job 타임아웃을 확정할 것

## Observability
- request trace와 audit log를 외부 로그 스택으로 내보낼 것
- 에러율, 지연 시간, publish 실패율 알람을 구성할 것
- request id와 job id를 운영 로그에서 함께 추적 가능하게 할 것

## Integrations
- blog/social provider 인증과 sandbox 계정을 준비할 것
- Nano Banana 실제 API key와 비용 제한 정책을 정할 것
- 외부 발행 실패 시 수동 재처리 절차를 문서화할 것

## Verification
- backend `pytest`와 frontend `lint/build`를 CI에서 고정할 것
- 승인/반려/발행/리뷰 승인에 대한 회귀 테스트를 유지할 것
- 배포 전 smoke test 시나리오를 운영 체크리스트에 포함할 것
