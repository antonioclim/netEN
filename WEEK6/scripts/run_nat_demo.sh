#!/usr/bin/env bash
# ============================================================================
# run_nat_demo.sh - Interactive NAT/PAT demo for Week 6
#
# Starts the NAT topology and opens the Mininet CLI.
# British English is used throughout (no Oxford comma).
# Licence: MIT | ASE-CSIE 2025-2026
# ============================================================================

set -euo pipefail

BLUE='\033[0;34m'
NC='\033[0m'

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  SUDO="sudo"
fi

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════"
echo "  NAT/PAT Demo – Observing address translation"
echo "  Week 6: Computer Networks (ASE-CSIE 2025-2026)"
echo "═══════════════════════════════════════════════════════════════"
echo -e "${NC}"

echo -e "${BLUE}[INFO]${NC} Cleaning Mininet artefacts (safe cleanup)..."
timeout 15s ${SUDO} mn -c 2>/dev/null || true

echo -e "${BLUE}[INFO]${NC} Starting interactive topology (Mininet CLI)..."
${SUDO} python3 mininet/topologies/topo_nat.py --cli
