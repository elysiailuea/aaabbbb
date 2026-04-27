#!/usr/bin/env bash
set -euo pipefail

in_whitelist() {
  local ip="$1"
  local csv="$2"

  python3 - "$ip" "$csv" <<'PY'
import sys, ipaddress
ip = sys.argv[1]
csv = sys.argv[2]
try:
    ip_obj = ipaddress.ip_address(ip)
except Exception:
    sys.exit(1)
for part in [p.strip() for p in csv.split(",") if p.strip()]:
    try:
        if "/" in part:
            net = ipaddress.ip_network(part, strict=False)
            if ip_obj in net:
                sys.exit(0)
        else:
            if ip_obj == ipaddress.ip_address(part):
                sys.exit(0)
    except Exception:
        continue
sys.exit(1)
PY
}