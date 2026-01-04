#!/bin/bash
set -euo pipefail
set -euo pipefail
# =============================================================================
# verify.sh - Verification environment Week 13
# =============================================================================
# Quick verification a dependentelor necesare.
# For verification completa: ./tests/smoke_test.sh
# =============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Verification Environment - Starterkit S13                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Python
if python3 --version 2>/dev/null; then
    echo "[✓] Python3: $(python3 --version 2>&1)"
else
    echo "[✗] Python3: Not is instalat"
fi

# Docker
if docker --version 2>/dev/null; then
    echo "[✓] Docker: disponibil"
else
    echo "[!] Docker: Not is instalat (optional)"
fi

# tcpdump/tshark
if command -v tcpdump &>/dev/null; then
    echo "[✓] tcpdump: disponibil"
elif command -v tshark &>/dev/null; then
    echo "[✓] tshark: disponibil"
else
    echo "[!] tcpdump/tshark: Not are instalate"
fi

# Modules Python
echo ""
echo "Modules Python:"
for modules in "paho.mqtt.client" "scapy.all" "requests" "socket" "json"; do
    if python3 -c "import ${modules%%.*}" 2>/dev/null; then
        echo "  [✓] $modules"
    else
        echo "  [!] $modules: lipsa"
    fi
done

# Artefacts verification
echo ""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
if [ -d "$PROJECT_DIR/artifacts" ]; then
    echo "Artefacte demo:"
    [ -f "$PROJECT_DIR/artifacts/demo.log" ] && echo "  [✓] demo.log" || echo "  [!] demo.log (run run_all.sh)"
    [ -f "$PROJECT_DIR/artifacts/demo.pcap" ] && echo "  [✓] demo.pcap" || echo "  [!] demo.pcap"
    [ -f "$PROJECT_DIR/artifacts/validation.txt" ] && echo "  [✓] validation.txt" || echo "  [!] validation.txt"
else
    echo "[!] Directory artifacts/ not exista (created of run_all.sh)"
fi

echo ""
echo "For verification completa: ./tests/smoke_test.sh"
