#!/usr/bin/env bash
set -euo pipefail

# Week 14 cleanup: remove Mininet remnants and stop demo processes.
# The script aims to be conservative to avoid terminating unrelated services.

SUDO=""
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  else
    echo "[ERROR] sudo not available and not running as root" >&2
    exit 1
  fi
fi

log() {
  echo "$1"
}

log ">>> Cleaning Mininet and Open vSwitch artefacts..."

# 1) Mininet cleanup can occasionally hang on some systems.
# Use a short timeout and continue if it does not finish.
if command -v timeout >/dev/null 2>&1; then
  ${SUDO} timeout 10s mn -c >/dev/null 2>&1 || true
else
  ${SUDO} mn -c >/dev/null 2>&1 || true
fi

# 2) Remove typical Mininet bridges (s1, s2, s3 ...).
if command -v ovs-vsctl >/dev/null 2>&1; then
  while read -r br; do
    [[ -z "$br" ]] && continue
    if [[ "$br" =~ ^s[0-9]+$ ]]; then
      ${SUDO} ovs-vsctl --if-exists del-br "$br" >/dev/null 2>&1 || true
    fi
  done < <(${SUDO} ovs-vsctl list-br 2>/dev/null || true)
fi

# 3) Stop demo processes (started inside Mininet namespaces).
# Use TERM first, then KILL if still present.
patterns=(
  "python3 .*python/apps/backend_server.py"
  "python3 .*python/apps/lb_proxy.py"
  "python3 .*python/apps/tcp_echo_server.py"
  "python3 .*python/apps/tcp_echo_client.py"
  "python3 .*python/apps/http_client.py"
  "tcpdump .*demo.pcap"
  "tcpdump .*manual_demo.pcap"
  "tcpdump .*scenario14.pcap"
)

for pat in "${patterns[@]}"; do
  ${SUDO} pkill -TERM -f "$pat" >/dev/null 2>&1 || true
done

sleep 0.4

for pat in "${patterns[@]}"; do
  ${SUDO} pkill -KILL -f "$pat" >/dev/null 2>&1 || true
done

# 4) Remove temporary PCAPs created by manual exercises.
${SUDO} rm -f /tmp/manual_demo.pcap /tmp/scenario14.pcap >/dev/null 2>&1 || true

log "✓ Cleanup complete."
