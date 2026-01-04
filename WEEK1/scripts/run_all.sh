#!/usr/bin/env bash
set -euo pipefail

#===============================================================================
# run_all.sh - End-to-end demo runner (Week 1)
#===============================================================================
# Produces:
#   - artifacts/demo.log
#   - artifacts/validation.txt
#   - artifacts/demo.pcap (optional, if capture is enabled)
#
# Usage:
#   bash scripts/run_all.sh
#   bash scripts/run_all.sh --quick        # skip Mininet
#   bash scripts/run_all.sh --no-capture   # disable packet capture
#
# Docker path:
#   USE_DOCKER=1 bash scripts/run_all.sh
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="${PROJECT_DIR}/artifacts"
PCAP_DIR="${PROJECT_DIR}/pcap"

mkdir -p "${ARTIFACTS_DIR}" "${PCAP_DIR}"

QUICK=0
CAPTURE=1

for arg in "$@"; do
  case "$arg" in
    --quick) QUICK=1 ;;
    --no-capture) CAPTURE=0 ;;
    *) echo "[run_all] Unknown argument: ${arg}" >&2; exit 2 ;;
  esac
done

if [[ "${USE_DOCKER:-0}" == "1" ]]; then
  echo "[run_all] USE_DOCKER=1 detected, delegating to Makefile docker-demo."
  make -C "${PROJECT_DIR}" docker-demo
  exit 0
fi

DEMO_LOG="${ARTIFACTS_DIR}/demo.log"
VALIDATION_FILE="${ARTIFACTS_DIR}/validation.txt"
DEMO_PCAP="${ARTIFACTS_DIR}/demo.pcap"

# Backwards-compatible legacy names (do not rely on them in tests)
LEGACY_LOG="${ARTIFACTS_DIR}/ofmo.log"
LEGACY_PCAP="${ARTIFACTS_DIR}/ofmo.pcap"

: > "${DEMO_LOG}"
: > "${VALIDATION_FILE}"

log() { printf "%s %s\n" "$(date -Iseconds)" "$*" | tee -a "${DEMO_LOG}"; }

log "[run_all] Starting Week 1 demo"
log "[run_all] Project dir: ${PROJECT_DIR}"

# Load environment plans if present
if [[ -f "${PROJECT_DIR}/configs/ports.env" ]]; then
  # shellcheck disable=SC1090
  source "${PROJECT_DIR}/configs/ports.env"
fi
TCP_APP_PORT="${TCP_APP_PORT:-9090}"
UDP_APP_PORT="${UDP_APP_PORT:-9091}"
HTTP_PORT="${HTTP_PORT:-8080}"

# Optional capture
TCPDUMP_PID=""
if [[ "${CAPTURE}" -eq 1 ]] && command -v tcpdump >/dev/null 2>&1; then
  log "[run_all] Capture enabled, writing to ${DEMO_PCAP}"
  sudo tcpdump -i any -w "${DEMO_PCAP}" "icmp or tcp or udp" >/dev/null 2>&1 &
  TCPDUMP_PID="$!"
  sleep 1
else
  log "[run_all] Capture disabled or tcpdump not available"
fi

# Host-level inspection
log "[run_all] ip -br a"
ip -br a | tee -a "${DEMO_LOG}"
log "[run_all] ip r"
ip r | tee -a "${DEMO_LOG}"
log "[run_all] ss -lntup"
ss -lntup | tee -a "${DEMO_LOG}" || true

# Python demos
if command -v python3 >/dev/null 2>&1; then
  log "[run_all] Running Python exercises"
  python3 "${PROJECT_DIR}/python/exercises/ex_1_01_ping_latency.py" --host 127.0.0.1 --count 2 | tee -a "${DEMO_LOG}"
  python3 "${PROJECT_DIR}/python/exercises/ex_1_02_tcp_server_client.py" --port "${TCP_APP_PORT}" | tee -a "${DEMO_LOG}"
  python3 "${PROJECT_DIR}/python/exercises/ex_1_04_transmission_delay.py" --size-bytes 1500 --rate-mbps 100 | tee -a "${DEMO_LOG}"
else
  log "[run_all] python3 not available, skipping Python exercises"
fi

# Mininet demo (optional)
if [[ "${QUICK}" -eq 0 ]] && command -v mn >/dev/null 2>&1; then
  log "[run_all] Running Mininet topology smoke run"
  sudo python3 "${PROJECT_DIR}/mininet/topologies/topo_simple.py" --test-only | tee -a "${DEMO_LOG}"
else
  log "[run_all] Mininet skipped (either --quick or mn not available)"
fi

# Stop capture
if [[ -n "${TCPDUMP_PID}" ]]; then
  log "[run_all] Stopping tcpdump (pid ${TCPDUMP_PID})"
  sudo kill "${TCPDUMP_PID}" >/dev/null 2>&1 || true
  sleep 1
fi

# Create validation summary
{
  echo "Week: 1"
  echo "Timestamp: $(date -Iseconds)"
  echo "Quick mode: ${QUICK}"
  echo "Capture enabled: ${CAPTURE}"
  echo "TCP_APP_PORT: ${TCP_APP_PORT}"
  echo "UDP_APP_PORT: ${UDP_APP_PORT}"
  echo "HTTP_PORT: ${HTTP_PORT}"
  echo "Artefacts:"
  ls -lah "${ARTIFACTS_DIR}" | sed 's/^/  /'
} > "${VALIDATION_FILE}"

# Legacy copies for compatibility
cp -f "${DEMO_LOG}" "${LEGACY_LOG}" || true
if [[ -f "${DEMO_PCAP}" ]]; then
  cp -f "${DEMO_PCAP}" "${LEGACY_PCAP}" || true
fi

log "[run_all] Done"
