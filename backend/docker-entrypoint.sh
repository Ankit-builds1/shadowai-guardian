#!/bin/sh
set -eu

if [ "${1:-info}" = "serve" ]; then
  shift || true
  exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
fi

exec python -m app.cli "$@"
