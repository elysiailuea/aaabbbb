#!/usr/bin/env bash
set -euo pipefail

cd /app

# 自动迁移到最新版本
alembic -c alembic.ini upgrade head

# 启动 API
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000