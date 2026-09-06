#!/bin/sh
set -eu

cd /app/backend
python -c "from app.models.db import wait_for_db; wait_for_db()"

WORKERS="${WEB_CONCURRENCY:-2}"
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --proxy-headers \
  --forwarded-allow-ips='*' \
  --timeout-keep-alive 120 \
  --workers "$WORKERS"
