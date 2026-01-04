#!/usr/bin/env bash
# =============================================================================
# smoke_test.sh — Smoke test for Week 12
# =============================================================================
# This test is non-interactive. It validates that the main demo produces the
# expected artefacts and that the artefacts contain a minimal set of markers.
#
# Usage: ./tests/smoke_test.sh
# Exit codes: 0 = PASS, 1 = FAIL
# =============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="${PROJECT_ROOT}/artifacts"

DEMO_LOG="${ARTIFACTS_DIR}/demo.log"
VALIDATION_FILE="${ARTIFACTS_DIR}/validation.txt"
DEMO_PCAP="${ARTIFACTS_DIR}/demo.pcap"

fail() {
  echo "SMOKE TEST: FAILED"
  echo "Reason: $1"
  echo ""
  echo "Hints:"
  echo "  1. Run: ./scripts/setup.sh"
  echo "  2. Run: ./scripts/run_all.sh"
  echo "  3. Inspect: artifacts/"
  exit 1
}

[ -d "${ARTIFACTS_DIR}" ] || fail "Missing artifacts/ directory"

[ -f "${DEMO_LOG}" ] || fail "Missing ${DEMO_LOG}"
[ -s "${DEMO_LOG}" ] || fail "${DEMO_LOG} is empty"

[ -f "${VALIDATION_FILE}" ] || fail "Missing ${VALIDATION_FILE}"
[ -s "${VALIDATION_FILE}" ] || fail "${VALIDATION_FILE} is empty"

grep -q "WEEK 12: AUTOMATIC EMAIL & RPC DEMO" "${DEMO_LOG}" || fail "Missing header marker in demo.log"
grep -q "Project root:" "${DEMO_LOG}" || fail "Missing 'Project root' marker in demo.log"

# Optional capture artefact (only if tcpdump ran successfully)
if [ -f "${DEMO_PCAP}" ]; then
  if [ ! -s "${DEMO_PCAP}" ]; then
    fail "${DEMO_PCAP} exists but is empty"
  fi
fi

echo "SMOKE TEST: PASSED"
exit 0
