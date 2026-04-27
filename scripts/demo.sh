#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost}"
SSH_HOST="${SSH_HOST:-localhost}"
SSH_PORT="${SSH_PORT:-2222}"

echo "[1/3] HTTP 扫描模拟..."
paths=(
  "/"
  "/.env"
  "/.git/config"
  "/wp-login.php"
  "/xmlrpc.php"
  "/phpmyadmin"
  "/admin"
  "/config.php"
  "/actuator/health"
  "/.DS_Store"
)
for p in "${paths[@]}"; do
  curl -s -o /dev/null -w "%{http_code} $p\n" "$BASE_URL$p" -A "zgrab/0.x" || true
done

echo
echo "[2/3] HTTP 高频请求模拟（短时间）..."
for i in $(seq 1 80); do
  curl -s -o /dev/null "$BASE_URL/.env" -A "python-requests/2.x" || true
done

echo
echo "[3/3] SSH 失败登录模拟（paramiko）..."
if command -v python3 >/dev/null 2>&1; then
  if python3 -c "import paramiko" >/dev/null 2>&1; then
    python3 scripts/ssh_bruteforce_sim.py --host "$SSH_HOST" --port "$SSH_PORT" --rounds 40 --sleep 0.2 || true
  else
    echo "未检测到 paramiko，请执行：pip install paramiko"
  fi
else
  echo "未检测到 python3，跳过 SSH 模拟"
fi

echo
echo "完成。请打开前端："
echo "  http://localhost:5173/app/dashboard"
echo "建议等待 30 秒（定时聚合）后查看：总览看板/告警中心/事件查询/攻击画像"