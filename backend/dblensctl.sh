#!/usr/bin/env bash
set -euo pipefail
APP_DIR=/opt/dblens/app/backend
RUNTIME_DIR=/opt/dblens/runtime
PID_DIR=$RUNTIME_DIR/pids
LOG_DIR=$RUNTIME_DIR/logs
PID_FILE=$PID_DIR/dblens.pid
LOG_FILE=$LOG_DIR/dblens.log
ENV_FILE=$APP_DIR/.env
PYTHON_BIN=/opt/dblens/venv/bin/python
APP_BIND=0.0.0.0:8000
APP_MODULE=app.main:app
APP_PATTERN="$PYTHON_BIN -m uvicorn $APP_MODULE --host 0.0.0.0 --port 8000"
mkdir -p "$PID_DIR" "$LOG_DIR"
resolve_pid() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      echo "$pid"
      return 0
    fi
  fi
  local discovered
  discovered="$(pgrep -f "$APP_PATTERN" | head -n 1 || true)"
  if [[ -n "${discovered:-}" ]]; then
    echo "$discovered" > "$PID_FILE"
    echo "$discovered"
    return 0
  fi
  return 1
}
require_runtime() {
  [[ -d "$APP_DIR" ]]
  [[ -f "$ENV_FILE" ]]
  [[ -x "$PYTHON_BIN" ]]
}
start_app() {
  require_runtime
  if pid="$(resolve_pid)"; then
    echo "DBLens backend is already running (PID: $pid)"
    exit 0
  fi
  cd "$APP_DIR"
  set -a
  source "$ENV_FILE"
  set +a
  nohup "$PYTHON_BIN" -m uvicorn "$APP_MODULE" --host 0.0.0.0 --port 8000 >> "$LOG_FILE" 2>&1 &
  local pid=$!
  echo "$pid" > "$PID_FILE"
  sleep 2
  if kill -0 "$pid" 2>/dev/null; then
    echo "DBLens backend started (PID: $pid)"
    exit 0
  fi
  echo "Failed to start DBLens backend. Check log: $LOG_FILE" >&2
  exit 1
}
stop_app() {
  if ! pid="$(resolve_pid)"; then
    rm -f "$PID_FILE"
    echo "DBLens backend is not running"
    exit 0
  fi
  kill "$pid" 2>/dev/null || true
  for _ in {1..10}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      rm -f "$PID_FILE"
      echo "DBLens backend stopped"
      exit 0
    fi
    sleep 1
  done
  kill -9 "$pid" 2>/dev/null || true
  rm -f "$PID_FILE"
  echo "DBLens backend force-stopped"
}
status_app() {
  if pid="$(resolve_pid)"; then
    echo "DBLens backend is running"
    echo "PID: $pid"
    if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
      echo "Health: OK"
    else
      echo "Health: UNAVAILABLE"
    fi
    exit 0
  fi
  echo "DBLens backend is stopped"
  exit 1
}
restart_app() {
  (stop_app) || true
  start_app
}
case "${1:-}" in
  start) start_app ;;
  stop) stop_app ;;
  restart) restart_app ;;
  status) status_app ;;
  *) echo "Usage: $0 {start|stop|restart|status}" >&2; exit 1 ;;
esac
