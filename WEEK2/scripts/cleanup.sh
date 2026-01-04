#!/usr/bin/env bash
# =============================================================================
# cleanup.sh - Wrapper for cleaning standard (WEEK 2)
# =============================================================================
# This script este un wrapper for compatibilitate with standardul transversal.
# Logica principala este in clean.sh
# =============================================================================
# Computer Networks - ASE Bucharest, CSIE
# Hypotheticalandrei & Rezolvix | MIT License
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Culori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       Cleanup - Week 2: Socket Programming             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# cleaning processes
# =============================================================================
echo "[INFO] Stopping processes demo..."

# stopping servers TCP/UDP
pkill -f "ex_2_01_tcp.py" 2>/dev/null && echo "  ✓ server TCP oprit" || true
pkill -f "ex_2_02_udp.py" 2>/dev/null && echo "  ✓ server UDP oprit" || true

# stopping capturi tcpdump
sudo pkill -f "tcpdump.*port.*909" 2>/dev/null && echo "  ✓ tcpdump oprit" || true

# =============================================================================
# cleaning MININET
# =============================================================================
echo "[INFO] cleaning Mininet..."
if command -v mn &>/dev/null; then
    sudo mn -c 2>/dev/null && echo "  ✓ Mininet curatat" || true
else
    echo "  - Mininet is not installed"
fi

# =============================================================================
# cleaning ARTIFACTS (OPTIONAL)
# =============================================================================
if [[ "${1:-}" == "--full" ]]; then
    echo "[INFO] cleaning completa (inclusiv artefacts)..."
    rm -rf "$PROJECT_ROOT/artifacts/"*.log 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/artifacts/"*.pcap 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/artifacts/"*.txt 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/logs/"*.log 2>/dev/null || true
    echo "  ✓ Artefacte deleted"
fi

# =============================================================================
# cleaning PYCACHE
# =============================================================================
echo "[INFO] cleaning __pycache__..."
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
echo "  ✓ Cache Python curatat"

# =============================================================================
# RAPORT
# =============================================================================
echo ""
echo "════════════════════════════════════════════════════════════════"
echo " Cleanup complet!"
echo ""
echo " for cleaning completa (inclusiv artefacts):"
echo "   ./scripts/cleanup.sh --full"
echo ""
echo " for verification status ports:"
echo "   ss -tuln | grep -E '909[01]|8080|9999'"
echo "════════════════════════════════════════════════════════════════"
