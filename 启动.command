#!/bin/bash
set -u

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$ROOT_DIR/.run"
BACKEND_PID_FILE="$RUN_DIR/backend.pid"
FRONTEND_PID_FILE="$RUN_DIR/frontend.pid"

mkdir -p "$RUN_DIR"

is_running() {
  [[ -f "$1" ]] && kill -0 "$(<"$1")" 2>/dev/null
}

port_is_busy() {
  lsof -tiTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

wait_for_port() {
  local port="$1"
  local label="$2"
  for _ in {1..45}; do
    if port_is_busy "$port"; then
      echo "$label 已启动：端口 $port"
      return 0
    fi
    sleep 1
  done
  return 1
}

if is_running "$BACKEND_PID_FILE" || is_running "$FRONTEND_PID_FILE"; then
  echo "RAG 项目已在运行。如需重启，请先双击“关闭.command”。"
  exit 0
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "未找到 uv，请先安装 uv：pip install uv"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "未找到 python3，请先安装 Python。"
  exit 1
fi

if port_is_busy 8000 || port_is_busy 5174; then
  echo "8000 或 5174 端口正在被占用，请先关闭占用该端口的项目。"
  exit 1
fi

if [[ ! -x "$ROOT_DIR/.venv/bin/python" ]]; then
  echo "首次启动，正在同步 Python 依赖…"
  (cd "$ROOT_DIR" && uv sync) || exit 1
fi

echo "正在启动 RAG 后端…"
nohup bash -lc 'cd "$1" && exec uv run uvicorn src.api.main:app --host 127.0.0.1 --port 8000' -- "$ROOT_DIR" \
  > "$RUN_DIR/backend.log" 2>&1 &
echo $! > "$BACKEND_PID_FILE"

echo "正在启动 RAG 静态前端…"
nohup bash -lc 'exec python3 -m http.server 5174 --bind 127.0.0.1 --directory "$1"' -- "$ROOT_DIR/frontend" \
  > "$RUN_DIR/frontend.log" 2>&1 &
echo $! > "$FRONTEND_PID_FILE"

if ! wait_for_port 8000 "后端" || ! wait_for_port 5174 "前端"; then
  echo "启动超时，请查看：$RUN_DIR"
  bash "$ROOT_DIR/关闭.command"
  exit 1
fi

echo "RAG 项目已启动：http://localhost:5174"
echo "日志目录：$RUN_DIR"
open "http://localhost:5174"
