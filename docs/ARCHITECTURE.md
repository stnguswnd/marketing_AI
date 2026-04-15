# 아키텍처

## 개요
이 시스템은 구조화된 폼 입력을 받아 내부 LangGraph 워크플로우를 실행하고, 결과를 저장한 뒤 승인, 게시, 리포트, 리뷰 대응까지 이어지는 운영형 백엔드를 목표로 한다.

핵심 구성은 다음과 같다.

- `frontend/`: Next.js App Router 기반 UI
- `backend/`: FastAPI, LangGraph, SQLAlchemy, Celery가 들어 있는 백엔드 워크스페이스
- FastAPI: 외부 요청 진입점
- Pydantic v2: 요청/응답 및 내부 스키마 검증
- SQLAlchemy + PostgreSQL: 운영 데이터와 감사 로그 저장
- LangGraph: 상태 기반 AI 워크플로우 실행
- Celery + Redis: 비동기 작업, 스케줄링, 재시도
- `integrations/`: 외부 플랫폼 및 모델 연동 어댑터
- Asset storage/CDN: 업로드 이미지와 변형 결과 저장

## 시스템 컨텍스트
```text
Merchant/Admin UI
  -> frontend/ Next.js App Router
  -> FastAPI REST API
  -> Service Layer
  -> Repository Layer
  -> PostgreSQL

FastAPI / Worker
  -> LangGraph Workflow
  -> Integrations (LLM / Social / Review / Messaging / Media)

Scheduler / Async Job
  -> Celery
  -> Redis
```

## 디렉토리 구조
```text
frontend/
├── app/                  # Next.js App Router pages and global styles
├── components/           # UI components and CSS modules
├── lib/                  # API clients, helpers, shared utils
└── public/               # Static assets

backend/
├── app/
│   ├── main.py             # FastAPI 엔트리포인트
│   ├── core/               # 설정, 보안, 로깅, DB 연결
│   ├── api/                # REST API 라우터
│   │   └── v1/
│   ├── schemas/            # Pydantic 요청/응답 및 내부 스키마
│   ├── models/             # SQLAlchemy ORM 모델
│   ├── services/           # 비즈니스 로직 서비스
│   ├── graphs/             # LangGraph 워크플로우
│   ├── integrations/       # 외부 API 어댑터
│   ├── workers/            # Celery 앱 및 태스크
│   ├── repositories/       # 저장소 레이어
│   └── db/                 # 세션, 부트스트랩, seed
├── scripts/                # DB 초기화, 로컬/컨테이너 실행 보조 스크립트
├── tests/                  # 단위/통합 테스트
└── pyproject.toml          # 백엔드 Python 의존성
infra/                       # Docker, 배포, 인프라 설정
```

## 레이어 원칙
- 모든 외부 요청은 FastAPI API 또는 명시된 webhook endpoint를 통해서만 진입한다.
- 모든 사용자 입력은 구조화된 API 스키마로 검증한다.
- 프론트엔드는 `frontend/` 아래 Next.js App Router로 구현하고, UI 전용 코드는 `backend/app/` 패키지와 분리한다.
- `backend/app/`는 Python 백엔드 전용 디렉토리이며, Next.js 루트로 사용하지 않는다.
- 비즈니스 로직은 `services/`에 둔다.
- DB 접근은 `repositories/`로 분리한다.
- AI 모델 호출은 `services/` 또는 `graphs/nodes/` 내부에서만 수행한다.
- 외부 플랫폼 API 호출은 반드시 `integrations/` 어댑터를 통해 수행한다.
- 이미지 보정/변형 모델 호출도 반드시 `integrations/media/` 어댑터를 통해 수행한다.
- 민감 리뷰와 외부 발행 가능 콘텐츠는 감사 로그를 남긴다.

## 핵심 패턴

### 1. Form-first request pattern
사용자는 자연어 한 줄 요청이 아니라 구조화된 폼을 입력한다. 프론트는 입력 수집과 검증을 담당하고, 서버는 검증된 스키마를 바탕으로 workflow state를 구성한다.

프론트 구현은 Next.js App Router를 기준으로 한다. 라우트 그룹을 점주용/관리자용으로 분리하고, 모달과 폼 상태는 클라이언트 컴포넌트가 담당한다.

### 2. Thin router pattern
라우터는 인증, 권한 확인, 스키마 검증, 서비스 호출만 수행한다. 도메인 규칙과 예외 처리 정책은 서비스 계층이 담당한다.

### 3. Stateful workflow pattern
콘텐츠 생성, 리뷰 대응, 리포트 생성은 LangGraph 상태 객체를 중심으로 노드 단위로 실행된다. 각 노드는 명시적인 입력/출력을 갖고 재시도 가능해야 한다.

### 4. Adapter pattern
Instagram, Google Business Profile, 메시징, LLM 공급자 등 외부 의존성은 어댑터 계층으로 추상화한다. 서비스 레이어는 공급자별 구현 상세를 몰라야 한다.

### 5. Approval gate pattern
외부 게시물과 민감한 리뷰 답변은 자동 게시하지 않는다. `draft -> approved -> scheduled -> published` 또는 `rejected` 상태 전이를 따른다.

### 6. Event-driven async pattern
장시간 실행, 예약 발행, 배치 리포트, 리뷰 수집은 Celery task로 분리한다. 작업 상태는 DB job record와 task ID를 함께 저장한다.

### 7. Pre-publish asset processing pattern
사용자가 업로드한 입력 이미지가 있을 경우, 발행 직전 선택적으로 이미지 보정/변형 단계를 실행할 수 있다. 이 단계는 원본 이미지를 대체하지 않고 variant asset을 추가 생성하는 방식으로 처리한다.

## 데이터 흐름

### 공통 흐름
```text
사용자 모달/폼 입력
-> 프론트엔드 검증
-> FastAPI API 호출
-> 서버 입력 스키마 검증
-> 점포 프로필 / 홈페이지 / 기존 승인 콘텐츠 / 룰셋 조회
-> LangGraph state 구성
-> 그래프 노드 실행
-> 결과 저장
-> 승인 필요 여부 판정
-> 발행 시 optional image variant processing
-> 응답 반환 또는 후속 작업 큐 등록
-> 관리자/점주 UI 반영
```

### 콘텐츠 생성 예시
```text
점주가 콘텐츠 생성 모달에서
[나라, 플랫폼, 목적, 강조 내용, 홈페이지 URL, 이미지] 입력
-> POST /contents/generate
-> merchant profile 조회
-> website 요약 및 기존 데이터 조회
-> content graph 실행
-> 전략 수립 노드
-> 카피 생성 노드
-> 규칙 검증 노드
-> draft 저장
-> approval 상태 반환
-> publish 요청 시 source asset 조회
-> optional Nano Banana image transform 실행
-> variant asset 저장
-> 게시 payload 구성
```

### 리뷰 대응 예시
```text
리뷰 이벤트 수집
-> 리뷰 분류 서비스
-> 민감도 판정
-> reply graph 실행
-> 답변 초안 생성
-> 민감 리뷰면 escalation
-> 승인 또는 수정 후 게시
```

## 상태 관리
- 프론트엔드는 폼 상태와 화면 표시 상태만 관리한다.
- 서버의 source of truth는 PostgreSQL이다.
- 워크플로우 상태는 LangGraph state로 관리한다.
- 비동기 작업 상태는 Celery task와 DB job record로 관리한다.
- 일시적 캐시와 큐 상태는 Redis를 사용한다.
- 생성 결과 상태는 `draft`, `approved`, `scheduled`, `published`, `rejected` 등 명시적 값으로 저장한다.
- 업로드 자산은 `source`, `variant`, `approved_variant`, `published_variant` 같은 자산 상태 또는 타입으로 구분한다.

## 주요 도메인 경계
- Merchant Service: 점포 정보, 브랜드 프로필, 자산 관리
- Content Service: 콘텐츠 생성, 버전 관리, 승인, 발행 요청
- Asset Service: 파일 업로드, 원본/변형 자산 관리, provider 실행 이력 관리
- Review Service: 리뷰 수집, 분류, 답글 초안, escalation
- Report Service: 월간 성과 집계, PDF/요약 생성, 관리자 조회
- Admin Service: 사업 단위 모니터링, 정책, 룰셋, 감사 조회

## 사전에 준비해야 할 외부 API
- LLM provider API: 콘텐츠 초안, 리뷰 답글, 리포트 요약 생성
- Social platform publish API: Instagram, Google Business Profile 등 게시 및 리뷰 연동
- Review/webhook API: 외부 리뷰 이벤트 수신
- Messaging or notification API: 승인 요청, 실패 알림, 운영 알림
- Asset storage API or object storage: 업로드 이미지, variant 이미지 저장
- Image transform provider API: 입력 이미지를 기반으로 보정/변형 이미지를 만드는 provider

`Nano Banana`를 쓸 경우 이 문서에서는 `integrations/media/nano_banana_adapter.py` 같은 어댑터를 두고, 발행 직전 optional pre-publish 단계에서 호출하는 것으로 가정한다.

## 예시 입력 스키마
```json
{
  "merchant_id": "m_123",
  "target_country": "JP",
  "platform": "instagram",
  "goal": "store_visit",
  "input_brief": "벚꽃 시즌에 맞춰 말차라떼와 푸딩을 강조하고 싶어요.",
  "website_url": "https://example.com",
  "tone": "friendly",
  "must_include": ["말차라떼", "부산 여행"],
  "must_avoid": ["최고", "무조건"],
  "uploaded_asset_ids": ["asset_1", "asset_2"],
  "publish_mode": "draft"
}
```

## 비기능 요구사항
- 모든 승인 이력과 결과물 버전은 추적 가능해야 한다.
- 민감 리뷰와 외부 발행 콘텐츠는 감사 로그를 남겨야 한다.
- 실패한 워크플로우는 재시도 가능하거나 중간 상태에서 재개 가능해야 한다.
- 테스트 없이 새 기능을 머지하지 않는다.
- 프롬프트 변경 시 버전 기록이 필요하다.

## 실행 방식
이 저장소는 이제 `frontend/`와 `backend/`가 완전히 분리된 멀티서비스 구조를 기준으로 한다.

- `frontend/`: Next.js 개발 서버, 빌드, lint
- `backend/`: FastAPI, pytest, seed 스크립트, Celery
- `infra/docker-compose.yml`: Postgres, Redis, backend, worker, frontend 통합 실행
- `backend/scripts/start_backend.sh`: 컨테이너 시작 시 DB schema/seed를 먼저 적용한 뒤 API 서버를 띄운다.
- 개발용 Compose는 `frontend/`, `backend/`를 bind mount 하고, `next dev`, `uvicorn --reload`를 사용해 수정 사항을 재빌드 없이 반영한다.

초기 실행 시 DB는 자동으로 올라간다.

1. `docker compose up --build`로 Postgres와 Redis를 먼저 올린다.
2. `backend` 컨테이너가 `python scripts/init_mock_db.py`를 반복 실행한다.
3. 스키마 생성과 seed 계정 insert가 끝나면 `uvicorn`이 뜬다.
4. 프론트 브라우저는 `http://127.0.0.1:8000/api/v1`를 API base로 사용한다.

이후의 일반적인 개발 수정은 `--build` 없이 반영된다.

- 백엔드: bind mount + `uvicorn --reload`
- 프론트: bind mount + `next dev`

## 운영 명령어
```bash
cd backend && python3 -m uvicorn app.main:app --reload
cd backend && python3 -m pytest
cd frontend && npm install && npm run dev
cd backend && python3 scripts/init_mock_db.py
cd backend && celery -A app.workers.celery_app worker --loglevel=info
docker compose -f infra/docker-compose.yml up --build
```
