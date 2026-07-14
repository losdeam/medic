#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

./stop.sh
echo "==> 重启中..."
sleep 1
./start.sh
