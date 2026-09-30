#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PORT:-${1:-8000}}"
HOST="${HOST:-${2:-0.0.0.0}}"

echo "=========================================================="
echo "    দৈনিক জাহান আইপিটিভি (DAINIK JAHAN IPTV PLATFORM)   "
echo "    Broadcasting Division of Dainik Jahan                 "
echo "=========================================================="
echo "Port: $PORT"
echo "Host: $HOST"
echo "Initializing Database and Server..."

cd "$PROJECT_DIR"
exec python3 -m uvicorn app.main:app --host "$HOST" --port "$PORT"
