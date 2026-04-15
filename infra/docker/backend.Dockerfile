FROM python:3.11-slim

WORKDIR /workspace/backend

COPY backend/pyproject.toml ./pyproject.toml
RUN pip install --upgrade pip && pip install -e .[dev]

COPY backend/app ./app
COPY backend/tests ./tests
COPY backend/scripts ./scripts

CMD ["sh", "scripts/start_backend.sh"]
