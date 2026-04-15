# Mock DB Guide

이 프로젝트는 현재 운영 데이터와 계정/점포 데이터를 모두 `PostgreSQL + SQLAlchemy` 기준으로 구동한다. Docker Compose 실행 시 이 DB는 자동으로 생성되고 seed 된다.

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
- 운영 데이터 테이블
  - `assets`
  - `contents`
  - `reviews`
  - `reports`
  - `jobs`
  - `publish_results`
  - `audit_logs`
  - `request_logs`

## 자동 초기화 방식
`docker compose -f infra/docker-compose.yml up --build`를 실행하면 다음 순서로 자동 처리된다.

1. `postgres` 컨테이너가 뜬다.
2. `backend` 컨테이너가 `backend/scripts/start_backend.sh`를 실행한다.
3. 이 스크립트가 `python scripts/init_mock_db.py`를 반복 호출한다.
4. init 스크립트는 mock schema를 최신 모델 기준으로 재생성한 뒤 seed 계정과 demo 데이터를 넣는다.
5. 그 다음 `uvicorn`이 시작된다.

즉, 별도 수동 insert 없이 초기 계정이 자동 업로드된다. Docker Compose 기준 mock 환경에서는 재시작 시 데이터가 seed 상태로 다시 맞춰질 수 있다.

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

- 실제 object storage 연동은 아직 없다.
- `Nano Banana`와 외부 발행 adapter는 여전히 스텁 수준이다.
- DB는 붙었지만 외부 채널 연동까지 운영 수준은 아니다.
