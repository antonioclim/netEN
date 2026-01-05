#!/usr/bin/env bash
# ============================================================================
# run_sdn_demo.sh - Interactive SDN/OpenFlow demo for Week 6
#
# This starter kit uses a controller-less SDN mode by default. The OpenFlow
# policy is installed directly into Open vSwitch so the lab remains reproducible
# on Ubuntu 24.04 with OS-Ken 4.x.
#
# British English is used throughout (no Oxford comma).
# Licence: MIT | ASE-CSIE 2025-2026
# ============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  SUDO="sudo"
fi

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════"
echo "  SDN/OpenFlow Demo – Policy via OVS flows (no controller)"
echo "  Week 6: Computer Networks (ASE-CSIE 2025-2026)"
echo "═══════════════════════════════════════════════════════════════"
echo -e "${NC}"

echo -e "${BLUE}[INFO]${NC} Cleaning Mininet artefacts (safe cleanup)..."
timeout 15s ${SUDO} mn -c 2>/dev/null || true

echo -e "${BLUE}[INFO]${NC} Starting interactive topology (Mininet CLI)..."
${SUDO} python3 mininet/topologies/topo_sdn.py --mode ovs --cli
