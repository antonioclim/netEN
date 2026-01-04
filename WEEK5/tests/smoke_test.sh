#!/usr/bin/env bash
set -euo pipefail

# smoke_test.sh — Quick functional smoke test (Week 5)
#
# Verifies that the demo artefacts exist and contain minimal expected markers.
# Exit codes:
#   0  success
#   1  failure

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="${ROOT_DIR}/artifacts"
LOG_FILE="${ART_DIR}/demo.log"
VAL_FILE="${ART_DIR}/validation.txt"

fail() { echo "[FAIL] $*"; exit 1; }

[[ -f "${LOG_FILE}" ]] || fail "Missing ${LOG_FILE} (run: make demo)"
[[ -f "${VAL_FILE}" ]] || fail "Missing ${VAL_FILE} (run: make demo)"

grep -q "Week 5: IP Addressing" "${LOG_FILE}" || fail "demo.log missing title marker"
grep -q "Network base: 10.0.5.0/24" "${LOG_FILE}" || fail "demo.log missing network marker"

grep -q "OK:" "${VAL_FILE}" || fail "validation.txt missing OK marker"
grep -q "10.0.5.0/24" "${VAL_FILE}" || fail "validation.txt missing network marker"

echo "[OK] Smoke test passed"
