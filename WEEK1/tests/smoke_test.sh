#!/usr/bin/env bash
set -euo pipefail

#===============================================================================
# smoke_test.sh - Non-interactive validation (Week 1)
#===============================================================================
# Validates that the demo produced the expected artefacts and that they contain
# minimal content.
#
# Usage:
#   bash tests/smoke_test.sh
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="${PROJECT_DIR}/artifacts"

require_file() {
  local f="$1"
  [[ -f "${f}" ]] || { echo "[FAIL] Missing file: ${f}" >&2; exit 1; }
  [[ -s "${f}" ]] || { echo "[FAIL] Empty file: ${f}" >&2; exit 1; }
  echo "[PASS] ${f}"
}

require_grep() {
  local pattern="$1"
  local f="$2"
  grep -qE "${pattern}" "${f}" || { echo "[FAIL] Pattern not found in ${f}: ${pattern}" >&2; exit 1; }
  echo "[PASS] ${f} contains ${pattern}"
}

require_file "${ARTIFACTS_DIR}/demo.log"
require_file "${ARTIFACTS_DIR}/validation.txt"

require_grep "\[run_all\] Starting Week 1 demo" "${ARTIFACTS_DIR}/demo.log"
require_grep "^Week: 1$" "${ARTIFACTS_DIR}/validation.txt"

# PCAP is optional
if [[ -f "${ARTIFACTS_DIR}/demo.pcap" ]]; then
  [[ -s "${ARTIFACTS_DIR}/demo.pcap" ]] || { echo "[FAIL] demo.pcap exists but is empty" >&2; exit 1; }
  echo "[PASS] ${ARTIFACTS_DIR}/demo.pcap"
else
  echo "[WARN] demo.pcap not present (capture disabled or tcpdump missing)"
fi

echo "[PASS] Smoke test completed"
