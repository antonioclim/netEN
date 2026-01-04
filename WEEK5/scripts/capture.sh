#!/usr/bin/env bash
set -euo pipefail

# capture.sh — Optional packet capture helper (Week 5)
#
# This script writes ./artifacts/demo.pcap if tcpdump is available.
# It is intentionally conservative to avoid breaking a minimal VM.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="${ROOT_DIR}/artifacts"
PCAP="${ART_DIR}/demo.pcap"

mkdir -p "${ART_DIR}"

if ! command -v tcpdump >/dev/null 2>&1; then
  echo "[INFO] tcpdump is not installed, skipping capture"
  exit 0
fi

echo "[INFO] Capturing 20 packets to ${PCAP}"
# Capture on any interface, limit packets and duration
sudo timeout 10 tcpdump -i any -c 20 -w "${PCAP}" >/dev/null 2>&1 || true

if [[ -s "${PCAP}" ]]; then
  echo "[OK] Capture written to ${PCAP}"
else
  echo "[WARN] Capture file is empty or missing"
fi
