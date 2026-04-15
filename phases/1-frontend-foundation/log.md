# Phase 1 Log

## Completed
- `frontend/` 아래 Next.js App Router 워크스페이스를 추가했다.
- 대시보드 셸, 콘텐츠 생성 모달, 관리자 요약 카드 UI를 구현했다.
- `frontend/lib/api.ts`에서 백엔드 `contents/generate` API를 호출하도록 연결했다.
- 이미지 변형 옵션과 `nano_banana` provider 선택 UI를 추가했다.
- `npm run lint`, `npm run build` 검증을 마쳤다.

## Errors
- 초기 프론트 스캐폴드는 Tailwind 전제를 깔고 있었지만 실제 설치 상태와 맞지 않아 CSS module 기반으로 정리했다.
- JSX 내 literal `->` 표기로 빌드 오류가 발생해 문자열 표현을 수정했다.
- 로컬 서버는 기동됐지만 현재 실행 환경 제약상 동일 세션 밖 `curl` 검증은 제한됐다.

## Improvements
- 현재는 단일 셸 화면 중심이라 `(merchant)`, `(admin)` 라우트 그룹 분리가 필요하다.
- 실제 파일 업로드 UI와 서버 에러 표시를 붙여야 한다.
- approve/reject/publish 같은 운영 액션 화면이 아직 없다.
