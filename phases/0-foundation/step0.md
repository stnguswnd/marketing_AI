# Step 0: project-setup

## 읽어야 할 파일
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- `/docs/API_SPEC.md`

## 작업
Python 백엔드 구현을 위한 최소 프로젝트 구조를 만든다.
- `app/`, `tests/` 디렉토리와 패키지 초기화 파일을 추가한다.
- `pyproject.toml`에 FastAPI, Pydantic v2, pytest 기준 의존성을 정의한다.
- 문서 기준 Python 3.12를 타겟으로 하되, 로컬 환경 차이는 별도 로그에 기록한다.

## Acceptance Criteria
```bash
python3 --version
python3 -m pytest
```

## 검증 절차
1. AC 커맨드를 실행한다.
2. 결과를 Phase 로그에 남긴다.
3. 성공 여부와 관계없이 `phases/0-foundation/index.json` 상태를 업데이트한다.

## 금지사항
- 문서와 다른 프레임워크를 도입하지 마라. 이유: ADR 위반이다.
- 외부 서비스 연동 코드를 넣지 마라. 이유: Foundation 단계 범위를 넘는다.
