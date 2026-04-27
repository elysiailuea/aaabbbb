#!/usr/bin/env bash
set -euo pipefail

# Setup ipset + iptables DROP
ipset create blacklist hash:ip timeout 3600 -exist

# Drop traffic to blocker itself for IPs in blacklist (ports 80 and 2222)
iptables -C INPUT -m set --match-set blacklist src -j DROP 2>/dev/null || \
  iptables -I INPUT -m set --match-set blacklist src -j DROP

# Start ban sync in background
/apply_bans.sh &

# Start nginx (HTTP) and haproxy (SSH)
nginx
exec haproxy -f /etc/haproxy/haproxy.cfg