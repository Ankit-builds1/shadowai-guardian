#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV="$BACKEND/.venv"

echo ""
echo "ShadowAI Guardian local setup"
echo "================================"

if command -v python3.12 >/dev/null 2>&1; then
  PYTHON="python3.12"
elif command -v python3.11 >/dev/null 2>&1; then
  PYTHON="python3.11"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  echo "Python 3.11+ was not found. Install Python and rerun setup."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Node.js/npm was not found. Install Node.js 18+ and rerun setup."
  exit 1
fi

echo "Creating backend virtual environment..."
if [ ! -x "$VENV/bin/python" ]; then
  "$PYTHON" -m venv "$VENV"
fi

echo "Installing backend dependencies..."
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/pip" install -r "$BACKEND/requirements.txt"

echo "Creating backend .env..."
if [ ! -f "$BACKEND/.env" ]; then
  cp "$ROOT/.env.example" "$BACKEND/.env"
fi

echo "Training local ML model..."
(cd "$BACKEND" && "$VENV/bin/python" -m app.ml.train_model)

echo "Creating frontend .env.local..."
printf "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000\n" > "$FRONTEND/.env.local"

echo "Installing frontend dependencies..."
(cd "$FRONTEND" && npm install)

echo ""
echo "Setup complete."
echo "Run the app with: ./start.sh"
