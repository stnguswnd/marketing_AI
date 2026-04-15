#!/bin/sh
set -eu

echo "[backend] waiting for database bootstrap"
until python scripts/init_mock_db.py; do
  echo "[backend] database is not ready yet, retrying in 2s"
  sleep 2
done

echo "[backend] starting api server"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
