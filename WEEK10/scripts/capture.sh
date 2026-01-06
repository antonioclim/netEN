#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PCAP_DIR="${ROOT_DIR}/pcap"
mkdir -p "${PCAP_DIR}"

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  echo "This capture script requires root privileges."
  echo "Run: sudo ./scripts/capture.sh"
  exit 1
fi

INTERFACE="any"
DURATION=20
FILTER="tcp port 8000 or tcp port 22 or tcp port 2121 or udp port 5353"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -i|--interface) INTERFACE="$2"; shift 2 ;;
    -t|--time) DURATION="$2"; shift 2 ;;
    -f|--filter) FILTER="$2"; shift 2 ;;
    -h|--help)
      cat <<EOF
Usage: sudo ./scripts/capture.sh [options]

Options:
  -i, --interface <iface>  Interface to capture on (default: any)
  -t, --time <seconds>     Capture duration (default: 20)
  -f, --filter <bpf>       tcpdump BPF filter

Default filter captures ports used in Week 10 docker demos:
  ${FILTER}
EOF
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 2 ;;
  esac
done

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="${PCAP_DIR}/week10_${STAMP}.pcap"

echo "Capturing for ${DURATION}s on interface '${INTERFACE}'"
echo "Output: ${OUT_FILE}"
echo "Filter: ${FILTER}"

# Prefer tshark if available because it is already used elsewhere in the kits.
if command -v tshark >/dev/null 2>&1; then
  timeout "${DURATION}s" tshark -i "${INTERFACE}" -f "${FILTER}" -w "${OUT_FILE}" >/dev/null 2>&1 || true
elif command -v tcpdump >/dev/null 2>&1; then
  timeout "${DURATION}s" tcpdump -i "${INTERFACE}" -w "${OUT_FILE}" ${FILTER} >/dev/null 2>&1 || true
else
  echo "Neither tshark nor tcpdump are available."
  exit 1
fi

if [[ -s "${OUT_FILE}" ]]; then
  echo "Capture complete (non-empty pcap)."
else
  echo "Capture complete but the pcap is empty."
  echo "Tip: run the docker demos while capturing to generate traffic."
fi
