# 기능 명세서

## 1. 문서 목적
이 문서는 현재 프로젝트의 전체 구조를 기능 중심으로 설명하는 기준 명세서다.  
PRD, Architecture, API, Phase 로그에 흩어진 내용을 실제 구현 기준으로 다시 정리한다.

이 문서는 다음 질문에 답하는 것을 목표로 한다.
- 이 시스템은 누구를 위해 존재하는가
- 어떤 역할이 어떤 기능을 사용하는가
- 각 기능은 어떤 입력, 처리, 상태, 출력으로 동작하는가
- 프론트엔드와 백엔드는 어떻게 연결되는가
- 현재 구현된 범위와 아직 스텁인 범위는 어디까지인가

---

## 2. 제품 개요

### 제품명
소상공인 글로벌 마케팅 자동화 플랫폼

### 제품 목표
소상공인이 해외 고객 대상 마케팅 업무를 직접 하지 않아도 되도록, 구조화된 입력만으로 콘텐츠 생성, 리뷰 대응, 발행 요청, 성과 리포트, 감사 추적까지 운영할 수 있게 한다.

### 핵심 원칙
- 사용자 입력은 자유 자연어가 아니라 구조화된 폼을 우선한다.
- AI는 사용자 인터페이스가 아니라 내부 워크플로우 엔진으로 동작한다.
- 생성 결과는 바로 외부 발행하지 않고 승인 가능성과 감사 가능성을 전제로 저장한다.
- 점주 화면과 관리자 화면은 역할에 맞게 분리한다.
- 모든 민감 액션은 상태 전이와 감사 로그 기준으로 추적 가능해야 한다.

---

## 3. 사용자와 역할

### `merchant`
- 본인 점포 기준으로 콘텐츠 요청을 생성한다.
- 이미지 자산을 등록한다.
- 생성된 draft 상태 결과를 확인한다.
- 생성된 draft가 불필요하면 삭제한다.
- 본인 점포 콘텐츠를 승인, 반려, 발행 요청할 수 있다.
- 리뷰 답글 승인과 리포트 생성을 직접 수행할 수 있다.

### `operator`
- 운영 관점에서 여러 점포 데이터를 조회한다.
- 감사, 관측, 예외 상황 대응을 지원한다.

### `admin`
- `operator`와 유사하지만 운영/관리 전반을 총괄하는 역할이다.
- 감사 로그, 관측 정보, 발행 결과, 작업 상태를 조회한다.
- 점포 단위 활동 요약과 플랫폼 운영 정책을 관리한다.

### `webhook`
- 외부 리뷰 플랫폼이 시스템으로 이벤트를 전달할 때 사용하는 진입 역할이다.

---

## 4. 시스템 구조 요약

## 프론트엔드
- 위치: `frontend/`
- 프레임워크: Next.js App Router
- 주요 라우트
  - `/`
  - `/merchant`
  - `/admin`

## 백엔드
- 위치: `backend/app/`
- 프레임워크: FastAPI
- 주요 계층
  - `api/v1/routes/`: 외부 진입 라우트
  - `services/`: 비즈니스 로직
  - `graphs/`: LangGraph 워크플로우
  - `schemas/`: 요청/응답 스키마
  - `integrations/`: 외부 연동 어댑터
  - `core/`: 인증, 권한, 설정, 에러

## 상태 저장
- 현재 런타임 기준: `PostgreSQL + SQLAlchemy Repository`
- 저장 항목
  - assets
  - contents
  - reviews
  - reports
  - jobs
  - publish_results
  - audit_logs
  - request_logs

## 운영 인프라
- `backend/app/core/settings.py`
- `backend/app/db/`
- `backend/app/models/`
- `backend/app/workers/`
- `infra/docker-compose.yml`

현재 백엔드 CRUD와 감사/관측 로그는 DB를 기준으로 동작한다.

---

## 5. 기능 목록

### 5.1 점주 콘텐츠 요청

#### 목적
점주가 짧고 명확한 입력만으로 콘텐츠 초안 생성을 요청할 수 있게 한다.

#### 프론트 위치
- `/merchant`
- `frontend/components/merchant-dashboard.tsx`

#### 입력 항목
- 대상 국가
- 플랫폼
- 목표
- 톤
- 홈페이지 URL
- 강조 brief
- 꼭 포함할 표현
- 피해야 할 표현
- 업로드 자산
- 이미지 변형 사용 여부
- 이미지 변형 provider

#### 백엔드 엔드포인트
- `POST /api/v1/assets/upload-init`
- `POST /api/v1/contents/generate`

#### 처리 방식
1. 점주가 파일을 선택한다.
2. 프론트가 `upload-init`으로 자산 메타데이터를 등록한다.
3. 프론트가 `POST /api/v1/assets/{asset_id}/binary` 로 실제 파일을 업로드한다.
4. 자산 ID를 포함해 콘텐츠 생성 요청을 보낸다.
5. 백엔드는 입력 스키마를 검증한다.
6. 콘텐츠 그래프를 실행해 title/body/hashtags를 생성한다.
7. 결과를 `draft` 상태로 PostgreSQL에 저장한다.
8. content_generate job과 audit log를 DB에 생성한다.

#### 출력
- `content_id`
- `status=draft`
- `approval_required=true`
- `job_id`

#### 현재 상태
- 구현 완료
- 로컬/데모 기준 실제 multipart 업로드 구현 완료
- object storage와 signed URL은 아직 없음

---

### 5.2 콘텐츠 상세 조회

#### 목적
점주 또는 관리자가 특정 콘텐츠의 상태와 내용을 조회한다.

#### 엔드포인트
- `GET /api/v1/contents/{content_id}`
- `GET /api/v1/contents`

#### 조회 정보
- 대상 국가
- 플랫폼
- 목표
- 본문/title/hashtags
- 상태
- 업로드 자산 ID
- 이미지 variant 관련 정보
- publish_result 연결 정보

#### 현재 상태
- 구현 완료
- 관리자 화면에서는 목록 기반 큐와 상세 조회 둘 다 사용 중

---

### 5.3 콘텐츠 승인 / 반려

#### 목적
점주가 본인 점포 draft 콘텐츠를 운영 기준에 따라 승인 또는 반려한다.

#### 엔드포인트
- `POST /api/v1/contents/{content_id}/approve`
- `POST /api/v1/contents/{content_id}/reject`

#### 상태 전이
- `draft -> approved`
- `draft -> rejected`

#### 검증 규칙
- 승인/반려는 `merchant`, `operator`, `admin`이 가능
- 잘못된 상태 전이는 거부
- 모든 액션은 audit log 기록

#### 현재 상태
- 구현 완료
- 상태 전이 규칙은 `backend/app/domain/status_rules.py`에 중앙화

---

### 5.4 콘텐츠 발행 요청

#### 목적
승인된 콘텐츠를 외부 채널 발행 후보 상태로 전환하고, 발행 결과를 추적한다.

#### 엔드포인트
- `POST /api/v1/contents/{content_id}/publish`
- `GET /api/v1/publish-results`
- `GET /api/v1/publish-results/{publish_result_id}`

#### 상태 전이
- `approved -> scheduled`

#### 처리 방식
1. 점주 또는 운영자가 publish 요청을 보낸다.
2. 백엔드는 승인 상태인지 확인한다.
3. 필요하면 variant 생성 단계를 실행한다.
4. publish job을 생성한다.
5. publish_result를 저장한다.
6. audit log를 기록한다.

#### 현재 채널 처리
- `blog`: `blog_publish_adapter` 스텁 사용
- 기타 플랫폼: internal stub 수준

#### 현재 상태
- 구조 구현 완료
- 실제 외부 채널 인증/발행은 아직 스텁

---

### 5.5 이미지 자산 관리

#### 목적
원본 자산과 variant 자산을 등록, 조회, 추적한다.

#### 엔드포인트
- `POST /api/v1/assets/upload-init`
- `POST /api/v1/assets/{asset_id}/binary`
- `GET /api/v1/assets`
- `GET /api/v1/assets/{asset_id}`

#### 자산 유형
- `source`
- `variant`

#### 저장 정보
- merchant_id
- filename
- content_type
- size_bytes
- provider
- generated_by_job_id
- source_asset_ids
- created_at / updated_at

#### 현재 상태
- 자산 메타데이터 관리와 로컬 업로드 구현 완료
- object storage와 signed URL은 아직 없음

---

### 5.6 이미지 variant 생성

#### 목적
업로드한 원본 이미지를 기반으로 발행용 variant 이미지를 생성한다.

#### provider
- `nano_banana`

#### 처리 방식
1. publish 요청에서 `apply_image_variant=true`
2. source asset 존재 여부 검증
3. `Nano Banana` 어댑터 호출
4. variant asset 생성
5. image variant job 생성
6. content와 publish_result에 variant 정보 연결

#### 현재 상태
- 스텁 구현 완료
- provider 호출은 mock/stub 수준
- 실제 외부 API key 사용 및 비용 제어는 미구현

---

### 5.7 리뷰 수집과 답글 승인

#### 목적
외부 리뷰를 분류하고, 답글 초안을 만든 뒤, 민감 리뷰는 운영자가 승인한다.

#### 엔드포인트
- `POST /api/v1/webhooks/reviews`
- `GET /api/v1/reviews`
- `GET /api/v1/reviews/{review_id}`
- `POST /api/v1/reviews/{review_id}/approve-reply`

#### 처리 방식
1. webhook이 리뷰 이벤트를 전송한다.
2. 백엔드는 리뷰 그래프를 실행한다.
3. 감도, 초안, escalation 여부를 계산한다.
4. review/job 저장
5. 필요 시 관리자가 답글 승인
6. audit log 기록

#### 상태
- `draft`
- `approved`

#### 현재 상태
- 구현 완료
- 실제 외부 플랫폼 답글 게시까지는 아직 없음

---

### 5.8 월간 리포트 생성

#### 목적
점포 또는 프로그램 단위로 월간 리포트 생성 요청을 기록하고 상태를 추적한다.

#### 엔드포인트
- `POST /api/v1/reports/monthly/generate`
- `GET /api/v1/reports`
- `GET /api/v1/jobs`
- `GET /api/v1/jobs/{job_id}`

#### 처리 방식
1. 관리자가 scope 기준으로 요청
2. report/job 저장
3. audit log 기록
4. 관리자 화면에서 job 상태 조회

#### 현재 상태
- 생성 요청과 상태 추적 구현 완료
- 실제 리포트 파일 생성/PDF 렌더링은 아직 없음

---

### 5.9 관리자 운영 화면

#### 목적
운영자가 승인 대기, 리뷰, 작업 상태, 발행 결과, variant 자산, 감사 로그를 한 화면에서 본다.

#### 프론트 위치
- `/admin`
- `frontend/components/admin-dashboard.tsx`

#### 주요 화면 기능
- draft 큐 목록
- 리뷰 큐 목록
- publish job 목록
- 리포트 목록
- publish result 목록
- variant asset 목록
- 콘텐츠 승인/반려/발행
- 리뷰 답글 승인
- observability summary
- audit log 목록
- request trace 목록

#### 현재 상태
- 구현 완료
- 고급 필터/정렬/페이지네이션은 아직 없음

---

### 5.10 감사 로그와 요청 추적

#### 목적
운영자가 민감 액션과 요청 흐름을 추적할 수 있게 한다.

#### 엔드포인트
- `GET /api/v1/audit-logs`
- `GET /api/v1/observability/requests`
- `GET /api/v1/observability/summary`

#### audit 기록 대상
- asset.upload_init
- content.generate
- content.approve
- content.reject
- content.publish_request
- review.ingest_webhook
- review.approve_reply
- report.generate_monthly

#### observability 항목
- request_id
- method
- path
- status_code
- duration_ms
- actor_role
- actor_id
- merchant_id

#### 현재 상태
- 구현 완료
- 현재는 in-memory 저장
- 외부 로그 스택 연동은 아직 없음

---

## 6. 내부 워크플로우 명세

### 콘텐츠 그래프
- 위치: `backend/app/graphs/content.py`
- 노드
  - `plan_content`
  - `generate_copy`
  - `validate_copy`

### 리뷰 그래프
- 위치: `backend/app/graphs/review.py`
- 노드
  - `assess_review_sensitivity`
  - `build_reply_draft`

### 상태 규칙
- 위치: `backend/app/domain/status_rules.py`
- 콘텐츠와 리뷰 상태 전이를 중앙에서 관리한다.

---

## 7. API 구조 요약

### 콘텐츠
- `POST /contents/generate`
- `GET /contents`
- `GET /contents/{content_id}`
- `POST /contents/{content_id}/approve`
- `POST /contents/{content_id}/reject`
- `POST /contents/{content_id}/publish`

### 자산
- `POST /assets/upload-init`
- `GET /assets`
- `GET /assets/{asset_id}`

### 리뷰
- `POST /webhooks/reviews`
- `GET /reviews`
- `GET /reviews/{review_id}`
- `POST /reviews/{review_id}/approve-reply`

### 리포트 / 작업
- `POST /reports/monthly/generate`
- `GET /reports`
- `GET /jobs`
- `GET /jobs/{job_id}`

### 발행 결과
- `GET /publish-results`
- `GET /publish-results/{publish_result_id}`

### 감사 / 관측
- `GET /audit-logs`
- `GET /observability/requests`
- `GET /observability/summary`

---

## 8. 현재 구현 상태 요약

### 구현 완료
- 점주 콘텐츠 요청 UI
- 관리자 운영 UI
- 콘텐츠/리뷰/자산/리포트/작업/발행결과 API
- LangGraph 기반 content/review workflow
- 상태 전이 규칙
- audit log
- request tracing / observability summary
- 운영 설정 스캐폴드
- SQLAlchemy/Celery/Redis/PostgreSQL 전환용 파일 구조

### 스텁 또는 미완료
- Celery task가 실제 후속 상태 전이를 수행하는 비동기 실행 경로
- Redis broker/result backend를 활용한 실작업 큐 소비
- object storage / signed URL
- 실제 Nano Banana API
- 실제 블로그/소셜 인증과 발행
- 실제 인증 계층
- 배포 자동화와 secret manager

---

## 9. 비기능 요구사항

- 모든 민감 액션은 감사 가능해야 한다.
- 잘못된 상태 전이는 차단해야 한다.
- 프론트와 백엔드는 역할 기준으로 화면과 권한이 분리되어야 한다.
- 테스트 없이 기능을 머지하지 않는다.
- request_id, job_id, publish_result_id, asset_id는 추적 가능해야 한다.
- 운영 전환 시 데모용 스텁 연동을 실제 외부 연동으로 교체해야 한다.

---

## 10. 구현 기준 파일

### 프론트엔드 핵심
- `frontend/components/merchant-dashboard.tsx`
- `frontend/components/admin-dashboard.tsx`
- `frontend/lib/api.ts`

### 백엔드 핵심
- `backend/app/main.py`
- `backend/app/api/v1/routes/*`
- `backend/app/services/*`
- `backend/app/graphs/*`
- `backend/app/domain/status_rules.py`
- `backend/app/core/settings.py`
- `backend/app/core/permissions.py`

### 운영 스캐폴드
- `backend/app/db/*`
- `backend/app/models/*`
- `backend/app/workers/*`
- `infra/docker-compose.yml`

---

## 11. 참조 문서

- [PRD.md](/Users/guswnd0432389/Desktop/marketing_AI/docs/PRD.md)
- [ARCHITECTURE.md](/Users/guswnd0432389/Desktop/marketing_AI/docs/ARCHITECTURE.md)
- [API_SPEC.md](/Users/guswnd0432389/Desktop/marketing_AI/docs/API_SPEC.md)
- [PROJECT_DIAGRAMS.md](/Users/guswnd0432389/Desktop/marketing_AI/docs/PROJECT_DIAGRAMS.md)
- [phases/index.json](/Users/guswnd0432389/Desktop/marketing_AI/phases/index.json)
