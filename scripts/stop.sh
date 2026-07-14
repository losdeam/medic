#!/usr/bin/env bash
set -e

PORT=8501
PID=$(lsof -ti tcp:"$PORT" 2>/dev/null || true)

if [ -n "$PID" ]; then
    echo "==> 停止端口 $PORT 上的进程 (PID: $PID)"
    kill "$PID"
    echo "已停止"
else
    echo "端口 $PORT 上无运行中的进程"
fi
