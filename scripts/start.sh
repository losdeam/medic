#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo "==> 启动应用 (端口 8501)..."
uv run python main.py
