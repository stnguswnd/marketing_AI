# Phase 3 Log

## Completed
- 루트 화면을 역할 선택 허브로 바꾸고 `merchant`, `admin` 라우트를 분리했다.
- 점주 화면에서 파일 선택 후 `assets/upload-init`를 호출하는 업로드 UI를 연결했다.
- 수동 `asset id` 입력을 제거하고 등록된 자산 목록을 화면에서 관리하도록 바꿨다.
- 점주 화면에 최근 생성한 draft 결과 패널을 추가했다.
- 점주가 자기 점포 콘텐츠를 직접 승인, 반려, 발행할 수 있도록 UI와 API 권한을 옮겼다.
- 점주가 민감 리뷰 답글을 직접 승인할 수 있도록 review 접근/승인 권한을 merchant scope로 변경했다.
- 점주 화면에서 월간 리포트 생성, 최근 job/review/publish result 요약을 확인하도록 운영 패널을 확장했다.
- 기존 단일 `dashboard-shell`과 프론트 내부 중복 phase 문서를 제거했다.
- `npm run lint`, `npm run build`를 모두 통과했다.

## Errors
- 구현 중 TypeScript에서 `int` 타입 표기가 들어가 빌드 전에 `number`로 수정했다.
- React hook dependency 경고가 있어 초기 bootstrap 로직을 effect 내부 비동기 블록으로 다시 정리했다.

## Remaining
- 필드 단위 검증 메시지와 step 분리는 아직 단순한 폼 수준이다.
- asset 업로드는 아직 `upload-init` 메타데이터 등록 단계이며 실제 object storage 업로드는 아니다.
- 실제 채널 발행 성공/실패를 점주 화면에서 더 세밀하게 추적하는 UI는 추가 여지가 있다.
