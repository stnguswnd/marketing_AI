# 프론트 모달 필드 명세서

## 문서 목적
이 문서는 점주용 구조화 입력 UI의 기준 명세서다. 챗형 입력 대신 모달/폼 기반으로 콘텐츠 생성 요청을 수집하고, 백엔드 API 스키마와 일관되게 연결하는 것을 목표로 한다.

초기 MVP에서는 `콘텐츠 생성 모달`을 최우선 범위로 정의한다.

프론트 구현은 `frontend/` 아래 Next.js App Router를 기준으로 하며, 점주용 라우트와 관리자용 라우트를 라우트 그룹으로 분리한다.

## 설계 원칙
- 사용자는 자유 문장 대신 구조화된 필드를 입력한다.
- 한 번의 모달에서 너무 많은 결정을 요구하지 않는다.
- 필수 입력과 선택 입력을 명확히 구분한다.
- UI 필드 이름은 사용자가 이해하기 쉬운 용어를 쓰고, API 필드는 서버 표준 스키마를 따른다.
- 생성과 게시는 분리한다. 기본값은 `draft`다.

## 대상 화면
- 점주 대시보드의 "콘텐츠 만들기" 진입 버튼
- 점포 상세 화면의 "새 콘텐츠 요청" 진입 버튼
- 관리자 화면의 대행 생성 플로우는 같은 필드를 쓰되 `merchant_id` 선택 UI를 추가할 수 있다

## 권장 라우트
- 점주 콘텐츠 생성: `frontend/app/(merchant)/contents/new/page.tsx`
- 관리자 대행 생성: `frontend/app/(admin)/merchants/[merchantId]/contents/new/page.tsx`
- 공통 모달 컴포넌트: `frontend/components/content/content-create-modal.tsx`

## 1차 MVP 모달

### 모달명
`콘텐츠 생성`

### 목적
특정 국가와 플랫폼에 맞는 마케팅 콘텐츠 초안을 생성 요청한다.

### 제출 엔드포인트
`POST /api/v1/contents/generate`

### 기본 제출 결과
- 성공 시: draft 생성 완료, 승인 대기 또는 후속 검토 필요 상태 반환
- 실패 시: 필드 오류 또는 시스템 오류 메시지 반환

## 폼 단계 구성

### Step 1. 대상 설정
- 대상 국가
- 플랫폼
- 목표

### Step 2. 요청 내용
- 강조하고 싶은 내용
- 톤 앤 매너
- 꼭 포함할 표현
- 피해야 할 표현

### Step 3. 참고 자료
- 홈페이지 URL
- 이미지 업로드
- 발행 시 이미지 변형 옵션

### Step 4. 검토 후 제출
- 입력 요약
- 누락 경고
- 제출

## 필드 명세

| UI 라벨 | 필드 키 | 타입 | 필수 | 입력 방식 | 설명 |
|---------|---------|------|------|-----------|------|
| 대상 국가 | `target_country` | enum | Y | select | 콘텐츠 타겟 국가 |
| 플랫폼 | `platform` | enum | Y | segmented/select | 게시 대상 플랫폼 |
| 목표 | `goal` | enum | Y | radio card | 콘텐츠 목적 |
| 강조 내용 | `input_brief` | string | Y | textarea | 이번 콘텐츠에서 강조할 핵심 메시지 |
| 홈페이지 URL | `website_url` | string(url) | N | text input | 점포 또는 캠페인 참고 URL |
| 톤 앤 매너 | `tone` | enum | N | select | 문체 스타일 |
| 꼭 포함할 표현 | `must_include` | string[] | N | token input | 반드시 포함할 키워드 |
| 피해야 할 표현 | `must_avoid` | string[] | N | token input | 금지 또는 회피 표현 |
| 업로드 이미지 | `uploaded_asset_ids` | string[] | N | file uploader | 사전 업로드 후 asset id로 매핑 |
| 발행 시 이미지 변형 | `apply_image_variant` | boolean | N | checkbox | 발행 직전 입력 이미지 기반 변형 실행 여부 |
| 이미지 변형 공급자 | `image_variant_provider` | enum | N | select | 이미지 변형 provider 선택 |
| 발행 방식 | `publish_mode` | enum | Y | hidden/default | MVP 기본값은 `draft` |

## 서버 고정 필드
아래 값은 사용자 직접 입력이 아니라 앱 상태 또는 인증 컨텍스트에서 주입한다.

| 필드 키 | 소스 | 설명 |
|---------|------|------|
| `merchant_id` | 로그인 세션 또는 현재 점포 컨텍스트 | 요청 대상 점포 식별자 |
| `requested_by` | 인증 컨텍스트 | 요청 사용자 식별자 |
| `locale` | 앱 설정 | 표시 언어 또는 기본 로캘 |

## 이미지 처리 관련 필드
아래 값은 콘텐츠 생성 시점에 저장되거나 발행 시점에 추가로 입력될 수 있다.

| 필드 키 | 설명 |
|---------|------|
| `uploaded_asset_ids` | 사용자가 업로드한 원본 이미지 asset id |
| `apply_image_variant` | 발행 시 입력 이미지를 기반으로 variant를 만들지 여부 |
| `image_variant_provider` | variant 생성 provider. 초기값은 `nano_banana` 또는 `none` |

## Enum 정의

### `target_country`
| 값 | 라벨 |
|----|------|
| `JP` | 일본 |
| `US` | 미국 |
| `CN` | 중국 |
| `TW` | 대만 |
| `HK` | 홍콩 |

초기 MVP에서는 운영 대상 국가만 노출한다. 지원하지 않는 국가는 UI에서 비활성 또는 숨김 처리한다.

### `platform`
| 값 | 라벨 |
|----|------|
| `instagram` | Instagram |
| `google_business` | Google Business Profile |
| `xiaohongshu` | Xiaohongshu |
| `blog` | 블로그/웹 게시용 |

### `goal`
| 값 | 라벨 | 설명 |
|----|------|------|
| `store_visit` | 매장 방문 유도 | 오프라인 방문 중심 |
| `awareness` | 점포 인지도 확산 | 신규 고객 노출 확대 |
| `seasonal_promotion` | 시즌 프로모션 홍보 | 특정 시즌/이벤트 강조 |
| `review_response` | 리뷰 유입 보조 | 후기와 신뢰 메시지 강화 |

### `tone`
| 값 | 라벨 |
|----|------|
| `friendly` | 친근한 느낌 |
| `professional` | 신뢰감 있는 느낌 |
| `trendy` | 감각적인 느낌 |
| `calm` | 차분한 느낌 |

### `publish_mode`
| 값 | 설명 |
|----|------|
| `draft` | 초안 저장 후 승인 대기 |

MVP에서는 UI에서 수정할 수 없고 기본값으로 고정한다.

### `image_variant_provider`
| 값 | 설명 |
|----|------|
| `none` | 이미지 변형 없음 |
| `nano_banana` | 입력 이미지 기반 보정/변형 이미지 생성 |

## 필드별 상세 규칙

### `target_country`
- 단일 선택만 허용한다.
- 선택 전에는 다음 단계로 이동할 수 없다.

### `platform`
- 국가와 무관하게 노출 가능하되, 운영 정책상 미지원 조합은 선택 불가 처리한다.
- 미지원 조합 예시:
  - `target_country=JP`, `platform=xiaohongshu`

### `goal`
- 카드형 선택 UI를 사용한다.
- 선택 시 하단 도움말에 생성 방향 설명을 보여준다.

### `input_brief`
- 최소 10자, 최대 500자
- 줄바꿈 허용
- placeholder 예시:
  `벚꽃 시즌에 맞춰 말차라떼와 푸딩을 강조하고 싶어요. 부산 여행 중 들르기 좋은 카페라는 느낌을 담아주세요.`
- 금지:
  - 빈 값 제출
  - 의미 없는 반복 문자

### `website_url`
- 유효한 `http` 또는 `https` URL만 허용
- 입력하지 않아도 제출 가능
- 입력 시 서버에서 점포/브랜드 참고 정보 수집에 사용될 수 있다

### `tone`
- 미선택 허용
- 미선택 시 서버 기본값 또는 점포 기본 브랜드 톤을 사용한다

### `must_include`
- 최대 10개
- 각 항목 1자 이상 30자 이하
- 중복값 제거
- 해시태그 기호 포함은 허용하되 저장 시 trim 처리

### `must_avoid`
- 최대 10개
- 각 항목 1자 이상 30자 이하
- 중복값 제거
- 운영 정책상 금지어 룰셋과 함께 사용될 수 있다

### `uploaded_asset_ids`
- 파일 업로드는 별도 자산 업로드 API 이후 asset id 배열로 관리한다
- 허용 파일:
  - jpg
  - jpeg
  - png
  - webp
- 최대 업로드 수:
  - 5개
- 파일당 최대 크기:
  - 10MB

### `apply_image_variant`
- 기본값은 `false`
- 사용자가 체크하면 발행 단계에서 이미지 variant 생성 옵션을 함께 저장한다
- 업로드 이미지가 없는 경우 활성화할 수 없다

### `image_variant_provider`
- `apply_image_variant=true`일 때만 노출한다
- 초기 MVP 기본값은 `nano_banana`
- 향후 provider 추가 가능성을 고려해 enum으로 관리한다

## 조건부 UX 규칙
- `platform=instagram`이면 이미지 업로드 영역을 강조 표시한다.
- `platform=google_business`이면 설명 문구에 검색/지도 노출용 초안 생성 가능 안내를 추가한다.
- `goal=seasonal_promotion`이면 입력 가이드에 시즌명, 기간, 대표 메뉴를 포함하라고 안내한다.
- `website_url` 미입력 상태에서도 제출은 가능하지만, 참고 자료 부족 경고를 표시할 수 있다.
- 업로드 이미지가 하나 이상 있으면 "발행 시 이미지 보정/변형" 옵션을 노출할 수 있다.
- `apply_image_variant=true`이면 "원본을 대체하지 않고 variant를 추가 생성한다"는 안내 문구를 보여준다.

## 검증 규칙

### 클라이언트 검증
- 필수값 누락 여부
- 문자열 길이 제한
- URL 형식 검증
- 업로드 파일 개수/크기/형식 검증
- enum 외 값 차단
- 업로드 이미지 없이 이미지 변형 옵션을 활성화하지 못하게 검증

### 서버 검증
- 점포 접근 권한 확인
- 지원 국가/플랫폼 조합 검증
- asset id 소유권 및 유효성 검증
- 운영 정책상 금지 입력값 검증
- 이미지 변형 요청 시 provider 지원 여부 및 source asset 존재 여부 검증

## 에러 메시지 가이드
| 상황 | 메시지 예시 |
|------|-------------|
| 국가 미선택 | `대상 국가를 선택해 주세요.` |
| 플랫폼 미선택 | `플랫폼을 선택해 주세요.` |
| 목표 미선택 | `콘텐츠 목적을 선택해 주세요.` |
| 강조 내용 누락 | `강조하고 싶은 내용을 입력해 주세요.` |
| URL 형식 오류 | `홈페이지 주소 형식이 올바르지 않습니다.` |
| 업로드 제한 초과 | `이미지는 최대 5개까지 업로드할 수 있습니다.` |
| 이미지 변형 조건 오류 | `이미지 변형을 사용하려면 먼저 이미지를 업로드해 주세요.` |
| 서버 정책 불일치 | `선택한 국가와 플랫폼 조합은 현재 지원하지 않습니다.` |

## 제출 payload 예시
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
  "apply_image_variant": true,
  "image_variant_provider": "nano_banana",
  "publish_mode": "draft"
}
```

## 응답 처리 기준

### 성공 응답 예시
```json
{
  "content_id": "content_123",
  "status": "draft",
  "approval_required": true,
  "message": "콘텐츠 초안이 생성되었습니다."
}
```

### 실패 응답 예시
```json
{
  "error_code": "INVALID_PLATFORM_COMBINATION",
  "message": "선택한 국가와 플랫폼 조합은 현재 지원하지 않습니다.",
  "field_errors": {
    "platform": ["지원하지 않는 조합입니다."]
  }
}
```

## 화면 상태 정의
- `idle`: 초기 진입 상태
- `editing`: 입력 중
- `validating`: 제출 전 검증 중
- `submitting`: API 요청 중
- `success`: 생성 요청 성공
- `error`: 검증 오류 또는 서버 오류

## CTA 규칙
- 기본 CTA: `초안 생성하기`
- 보조 CTA: `취소`
- `submitting` 상태에서는 CTA를 비활성화하고 중복 제출을 막는다.
- 성공 후에는 `초안 보기` 또는 `계속 작성하기` 액션을 제공할 수 있다.

## 추적 이벤트
분석 및 운영 추적을 위해 최소 아래 이벤트를 남긴다.

| 이벤트명 | 발생 시점 |
|---------|-----------|
| `content_modal_opened` | 모달 오픈 |
| `content_modal_step_changed` | 스텝 이동 |
| `content_asset_uploaded` | 이미지 업로드 완료 |
| `content_image_variant_toggled` | 이미지 변형 옵션 변경 |
| `content_generate_submitted` | 제출 버튼 클릭 |
| `content_generate_succeeded` | 성공 응답 수신 |
| `content_generate_failed` | 실패 응답 수신 |

## 차기 확장 후보
- 국가별 추천 표현 preset
- 플랫폼별 길이 제한 실시간 안내
- 관리자 대행 생성 모드에서 `merchant_id` 검색 선택
- 리뷰 답글 생성 모달 명세
- 월간 리포트 생성 모달 명세
