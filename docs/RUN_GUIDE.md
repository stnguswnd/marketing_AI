# 실행 가이드

## 목적
이 문서는 저장소를 새로 받은 뒤 `backend/`, `frontend/` 구조에서 서비스를 실행하는 절차를 정리한다.

현재 기준 기본 실행 방식은 `docker compose` 이다.

- `frontend/`: Next.js App Router
- `backend/`: FastAPI + LangGraph + SQLAlchemy + Celery
- `infra/docker-compose.yml`: Postgres, Redis, backend, worker, frontend
- `backend/scripts/start_backend.sh`: 컨테이너 시작 시 DB schema/seed 자동 적용

현재 기준으로 아직 미완료인 항목은 다음과 같다.
- 실제 파일 업로드 UI
- 실제 `Nano Banana` 외부 API 연동
- 실제 플랫폼 publish adapter 연동

## 사전 준비
- Git
- Python 3.9 이상 권장
- Node.js 18 이상 권장
- npm

## 1. 저장소 받기
```bash
git clone <repo-url>
cd harness_framework
```

## 2. 권장 실행: Docker Compose
프로젝트 루트에서 실행한다.

```bash
docker compose -f infra/docker-compose.yml up --build
```

정상 기준:
- `postgres`, `redis`, `backend`, `worker`, `frontend` 컨테이너가 모두 뜬다.
- backend 시작 전에 DB schema와 seed 계정이 자동 생성된다.

접속 주소:
- 프론트: `http://127.0.0.1:3000`
- 백엔드: `http://127.0.0.1:8000`
- API base: `http://127.0.0.1:8000/api/v1`

로그인 계정:
- 관리자: `test1@email.com / 12345678`
- 점주: `test2@email.com / 12345678`
- 점주: `test3@email.com / 12345678`
- 점주: `test4@email.com / 12345678`

## 3. 로컬 개발 실행
컨테이너 대신 각 서비스를 따로 띄우고 싶을 때만 사용한다.

### 백엔드 설치

```bash
cd backend
python3 -m pip install -e '.[dev]'
```

### 백엔드 테스트
```bash
cd backend
python3 -m pytest
```

### 프론트 설치
```bash
cd frontend
npm install
```

### 프론트 검증
```bash
cd frontend
npm run lint
npm run build
```

### 로컬 DB seed
Docker로 Postgres만 띄운 뒤 seed를 넣는다.

```bash
docker compose -f infra/docker-compose.yml up -d postgres redis
cd backend
python3 scripts/init_mock_db.py
```

### 백엔드 실행
```bash
cd backend
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 프론트 실행
```bash
cd frontend
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1 npm run dev -- --hostname 127.0.0.1 --port 3000
```

## 4. 현재 데모에서 확인 가능한 것
- 점주용 콘텐츠 생성 모달
- 관리자 감사/관측/점포 요약 화면
- 구조화 필드 입력
- 로그인 폼과 test1~test4 계정 진입
- `이미지 변형 사용` 토글
- `nano_banana` provider 선택
- draft 생성 요청
- 점주별 예시 게시 카드와 예시 이미지

## 5. 현재 구현 제한
- 운영 데이터 본체는 아직 메모리 저장소 기반이다.
- 계정과 점포 정보는 PostgreSQL seed를 사용한다.
- `Nano Banana`는 실제 외부 API 호출이 아니라 스텁 어댑터다.
- 발행 adapter는 아직 실제 외부 플랫폼 payload 연동까지는 가지 않았다.

## 6. 트러블슈팅

### `docker compose up --build`에서 backend가 바로 안 뜰 때
backend는 시작 전에 `python scripts/init_mock_db.py`를 반복 실행한다. 보통 Postgres healthcheck가 끝나면 자동으로 붙는다.

```bash
docker compose -f infra/docker-compose.yml logs -f postgres backend
```

### 포트 충돌이 날 때
기존 로컬 dev server를 먼저 내리거나 Docker Compose만 사용한다.

### 프론트에서 API 요청이 실패할 때
프론트 환경변수가 올바른지 확인한다.

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## 7. 다음 구현 우선순위
1. 실제 asset 업로드 UI 및 storage 연동
2. 실제 `Nano Banana` API 어댑터 구현
3. publish adapter에서 variant asset 연결
4. report graph 실제 구현
