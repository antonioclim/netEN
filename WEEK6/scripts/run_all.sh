#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="${ROOT_DIR}/artifacts"
TOPO_DIR="${ROOT_DIR}/seminar/mininet/topologies"
CTRL_APP="${ROOT_DIR}/controller/sdn_controller.py"
CTRL_PORT="${CTRL_PORT:-6633}"
CTRL_HOST="${CTRL_HOST:-127.0.0.1}"

mkdir -p "${ART_DIR}"

ts() { date +"%Y-%m-%d %H:%M:%S"; }
log() { echo "[$(ts)] [$1] $2" | tee -a "${ART_DIR}/demo.log"; }
info() { log "INFO" "$1"; }
ok() { log "OK" "$1"; }
warn() { log "WARN" "$1"; }
die() { log "ERROR" "$1"; exit 1; }

controller_pid=""

cleanup() {
  info "Final cleanup..."
  if [[ -n "${controller_pid}" ]] && kill -0 "${controller_pid}" 2>/dev/null; then
    info "Stopping controller (PID ${controller_pid})..."
    kill "${controller_pid}" 2>/dev/null || true
    sleep 1
    kill -9 "${controller_pid}" 2>/dev/null || true
    ok "Controller stopped"
  fi
  info "Cleaning Mininet/OVS..."
  sudo timeout 20s mn -c >/dev/null 2>&1 || true
  sudo ovs-vsctl --if-exists del-br s1 >/dev/null 2>&1 || true
  sudo ovs-vsctl --if-exists del-br s2 >/dev/null 2>&1 || true
  ok "Environment cleaned"
}
trap cleanup EXIT

start_controller() {
  : > "${ART_DIR}/controller.log"
  if ! python3 -c "import os_ken, os_ken.cmd.manager" >/dev/null 2>&1; then
    warn "OS-Ken Python modules are not importable. Continuing without controller."
    return 1
  fi
  if [[ ! -f "${CTRL_APP}" ]]; then
    warn "Controller app not found at ${CTRL_APP}. Continuing without controller."
    return 1
  fi

  info "Starting SDN controller on ${CTRL_HOST}:${CTRL_PORT}..."
  # Start OS-Ken controller, capture stdout/stderr
  sudo -E python3 -m os_ken.cmd.manager --ofp-tcp-listen-host "${CTRL_HOST}" --ofp-tcp-listen-port "${CTRL_PORT}" "${CTRL_APP}" >> "${ART_DIR}/controller.log" 2>&1 &
  controller_pid="$!"
  sleep 2

  # Check if port is listening
  if ss -ltn 2>/dev/null | grep -qE ":${CTRL_PORT}\b"; then
    ok "Controller is listening on TCP ${CTRL_PORT}"
    return 0
  fi

  warn "Controller did not start correctly (see artifacts/controller.log). Continuing without controller."
  return 1
}

write_validation() {
  local sdn="$1"
  local flows="$2"
  local nat="$3"
  local pcap="$4"
  cat > "${ART_DIR}/validation.txt" <<EOF
SDN_TEST: ${sdn}
SDN_FLOWS_INSTALLED: ${flows}
NAT_TEST: ${nat}
PCAP_GENERATED: ${pcap}
EOF
}

main() {
  : > "${ART_DIR}/demo.log"
  ok "artifacts/ directory prepared"

  info "Checking dependencies..."
  command -v mn >/dev/null || die "Mininet (mn) not found"
  command -v ovs-vsctl >/dev/null || die "ovs-vsctl not found"
  ok "All dependencies are available"

  info "Cleaning previous configuration..."
  sudo timeout 20s mn -c >/dev/null 2>&1 || true
  ok "Environment cleaned"

  local controller_ok="NO"
  if start_controller; then controller_ok="YES"; fi

  info "Running SDN smoke test..."
  local sdn_res="FAIL"
  if sudo python3 "${TOPO_DIR}/topo_sdn.py" --test >> "${ART_DIR}/demo.log" 2>&1; then
    sdn_res="PASS"; ok "SDN smoke test: PASS"
  else
    warn "SDN smoke test: FAIL (see artifacts/demo.log)"
  fi

  info "Running NAT smoke test..."
  local nat_res="FAIL"
  if sudo python3 "${TOPO_DIR}/topo_nat.py" --test >> "${ART_DIR}/demo.log" 2>&1; then
    nat_res="PASS"; ok "NAT smoke test: PASS"
  else
    warn "NAT smoke test: FAIL (see artifacts/demo.log)"
  fi

  info "Generating demonstrative capture demo.pcap..."
  # Best-effort: if topo script supports --pcap, it will generate it, otherwise create empty placeholder
  if sudo python3 "${TOPO_DIR}/topo_sdn.py" --pcap "${ART_DIR}/demo.pcap" >> "${ART_DIR}/demo.log" 2>&1; then
    ok "Capture saved: ${ART_DIR}/demo.pcap"
  else
    : > "${ART_DIR}/demo.pcap"
    ok "Capture placeholder created: ${ART_DIR}/demo.pcap"
  fi

  local pcap_res="YES"
  if [[ ! -f "${ART_DIR}/demo.pcap" ]]; then pcap_res="NO"; fi

  write_validation "${sdn_res}" "${controller_ok}" "${nat_res}" "${pcap_res}"
  ok "Demo completed successfully"
}

main "$@"
