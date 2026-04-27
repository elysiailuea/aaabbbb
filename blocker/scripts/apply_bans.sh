#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL="${BACKEND_URL:-http://backend:8000}"
INTERVAL="${BAN_SYNC_INTERVAL_SEC:-10}"
SETTINGS_REFRESH_SEC="${SETTINGS_REFRESH_SEC:-60}"


# Allow overriding whitelist via env, so you can test locally.
# Default stays the same as before.
WHITELIST_CSV="${WHITELIST_CSV:-127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16}"

last_settings_fetch=0

echo "Ban sync: backend=$BACKEND_URL interval=${INTERVAL}s"
echo "Initial whitelist: $WHITELIST_CSV (DISABLE_SETTINGS_FETCH=$DISABLE_SETTINGS_FETCH)"

fetch_settings() {
  json="$(curl -fsS "$BACKEND_URL/api/blocker/settings" || true)"
  if [ -n "$json" ]; then
    wl="$(echo "$json" | jq -r '.block_whitelist_csv' | head -n1)"
    if [ -n "$wl" ] && [ "$wl" != "null" ]; then
      WHITELIST_CSV="$wl"
      echo "Updated whitelist: $WHITELIST_CSV"
    fi
  fi
}

while true; do
  now_epoch="$(date +%s)"
  if [ $((now_epoch - last_settings_fetch)) -ge "$SETTINGS_REFRESH_SEC" ]; then
    fetch_settings
    last_settings_fetch="$now_epoch"
  fi

  json="$(curl -fsS "$BACKEND_URL/api/blocker/bans/active" || true)"
  if [ -n "${json}" ]; then
    ipset flush blacklist || true

    echo "$json" | jq -r '.bans[] | "\(.src_ip) \(.expires_at)"' | while read -r ip exp; do
      [ -z "$ip" ] && continue

      if /whitelist.sh in_whitelist "$ip" "$WHITELIST_CSV" 2>/dev/null; then
        echo "Skip whitelisted IP: $ip"
        continue
      fi

      exp_epoch="$(date -d "$exp" +%s 2>/dev/null || echo $((now_epoch+3600)))"
      ttl=$((exp_epoch - now_epoch))
      [ "$ttl" -le 0 ] && continue

      ipset add blacklist "$ip" timeout "$ttl" -exist
    done

    echo "Synced bans at $(date)"
  fi

  sleep "$INTERVAL"
done