#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
PYTHON="$BACKEND/.venv/bin/python"

if [ ! -x "$PYTHON" ]; then
  echo "Backend virtual environment not found. Run ./setup.sh first."
  exit 1
fi

if [ ! -d "$FRONTEND/node_modules" ]; then
  echo "Frontend dependencies not found. Run ./setup.sh first."
  exit 1
fi

printf "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000\n" > "$FRONTEND/.env.local"

echo ""
echo "Starting ShadowAI Guardian..."
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Chrome extension folder: $ROOT/browser-extension"

(cd "$BACKEND" && "$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload) &
BACKEND_PID=$!
(cd "$FRONTEND" && npm run dev -- -p 3000) &
FRONTEND_PID=$!

sleep 5
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:3000" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open "http://localhost:3000" >/dev/null 2>&1 || true
fi

trap 'kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true' INT TERM EXIT
echo "App launched. Keep this terminal open. Press Ctrl+C to stop."
echo "To use the browser proxy, load the browser-extension folder in chrome://extensions."
wait
