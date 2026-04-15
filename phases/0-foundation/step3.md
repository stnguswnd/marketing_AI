# Step 3: phase-log

## 읽어야 할 파일
- `/docs/ADR.md`
- `/docs/ARCHITECTURE.md`
- `/docs/API_SPEC.md`
- `/tests/`

## 작업
Foundation 단계 결과를 로그 문서로 정리한다.
- 완료 항목
- 미해결 오류 및 로컬 제약
- 다음 Phase 개선 backlog

## Acceptance Criteria
```bash
python3 -m pytest tests
```

## 검증 절차
1. AC 커맨드 결과를 로그에 명시한다.
2. 다음 단계 진입 조건을 정리한다.
3. 결과를 index에 반영한다.

## 금지사항
- 성공한 것처럼 기록하지 마라. 이유: 하네스 로그는 운영 기록이다.
- 개선 backlog를 추상적으로 쓰지 마라. 이유: 다음 Phase 입력으로 재사용해야 한다.
