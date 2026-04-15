# Step 2: workflow-tests

## 읽어야 할 파일
- `/docs/API_SPEC.md`
- `/app/`
- `/tests/`

## 작업
핵심 플로우 테스트를 추가한다.
- 콘텐츠 생성, 조회, 승인, 반려, 게시
- 리뷰 webhook 수신, 조회, 답글 승인
- 리포트 생성, 잡 상태 조회
- 주요 validation/권한/상태 충돌 테스트

## Acceptance Criteria
```bash
python3 -m pytest tests
```

## 검증 절차
1. AC 커맨드를 실행한다.
2. 실패 시 원인과 누락 범위를 Phase 로그에 적는다.
3. 결과에 따라 step 상태를 갱신한다.

## 금지사항
- 테스트를 문서 대체물로 쓰지 마라. 이유: 검증과 설계 기록은 분리해야 한다.
- 네트워크 의존 테스트를 추가하지 마라. 이유: 로컬 하네스 재현성을 해친다.
