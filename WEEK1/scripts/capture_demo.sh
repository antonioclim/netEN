#!/usr/bin/env bash
set -euo pipefail

#===============================================================================
# capture_demo.sh - Generate example captures (Week 1)
#===============================================================================
# This script generates small PCAP samples using tcpdump while running local
# traffic (ICMP, TCP and UDP). It is optional and not required for assessment.
#
# Usage:
#   bash scripts/capture_demo.sh --mixed
#   bash scripts/capture_demo.sh --tcp
#   bash scripts/capture_demo.sh --udp
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PCAP_DIR="${PROJECT_DIR}/pcap"
mkdir -p "${PCAP_DIR}"

MODE="${1:---mixed}"
OUT="${PCAP_DIR}/example_${MODE#--}.pcap"

if ! command -v tcpdump >/dev/null 2>&1; then
  echo "[capture_demo] tcpdump not found"
  exit 1
fi

FILTER="icmp or tcp or udp"
case "${MODE}" in
  --tcp) FILTER="tcp" ;;
  --udp) FILTER="udp" ;;
  --mixed) FILTER="icmp or tcp or udp" ;;
  *) echo "[capture_demo] Unknown mode: ${MODE}" >&2; exit 2 ;;
esac

echo "[capture_demo] Writing ${OUT}"
sudo tcpdump -i any -w "${OUT}" "${FILTER}" >/dev/null 2>&1 &
PID="$!"
sleep 1

# Generate local traffic
ping -c 1 127.0.0.1 >/dev/null 2>&1 || true
# TCP and UDP on discard port, may fail but still generates attempted traffic
(printf "hello\n" | nc 127.0.0.1 9 >/dev/null 2>&1 || true)
(printf "hi\n" | nc -u 127.0.0.1 9 >/dev/null 2>&1 || true)

sudo kill "${PID}" >/dev/null 2>&1 || true
sleep 1

echo "[capture_demo] Done"
