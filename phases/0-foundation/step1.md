# Step 1: api-skeleton

## 읽어야 할 파일
- `/docs/ARCHITECTURE.md`
- `/docs/API_SPEC.md`
- `/docs/FRONTEND_MODAL_SPEC.md`

## 작업
FastAPI 기반 API 골격을 구현한다.
- `GET /health`
- 콘텐츠, 리뷰, 리포트, 잡 상태 조회용 `v1` 라우터
- 요청/응답 스키마
- 외부 의존성 없이 동작하는 in-memory 저장소 및 서비스

## Acceptance Criteria
```bash
python3 -m pytest tests
```

## 검증 절차
1. AC 커맨드를 실행한다.
2. 상태 전이와 권한/검증 실패 케이스를 확인한다.
3. 결과를 Phase 로그에 남긴다.

## 금지사항
- 라우터에서 직접 비즈니스 로직을 구현하지 마라. 이유: ADR-008 위반이다.
- DB나 Redis를 실제로 연결하지 마라. 이유: Foundation 단계에서는 스캐폴딩만 한다.
