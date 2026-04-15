# Mock DB Guide

이 프로젝트는 현재 운영 데이터 본체는 메모리 저장소를 사용하지만, 계정/점포와 로그인 검증은 `PostgreSQL + SQLAlchemy` 기반 목업 DB를 사용할 수 있다. Docker Compose 실행 시 이 DB는 자동으로 생성되고 seed 된다.

## Seed 계정

비밀번호는 모두 `12345678` 이다.

| 역할 | 이메일 | user_id | merchant_id |
|---|---|---|---|
| 관리자 | `test1@email.com` | `user_admin_001` | - |
| 점주 | `test2@email.com` | `user_merchant_002` | `m_002` |
| 점주 | `test3@email.com` | `user_merchant_003` | `m_003` |
| 점주 | `test4@email.com` | `user_merchant_004` | `m_004` |

점주/점포 프로필 이미지는 각각 다른 URL로 seed 된다.

## 생성되는 테이블

- `users`
- `merchants`
- `memberships`
- 기존 운영 스캐폴드 테이블
  - `assets`
  - `contents`
  - `jobs`
  - `audit_logs`
  - `request_logs`

## 자동 초기화 방식
`docker compose -f infra/docker-compose.yml up --build`를 실행하면 다음 순서로 자동 처리된다.

1. `postgres` 컨테이너가 뜬다.
2. `backend` 컨테이너가 `backend/scripts/start_backend.sh`를 실행한다.
3. 이 스크립트가 `python scripts/init_mock_db.py`를 반복 호출한다.
4. 스키마 생성과 seed 계정 insert가 끝나면 `uvicorn`이 시작된다.

즉, 별도 수동 insert 없이 초기 계정이 자동 업로드된다.

## 수동 실행 순서

1. PostgreSQL과 Redis 컨테이너 실행
```bash
docker compose -f infra/docker-compose.yml up -d postgres redis
```

2. Python 의존성 설치
```bash
cd backend
python3 -m pip install -e '.[dev]'
```

3. 스키마와 seed 데이터 생성
```bash
cd backend
python3 scripts/init_mock_db.py
```

## 확인 예시

```bash
docker exec -it $(docker ps -qf "ancestor=postgres:16") psql -U harness -d harness
```

```sql
select email, role from users order by email;
select merchant_id, name from merchants order by merchant_id;
select user_id, merchant_id, membership_role from memberships order by membership_id;
```

## 현재 한계

- FastAPI 런타임은 아직 메모리 저장소를 사용한다.
- 위 목업 DB는 인증/회원 관리와 초기 점포 데이터를 위한 실제 데이터베이스 초석이다.
- 다음 단계는 `MemoryRepository -> SQLAlchemy repository` 전환이다.
