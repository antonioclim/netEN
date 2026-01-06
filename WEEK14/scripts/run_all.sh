#!/usr/bin/env bash
# run_all.sh — Runs the complete Week 14 demo (Mininet + traffic + capture)
# Usage: sudo bash scripts/run_all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$ROOT_DIR/artifacts"

echo "=============================================="
echo "  Week 14 - Complete Demo Run"
echo "=============================================="

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "[ERROR] This script must be run with sudo"
  echo "        Usage: sudo bash scripts/run_all.sh"
  exit 1
fi

# Conservative cleanup (timeouts, graceful termination).
bash "$ROOT_DIR/scripts/cleanup.sh" || true

echo "[INFO] Checking Open vSwitch..."
if command -v systemctl >/dev/null 2>&1; then
  if ! systemctl is-active --quiet openvswitch-switch; then
    echo "[INFO] Starting openvswitch-switch..."
    systemctl start openvswitch-switch
    sleep 2
  fi
fi

echo "[INFO] Preparing artifacts directory: $ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"

echo "[INFO] Starting demo orchestrator..."
echo ""

cd "$ROOT_DIR"
python3 python/apps/run_demo.py --artifacts "$ARTIFACTS_DIR"

echo ""
echo "=============================================="
echo "  Demo completed"
echo "=============================================="
echo ""
echo "Artifacts generated in: $ARTIFACTS_DIR"
ls -la "$ARTIFACTS_DIR/" || true
echo ""
echo "Useful commands for analysis:"
echo "  tshark -r $ARTIFACTS_DIR/demo.pcap -q -z conv,ip"
echo "  tshark -r $ARTIFACTS_DIR/demo.pcap -Y 'http.request'"
echo "  cat $ARTIFACTS_DIR/validation.txt"
echo "  cat $ARTIFACTS_DIR/report.json | python3 -m json.tool"
echo ""

# Final cleanup of Mininet remnants (does not remove artifacts).
bash "$ROOT_DIR/scripts/cleanup.sh" >/dev/null 2>&1 || true
