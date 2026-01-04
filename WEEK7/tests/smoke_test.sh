#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ART_DIR="$ROOT_DIR/artifacts"

echo "[smoke] Checking artefacts in: $ART_DIR"

test -f "$ART_DIR/demo.log"
test -f "$ART_DIR/validation.txt"

# pcap is optional, but in the standard VM it should exist
if [[ -f "$ART_DIR/demo.pcap" ]]; then
  if [[ $(stat -c%s "$ART_DIR/demo.pcap") -lt 200 ]]; then
    echo "[smoke] demo.pcap exists but is too small. Capture may have failed."
    exit 2
  fi
else
  echo "[smoke] demo.pcap is missing. This is acceptable if tcpdump is not installed."
fi

grep -q "BASELINE_OK" "$ART_DIR/validation.txt"
grep -q "BLOCK_TCP_OK" "$ART_DIR/validation.txt"
grep -q "BLOCK_UDP_OK" "$ART_DIR/validation.txt"

echo "[smoke] OK"
