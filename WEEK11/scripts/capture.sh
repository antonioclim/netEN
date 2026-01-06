#!/usr/bin/env bash
# =============================================================================
# capture.sh — Packet capture helper for Week 11
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

PORT=${1:-8080}
COUNT=${2:-20}
OUTPUT="pcap/capture_$(date +%Y%m%d_%H%M%S).pcap"

ORIG_USER=${SUDO_USER:-$USER}
ORIG_UID=$(id -u "$ORIG_USER")
ORIG_GID=$(id -g "$ORIG_USER")

mkdir -p pcap

echo -e "${GREEN}[CAPTURE]${NC} Capturing traffic on TCP port ${PORT}"
echo -e "${YELLOW}[INFO]${NC} Output: ${OUTPUT}"
echo -e "${YELLOW}[INFO]${NC} Packets: ${COUNT}"
echo -e "${YELLOW}[INFO]${NC} You may be prompted for sudo, depending on your system."
echo ""

if command -v tshark >/dev/null 2>&1; then
  sudo tshark -i any -f "tcp port ${PORT}" -c "${COUNT}" -w "${OUTPUT}"
  sudo chown "${ORIG_UID}:${ORIG_GID}" "${OUTPUT}" 2>/dev/null || true
  echo ""
  echo -e "${GREEN}[OK]${NC} Capture saved to ${OUTPUT}"
  echo -e "${YELLOW}[INFO]${NC} View: tshark -r ${OUTPUT}"
elif command -v tcpdump >/dev/null 2>&1; then
  sudo tcpdump -i any -n tcp port "${PORT}" -c "${COUNT}" -w "${OUTPUT}"
  sudo chown "${ORIG_UID}:${ORIG_GID}" "${OUTPUT}" 2>/dev/null || true
  echo ""
  echo -e "${GREEN}[OK]${NC} Capture saved to ${OUTPUT}"
else
  echo -e "${RED}[ERROR]${NC} Neither tshark nor tcpdump are installed."
  echo -e "${YELLOW}[INFO]${NC} Install: sudo apt-get update && sudo apt-get install -y tshark"
  exit 1
fi
