#!/usr/bin/env bash
echo "=========================================================="
echo " Magnetar Labs — Agentic Windows EXE Builder Launcher"
echo " Engine: Qwen2.5-Coder 32B via Ollama & PyInstaller In-Code"
echo "=========================================================="

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "[1/2] Starting FastAPI Backend on http://localhost:8000..."
cd "$DIR/backend" || exit
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "[2/2] Starting React Vite Frontend on http://localhost:3000..."
cd "$DIR/frontend" || exit
if [ ! -d "node_modules" ]; then
  npm install
fi

npm run dev

kill $BACKEND_PID
