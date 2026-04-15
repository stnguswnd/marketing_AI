# API 요청/응답 스키마 명세서

## 문서 목적
이 문서는 MVP 범위의 FastAPI 엔드포인트, 요청/응답 스키마, 실패 케이스, 권한 정책을 정의한다.

본 문서는 다음 원칙을 따른다.
- 모든 사용자 입력은 구조화된 API 스키마로 받는다.
- 외부 요청 진입점은 FastAPI API 또는 명시된 webhook endpoint로 제한한다.
- 라우터는 얇게 유지하고 비즈니스 로직은 `services/`와 `graphs/`에서 수행한다.
- 외부 발행 가능 콘텐츠와 민감 리뷰는 승인 또는 감사 대상이다.

## 공통 규칙

### Base path
`/api/v1`

### Content-Type
`application/json`

### 인증
- 점주/관리자 UI 호출은 인증된 세션 또는 Bearer token을 전제로 한다.
- webhook endpoint는 별도 서명 검증 또는 shared secret 검증이 필요하다.

### 공통 응답 원칙
- 성공 응답은 resource 데이터 또는 action result를 반환한다.
- 실패 응답은 `error_code`, `message`, `field_errors`를 포함할 수 있다.
- 장시간 작업은 즉시 완료 응답 대신 `job_id` 또는 `task_id`를 반환할 수 있다.

### 공통 에러 응답 예시
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "입력값을 확인해 주세요.",
  "field_errors": {
    "target_country": ["지원하지 않는 국가입니다."]
  }
}
```

## 권한 역할

### `merchant`
- 본인 소속 점포의 생성 요청, 초안 조회, 승인 요청 상태 확인 가능

### `admin`
- 다수 점포 관리, 승인/반려, 리포트 조회, 민감 리뷰 검토 가능

### `operator`
- 운영 대행 관점에서 점포 대신 요청 생성 및 검토 가능

### `webhook`
- 외부 플랫폼 이벤트 전송 전용

## 데이터 타입

### 공통 enum

#### `CountryCode`
- `JP`
- `US`
- `CN`
- `TW`
- `HK`

#### `PlatformType`
- `instagram`
- `google_business`
- `xiaohongshu`
- `blog`

#### `ContentGoal`
- `store_visit`
- `awareness`
- `seasonal_promotion`
- `review_response`

#### `ToneType`
- `friendly`
- `professional`
- `trendy`
- `calm`

#### `ContentStatus`
- `draft`
- `approved`
- `scheduled`
- `published`
- `rejected`

#### `ReviewSensitivity`
- `low`
- `medium`
- `high`

#### `JobStatus`
- `queued`
- `running`
- `succeeded`
- `failed`

#### `ImageVariantProvider`
- `none`
- `nano_banana`

## 1. 콘텐츠 생성

### `POST /contents/generate`
구조화된 입력으로 콘텐츠 초안 생성을 요청한다.

### 권한
- `merchant`
- `operator`
- `admin`

### Request Body
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

### Request Schema
| 필드 | 타입 | 필수 | 규칙 |
|------|------|------|------|
| `merchant_id` | string | Y | 요청 대상 점포 ID |
| `target_country` | `CountryCode` | Y | 지원 국가만 허용 |
| `platform` | `PlatformType` | Y | 지원 플랫폼만 허용 |
| `goal` | `ContentGoal` | Y | 콘텐츠 목적 |
| `input_brief` | string | Y | 10~500자 |
| `website_url` | string | N | `http` 또는 `https` URL |
| `tone` | `ToneType` | N | 미입력 시 기본 톤 사용 |
| `must_include` | string[] | N | 최대 10개 |
| `must_avoid` | string[] | N | 최대 10개 |
| `uploaded_asset_ids` | string[] | N | 최대 5개 |
| `publish_mode` | string | Y | MVP에서는 `draft`만 허용 |

### Success Response `201`
```json
{
  "content_id": "content_123",
  "merchant_id": "m_123",
  "status": "draft",
  "approval_required": true,
  "job_id": "job_123",
  "message": "콘텐츠 초안이 생성되었습니다."
}
```

### 실패 케이스
- `400 VALIDATION_ERROR`
- `403 FORBIDDEN_MERCHANT_ACCESS`
- `404 MERCHANT_NOT_FOUND`
- `409 INVALID_PLATFORM_COMBINATION`
- `422 INVALID_ASSET_REFERENCE`
- `500 CONTENT_GENERATION_FAILED`

## 2. 콘텐츠 상세 조회

### `GET /contents/{content_id}`
콘텐츠 초안 또는 게시 이력을 조회한다.

### 권한
- `merchant`
- `operator`
- `admin`

### Success Response `200`
```json
{
  "content_id": "content_123",
  "merchant_id": "m_123",
  "target_country": "JP",
  "platform": "instagram",
  "goal": "store_visit",
  "status": "draft",
  "title": "봄 시즌 부산 카페 추천",
  "body": "벚꽃 시즌, 부산 여행 중 잠시 쉬어가기 좋은 카페입니다.",
  "hashtags": ["#부산여행", "#말차라떼"],
  "must_include": ["말차라떼", "부산 여행"],
  "must_avoid": ["최고", "무조건"],
  "approval_required": true,
  "created_at": "2026-04-15T14:00:00Z",
  "updated_at": "2026-04-15T14:01:30Z"
}
```

### 실패 케이스
- `403 FORBIDDEN_CONTENT_ACCESS`
- `404 CONTENT_NOT_FOUND`

## 3. 콘텐츠 초안 삭제

### `DELETE /contents/{content_id}`
점주가 아직 승인/반려/발행 전인 `draft` 초안을 삭제한다.

### 권한
- `merchant`
- `operator`
- `admin`

### Success Response `200`
```json
{
  "content_id": "content_123",
  "deleted": true,
  "message": "콘텐츠 초안을 삭제했습니다."
}
```

### 실패 케이스
- `403 FORBIDDEN_DELETE`
- `404 CONTENT_NOT_FOUND`
- `409 INVALID_CONTENT_STATUS_TRANSITION`

- 현재 구현은 hard delete 대신 `deleted` 상태로 전환하는 soft delete 방식이며, 일반 콘텐츠 조회/목록에서는 숨긴다.

## 4. 콘텐츠 승인

### `POST /contents/{content_id}/approve`
초안을 승인 상태로 전환한다.

### 권한
- `merchant`
- `admin`
- `operator`

### Request Body
```json
{
  "approver_id": "u_123",
  "comment": "문구 확인 완료"
}
```

### Success Response `200`
```json
{
  "content_id": "content_123",
  "status": "approved",
  "approved_by": "u_123",
  "approved_at": "2026-04-15T14:10:00Z"
}
```

### 실패 케이스
- `403 FORBIDDEN_APPROVAL`
- `404 CONTENT_NOT_FOUND`
- `409 INVALID_CONTENT_STATUS`

## 5. 콘텐츠 반려

### `POST /contents/{content_id}/reject`
초안을 반려하고 사유를 기록한다.

### 권한
- `merchant`
- `admin`
- `operator`

### Request Body
```json
{
  "reviewer_id": "u_123",
  "reason": "국가별 표현 가이드와 맞지 않습니다."
}
```

### Success Response `200`
```json
{
  "content_id": "content_123",
  "status": "rejected",
  "rejected_by": "u_123",
  "reason": "국가별 표현 가이드와 맞지 않습니다."
}
```

### 실패 케이스
- `403 FORBIDDEN_REJECTION`
- `404 CONTENT_NOT_FOUND`
- `409 INVALID_CONTENT_STATUS`

## 6. 게시 요청

### `POST /contents/{content_id}/publish`
승인된 콘텐츠에 대해 게시 작업을 요청한다.

### 권한
- `merchant`
- `admin`
- `operator`

### Request Body
```json
{
  "publish_at": "2026-04-16T09:00:00Z",
  "apply_image_variant": true,
  "image_variant_provider": "nano_banana",
  "source_asset_ids": ["asset_1", "asset_2"]
}
```

### 규칙
- `publish_at`이 없으면 즉시 게시 요청으로 간주한다.
- 상태가 `approved`가 아니면 요청할 수 없다.
- `apply_image_variant=true`이면 업로드된 입력 이미지 또는 지정된 `source_asset_ids`를 기준으로 variant 생성 job을 함께 만든다.
- 이미지 variant는 원본을 덮어쓰지 않고 publish payload에 첨부할 variant asset으로 저장한다.

### Success Response `202`
```json
{
  "content_id": "content_123",
  "status": "published",
  "job_id": "job_publish_123",
  "publish_at": "2026-04-16T09:00:00Z",
  "image_variant_job_id": "job_image_123",
  "image_variant_provider": "nano_banana"
}
```

- 현재 데모/하네스 구현에서는 실제 외부 채널 연동 대신 스텁 어댑터를 사용하므로, 즉시 발행 가능한 요청은 같은 응답 안에서 `published` 상태를 반환할 수 있다.

### 실패 케이스
- `403 FORBIDDEN_PUBLISH`
- `404 CONTENT_NOT_FOUND`
- `409 CONTENT_NOT_APPROVED`
- `422 INVALID_SOURCE_ASSET_REFERENCE`
- `500 PUBLISH_REQUEST_FAILED`

## 5-1. 자산 업로드 초기화

### `POST /assets/upload-init`
콘텐츠 생성 전 이미지 업로드를 위한 asset 발급을 요청한다.

### 권한
- `merchant`
- `operator`
- `admin`

### Request Body
```json
{
  "merchant_id": "m_123",
  "filename": "menu-photo.jpg",
  "content_type": "image/jpeg",
  "size_bytes": 2481200
}
```

### Success Response `201`
```json
{
  "asset_id": "asset_123",
  "upload_url": "http://127.0.0.1:8000/api/v1/assets/asset_123/binary",
  "asset_type": "source"
}
```

- init 단계에서는 asset row를 `pending_upload` 상태로 만들고, 실제 파일 바이너리는 다음 단계에서 업로드한다.

### `POST /assets/{asset_id}/binary`
`multipart/form-data` 로 실제 이미지 파일을 업로드한다.

### 권한
- `merchant`
- `operator`
- `admin`

### Form Data
- `file`: image/jpeg | image/png | image/webp

### Success Response `200`
```json
{
  "asset_id": "asset_123",
  "status": "uploaded",
  "preview_url": "http://127.0.0.1:8000/api/v1/assets/asset_123/binary",
  "updated_at": "2026-04-15T14:05:00Z"
}
```

### 실패 케이스
- `400 EMPTY_ASSET_FILE`
- `403 FORBIDDEN_ASSET_ACCESS`
- `404 ASSET_NOT_FOUND`
- `413 ASSET_TOO_LARGE`
- `415 UNSUPPORTED_ASSET_TYPE`

### 실패 케이스
- `400 VALIDATION_ERROR`
- `403 FORBIDDEN_MERCHANT_ACCESS`
- `413 ASSET_TOO_LARGE`
- `415 UNSUPPORTED_ASSET_TYPE`

## 6. 리뷰 이벤트 수신 webhook

### `POST /webhooks/reviews`
외부 리뷰 플랫폼에서 리뷰 이벤트를 수신한다.

### 권한
- `webhook`

### Request Body
```json
{
  "platform": "google_business",
  "external_review_id": "rv_123",
  "merchant_id": "m_123",
  "author_name": "guest",
  "rating": 2,
  "language": "ja",
  "review_text": "서비스가 아쉬웠어요.",
  "reviewed_at": "2026-04-15T12:00:00Z"
}
```

### Success Response `202`
```json
{
  "review_id": "review_123",
  "job_id": "job_review_123",
  "status": "queued"
}
```

### 실패 케이스
- `401 INVALID_WEBHOOK_SIGNATURE`
- `400 INVALID_WEBHOOK_PAYLOAD`
- `404 MERCHANT_NOT_FOUND`

## 7. 리뷰 상세 조회

### `GET /reviews/{review_id}`
리뷰 원문, 민감도, 답글 초안, 상태를 조회한다.

### 권한
- `admin`
- `operator`

### Success Response `200`
```json
{
  "review_id": "review_123",
  "merchant_id": "m_123",
  "platform": "google_business",
  "rating": 2,
  "language": "ja",
  "review_text": "서비스가 아쉬웠어요.",
  "sensitivity": "high",
  "status": "draft",
  "reply_draft": "불편을 드려 죄송합니다. 더 나은 경험을 위해 개선하겠습니다.",
  "escalated": true,
  "created_at": "2026-04-15T12:00:05Z"
}
```

### 실패 케이스
- `403 FORBIDDEN_REVIEW_ACCESS`
- `404 REVIEW_NOT_FOUND`

## 8. 리뷰 답글 승인

### `POST /reviews/{review_id}/approve-reply`
민감 리뷰 또는 일반 리뷰 답글 초안을 승인한다.

### 권한
- `admin`
- `operator`

### Request Body
```json
{
  "approver_id": "u_123",
  "reply_text": "불편을 드려 죄송합니다. 말씀 주신 내용을 확인해 개선하겠습니다."
}
```

### 규칙
- `reply_text`를 보내면 승인 전 최종 문안으로 덮어쓴다.
- 미전송 시 기존 draft 문안을 승인한다.

### Success Response `200`
```json
{
  "review_id": "review_123",
  "status": "approved",
  "approved_reply_text": "불편을 드려 죄송합니다. 말씀 주신 내용을 확인해 개선하겠습니다."
}
```

### 실패 케이스
- `403 FORBIDDEN_REVIEW_APPROVAL`
- `404 REVIEW_NOT_FOUND`
- `409 INVALID_REVIEW_STATUS`

## 9. 월간 리포트 생성 요청

### `POST /reports/monthly/generate`
점포 또는 사업 단위 월간 성과 리포트 생성을 요청한다.

### 권한
- `admin`
- `operator`

### Request Body
```json
{
  "scope_type": "merchant",
  "scope_id": "m_123",
  "year": 2026,
  "month": 4
}
```

### Request Schema
| 필드 | 타입 | 필수 | 규칙 |
|------|------|------|------|
| `scope_type` | string | Y | `merchant` 또는 `program` |
| `scope_id` | string | Y | 점포 또는 사업 식별자 |
| `year` | integer | Y | 4자리 연도 |
| `month` | integer | Y | 1~12 |

### Success Response `202`
```json
{
  "report_id": "report_123",
  "job_id": "job_report_123",
  "status": "succeeded"
}
```

- 현재 데모/하네스 구현에서는 리포트 생성 작업을 worker 비동기 완료 대신 즉시 완료 상태로 기록한다.

### 실패 케이스
- `403 FORBIDDEN_REPORT_ACCESS`
- `404 REPORT_SCOPE_NOT_FOUND`
- `409 REPORT_ALREADY_EXISTS`

## 10. 작업 상태 조회

### `GET /jobs/{job_id}`
비동기 작업 상태를 조회한다.

### 권한
- `merchant`
- `operator`
- `admin`

### Success Response `200`
```json
{
  "job_id": "job_123",
  "job_type": "content_generate",
  "status": "succeeded",
  "resource_type": "content",
  "resource_id": "content_123",
  "created_at": "2026-04-15T14:00:00Z",
  "updated_at": "2026-04-15T14:01:30Z"
}
```

### 실패 케이스
- `403 FORBIDDEN_JOB_ACCESS`
- `404 JOB_NOT_FOUND`

## Pydantic 스키마 권장 분리

### `backend/app/schemas/content.py`
- `ContentGenerateRequest`
- `ContentGenerateResponse`
- `ContentDetailResponse`
- `ContentApproveRequest`
- `ContentRejectRequest`
- `ContentPublishRequest`

### `backend/app/schemas/review.py`
- `ReviewWebhookRequest`
- `ReviewDetailResponse`
- `ReviewApproveReplyRequest`

### `backend/app/schemas/report.py`
- `MonthlyReportGenerateRequest`
- `MonthlyReportGenerateResponse`

### `backend/app/schemas/job.py`
- `JobStatusResponse`

### `backend/app/schemas/common.py`
- `ErrorResponse`
- 공통 enum 정의

## 라우터 구성 권장안

### `backend/app/api/v1/content.py`
- `POST /contents/generate`
- `GET /contents/{content_id}`
- `POST /contents/{content_id}/approve`
- `POST /contents/{content_id}/reject`
- `POST /contents/{content_id}/publish`

### `backend/app/api/v1/review.py`
- `POST /webhooks/reviews`
- `GET /reviews/{review_id}`
- `POST /reviews/{review_id}/approve-reply`

### `backend/app/api/v1/report.py`
- `POST /reports/monthly/generate`

### `backend/app/api/v1/job.py`
- `GET /jobs/{job_id}`

## 테스트 체크리스트
- 요청 스키마 validation 성공/실패 케이스
- 권한 없는 사용자의 접근 차단
- 미지원 국가/플랫폼 조합 차단
- 승인 전 게시 차단
- webhook 서명 실패 처리
- 비동기 job 생성 및 상태 조회
- 민감 리뷰 escalation 여부 검증

## 차기 확장 후보
- 콘텐츠 수정 API
- 승인 이력 조회 API
- 감사 로그 조회 API
- 자산 업로드 API 명세
- 관리자 대시보드 집계 API
