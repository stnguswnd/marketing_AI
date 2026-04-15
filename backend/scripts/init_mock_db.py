from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.bootstrap import create_database_schema
from app.db.seeds import seed_mock_data
from app.db.session import SessionLocal


def main() -> None:
    create_database_schema()
    with SessionLocal() as session:
        seed_mock_data(session)
    print("Mock PostgreSQL database initialized with admin and merchant accounts.")


if __name__ == "__main__":
    main()
