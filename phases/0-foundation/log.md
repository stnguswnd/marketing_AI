# Phase 0 Log

## Completed
- `pyproject.toml`, `app/`, `tests/`, `phases/` 기본 구조를 추가했다.
- FastAPI 라우터, 스키마, 서비스, in-memory 저장소 기반의 백엔드 골격을 만들었다.
- `pytest` 계약 테스트를 추가했고, 현재는 전체 테스트가 통과한다.
- `python3 -m py_compile`로 Python 문법 검증을 마쳤다.
- 실행 가이드와 핵심 아키텍처 문서를 정리했다.

## Errors
- 초기에는 Python 환경에 `fastapi`, `pydantic`, `pytest`가 없어 테스트 실행이 막혔다.
- Python bytecode cache가 기본 경로에 쓰이지 않아 `PYTHONPYCACHEPREFIX=/tmp/codex_pycache`로 우회했다.
- Python 3.9 환경에서 `datetime.UTC` 호환성 문제가 있어 `timezone.utc` 기준으로 수정했다.

## Improvements
- `.env.example`과 설치 방식을 더 명확히 정리할 필요가 있다.
- in-memory 저장소는 이후 phase에서 DB 저장소로 교체해야 한다.
- 테스트 인증 shim은 실제 인증 체계로 대체되어야 한다.
