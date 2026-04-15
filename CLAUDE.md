# 프로젝트: 소상공인 글로벌 마케팅 자동화 플랫폼

## 현재 성격
- 이 저장소는 점주/관리자 운영 흐름을 검증하는 프로토타입이자 데모 하네스다.
- `frontend/`와 `backend/`가 분리된 멀티서비스 구조를 사용한다.
- 실제 외부 연동 일부는 아직 스텁이며, 문서와 코드 모두 이 상태를 숨기지 않는다.

## 기술 스택
- 프론트엔드: Next.js App Router, React 18, TypeScript
- 백엔드: FastAPI, Pydantic v2, SQLAlchemy
- 워크플로우: LangGraph
- 비동기/인프라: Celery, Redis, PostgreSQL, Docker Compose

## 아키텍처 규칙
- CRITICAL: 외부 요청 진입은 `backend/app/api/v1/routes/` 라우터를 통해서만 처리한다.
- CRITICAL: 비즈니스 로직은 라우터가 아니라 `backend/app/services/` 에 둔다.
- CRITICAL: DB 접근은 `backend/app/repositories/` 를 통해서만 수행한다.
- CRITICAL: 외부 연동은 `backend/app/integrations/` 어댑터를 통해서만 호출한다.
- CRITICAL: 프론트는 `frontend/lib/api.ts` 를 통해 백엔드 API를 호출한다.
- 점주/관리자 UI 문구는 데모 범위를 넘는 실제 연동처럼 과장하지 않는다.
- 스텁 구현은 유지할 수 있지만, 문서와 UI에서 스텁임을 숨기지 않는다.

## 개발 프로세스
- 새 API나 상태 전이를 추가하면 백엔드 테스트를 함께 추가한다.
- 사용자 변경이 섞인 워크트리일 수 있으므로, 관련 없는 파일은 건드리지 않는다.
- 문서 수정 시 구현 완료/미완료 상태를 코드 기준으로 맞춘다.

## 자주 쓰는 명령어
```bash
docker compose -f infra/docker-compose.yml up --build
cd backend && python3 -m pip install -e '.[dev]'
cd backend && python3 -m pytest
cd frontend && npm install
cd frontend && npm run lint
cd frontend && npm run build
```
