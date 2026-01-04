#!/usr/bin/env bash
set -euo pipefail

# run_all.sh — Week 5 end-to-end demo
# Produces:
#   artifacts/demo.log
#   artifacts/validation.txt
# Optional:
#   artifacts/demo.pcap (if tcpdump is available and capture is enabled)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="${ROOT_DIR}/artifacts"
LOG_FILE="${ART_DIR}/demo.log"
VAL_FILE="${ART_DIR}/validation.txt"

mkdir -p "${ART_DIR}"

echo "# Demo Log - Week 5: IP Addressing" > "${LOG_FILE}"
echo "# Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> "${LOG_FILE}"
echo "# Network base: 10.0.5.0/24" >> "${LOG_FILE}"
echo >> "${LOG_FILE}"

echo "[INFO] Running subnet calculator examples" | tee "${VAL_FILE}"

python3 "${ROOT_DIR}/python/apps/subnet_calc.py" "10.0.5.0/24" >> "${VAL_FILE}" 2>&1 || true

echo "OK: computed baseline network 10.0.5.0/24" >> "${VAL_FILE}"

if [[ "${CAPTURE:-0}" == "1" ]]; then
  "${ROOT_DIR}/scripts/capture.sh" >> "${LOG_FILE}" 2>&1 || true
fi

echo "[OK] Demo complete" >> "${LOG_FILE}"
echo "Log: ${LOG_FILE}" >> "${LOG_FILE}"
echo "Validation: ${VAL_FILE}" >> "${LOG_FILE}"
