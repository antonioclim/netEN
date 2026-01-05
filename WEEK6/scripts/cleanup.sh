#!/usr/bin/env bash
# ============================================================================
# cleanup.sh - Safe environment cleanup for Week 6
# ============================================================================
#
# This script performs the supported cleanup steps for Mininet and Open vSwitch.
# It intentionally avoids deleting interfaces by name patterns.
#
# Usage:
#   ./scripts/cleanup.sh
# ============================================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${CYAN}[INFO]${NC} $*"; }
ok() { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

info "Cleaning Mininet state..."
if sudo -n true 2>/dev/null; then
  sudo mn -c 2>/dev/null || true
  sudo ovs-vsctl --if-exists del-br s1 2>/dev/null || true
  sudo ovs-vsctl --if-exists del-br s2 2>/dev/null || true
  sudo pkill -TERM -f "os_ken.cmd.manager" 2>/dev/null || true
  sudo pkill -TERM -f "osken-manager" 2>/dev/null || true
else
  warn "sudo is required for full cleanup. Run: sudo -v then re-run."
  mn -c 2>/dev/null || true
fi

ok "Cleanup complete."
