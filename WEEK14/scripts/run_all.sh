#!/bin/bash
# run_all.sh — Runs the complete W14 demo (Mininet + traffic + capture)
# Run: sudo bash scripts/run_all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$ROOT_DIR/artifacts"

echo "=============================================="
echo "  Demo W14 - Complete Run"
echo "=============================================="

# Check permissions
if [ "$EUID" -ne 0 ]; then
    echo "[!] This script must be run with sudo"
    echo "    Usage: sudo bash scripts/run_all.sh"
    exit 1
fi

# Clean any previous Mininet leftovers
echo "[*] Cleaning previous Mininet..."
mn -c 2>/dev/null || true
pkill -f "backend_server.py" 2>/dev/null || true
pkill -f "lb_proxy.py" 2>/dev/null || true
pkill -f "tcp_echo_server.py" 2>/dev/null || true
pkill -f "run_demo.py" 2>/dev/null || true
sleep 1

# Check OVS
echo "[*] Checking Open vSwitch..."
if ! systemctl is-active --quiet openvswitch-switch; then
    echo "    Starting openvswitch-switch..."
    systemctl start openvswitch-switch
    sleep 2
fi

# Create artefacts directory
echo "[*] Preparing artefacts directory: $ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"

# Run Python orchestrator
echo "[*] Starting demo orchestrator..."
echo ""

cd "$ROOT_DIR"
python3 python/apps/run_demo.py --artifacts "$ARTIFACTS_DIR"

# Display artefacts
echo ""
echo "=============================================="
echo "  Demo completed!"
echo "=============================================="
echo ""
echo "Artefacts generated in: $ARTIFACTS_DIR"
echo ""
ls -la "$ARTIFACTS_DIR/"
echo ""
echo "Useful commands for analysis:"
echo "  tshark -r $ARTIFACTS_DIR/demo.pcap -q -z conv,ip"
echo "  tshark -r $ARTIFACTS_DIR/demo.pcap -Y 'http.request'"
echo "  cat $ARTIFACTS_DIR/validation.txt"
echo "  cat $ARTIFACTS_DIR/report.json | python3 -m json.tool"
echo ""
