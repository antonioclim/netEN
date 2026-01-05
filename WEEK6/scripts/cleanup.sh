#!/usr/bin/env bash
# ============================================================================
# cleanup.sh - Safe cleanup for Week 6 Mininet/Open vSwitch artefacts
#
# This script aims to be conservative. It should not kill unrelated processes
# or delete non-Mininet interfaces. Prefer `mn -c` and targeted OVS cleanup.
# British English is used throughout (no Oxford comma).
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

info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }

PID_FILE="/tmp/osken_controller.pid"

info "Cleaning Mininet artefacts..."
timeout 15s ${SUDO} mn -c 2>/dev/null || true
success "Mininet cleanup complete"

if [ -f "${PID_FILE}" ]; then
  PID="$(cat "${PID_FILE}" 2>/dev/null || true)"
  if [ -n "${PID}" ] && kill -0 "${PID}" 2>/dev/null; then
    info "Stopping controller (PID: ${PID})..."
    ${SUDO} kill "${PID}" 2>/dev/null || true
    success "Controller stopped"
  fi
  rm -f "${PID_FILE}" || true
else
  warn "No controller PID file found (expected in OVS-flow mode)"
fi

info "Removing common OVS bridges (if present)..."
timeout 10s ${SUDO} ovs-vsctl --if-exists del-br s1 2>/dev/null || true
timeout 10s ${SUDO} ovs-vsctl --if-exists del-br s2 2>/dev/null || true
success "OVS cleanup complete"

success "Cleanup complete"
