#!/usr/bin/env bash
# ============================================================================
# run_all.sh - Automated demo for Week 6 (NAT/PAT & SDN/OpenFlow)
#
# Goals:
#   - Produce reproducible artefacts in ./artifacts/
#   - Avoid brittle OS-Ken CLI assumptions on Ubuntu 24.04 with os-ken 4.x
#   - Demonstrate SDN policy using controller-less OVS flow rules
#
# Artefacts:
#   - artifacts/demo.log
#   - artifacts/controller.log
#   - artifacts/demo.pcap
#   - artifacts/validation.txt
#
# British English is used throughout (no Oxford comma).
# ============================================================================

set -u
set -o pipefail

ARTIFACTS_DIR="artifacts"
DEMO_LOG="${ARTIFACTS_DIR}/demo.log"
CTRL_LOG="${ARTIFACTS_DIR}/controller.log"
VALIDATION="${ARTIFACTS_DIR}/validation.txt"
PCAP_FILE="${ARTIFACTS_DIR}/demo.pcap"

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  SUDO="sudo"
fi

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

log_line() {
  # $1 = level, $2... message
  local level="$1"; shift
  local msg="$*"
  echo "[${level}] ${msg}"
  echo "[$(timestamp)] [${level}] ${msg}" >> "${DEMO_LOG}"
}

log_info() { log_line "INFO" "$@"; }
log_ok()   { log_line "OK" "$@"; }
log_warn() { log_line "WARN" "$@"; }
log_err()  { log_line "ERROR" "$@"; }

prepare_artifacts() {
  mkdir -p "${ARTIFACTS_DIR}"
  : > "${DEMO_LOG}"
  : > "${CTRL_LOG}"
  : > "${VALIDATION}"
  rm -f "${PCAP_FILE}" 2>/dev/null || true

  # If invoked via sudo, make artefacts readable for the original user.
  if [ -n "${SUDO_USER-}" ] && [ "${SUDO_USER}" != "root" ]; then
    chown -R "${SUDO_USER}:${SUDO_USER}" "${ARTIFACTS_DIR}" 2>/dev/null || true
  fi

  log_ok "artifacts/ directory prepared"
}

controller_preflight() {
  {
    echo "=== Controller preflight ==="
    echo "python: $(command -v python3 || echo 'NOT FOUND')"
    python3 -c "import sys; print('version:', sys.version); print('sys.path:'); print('\n'.join('  '+p for p in sys.path))" 2>/dev/null || true

    if python3 -c "import os_ken" >/dev/null 2>&1; then
      echo "os_ken: import OK"
    else
      echo "os_ken: import FAIL"
    fi

    if command -v osken-manager >/dev/null 2>&1; then
      echo "osken-manager: FOUND ($(command -v osken-manager))"
    else
      echo "osken-manager: NOT FOUND"
    fi

    echo ""
    echo "This starter kit defaults to controller-less SDN mode (OVS flows)."
    echo "If you require an OS-Ken controller, pin: pip install 'os-ken<4.0.0'."
    echo "=== End preflight ==="
  } >> "${CTRL_LOG}"
}

safe_cleanup() {
  log_info "Cleaning previous configuration..."
  # Conservative cleanup: rely on Mininet plus OVS bridge removal.
  timeout 15s ${SUDO} mn -c 2>/dev/null || true
  timeout 10s ${SUDO} ovs-vsctl --if-exists del-br s1 2>/dev/null || true
  timeout 10s ${SUDO} ovs-vsctl --if-exists del-br s2 2>/dev/null || true
  log_ok "Environment cleaned"
}

check_dependencies() {
  log_info "Checking dependencies..."

  local missing=0

  for cmd in python3 mn ovs-vsctl ovs-ofctl iptables tcpdump; do
    if ! command -v "${cmd}" >/dev/null 2>&1; then
      log_err "Missing command: ${cmd}"
      missing=1
    fi
  done

  if ! python3 -c "import os_ken" >/dev/null 2>&1; then
    log_warn "Python module os_ken not importable (SDN will still run in OVS-flow mode)"
  else
    log_ok "Python module os_ken importable"
  fi

  if ! python3 -c "import scapy" >/dev/null 2>&1; then
    log_warn "Python module scapy not importable (optional for this lab)"
  else
    log_ok "Python module scapy importable"
  fi

  if [ "${missing}" -eq 0 ]; then
    log_ok "All dependencies are available"
    return 0
  fi

  log_err "Missing dependencies detected"
  return 1
}

run_sdn_smoke_test() {
  log_info "Running SDN smoke test (OVS OpenFlow rules)..."
  if ${SUDO} python3 mininet/topologies/topo_sdn.py --mode ovs --test >/dev/null 2>&1; then
    log_ok "SDN smoke test: PASS"
    echo "SDN_TEST: PASS" >> "${VALIDATION}"
    echo "SDN_FLOWS_INSTALLED: YES" >> "${VALIDATION}"
    return 0
  else
    log_warn "SDN smoke test: FAIL"
    echo "SDN_TEST: FAIL" >> "${VALIDATION}"
    echo "SDN_FLOWS_INSTALLED: NO" >> "${VALIDATION}"
    return 1
  fi
}

run_nat_smoke_test_and_capture() {
  log_info "Running NAT smoke test and capture..."
  if ${SUDO} python3 mininet/topologies/topo_nat.py --test --pcap "${PCAP_FILE}" >/dev/null 2>&1; then
    log_ok "NAT smoke test: PASS"
    echo "NAT_TEST: PASS" >> "${VALIDATION}"
    return 0
  else
    log_warn "NAT smoke test: FAIL"
    echo "NAT_TEST: FAIL" >> "${VALIDATION}"
    return 1
  fi
}

validate_pcap() {
  if [ -f "${PCAP_FILE}" ] && [ "$(stat -c%s "${PCAP_FILE}" 2>/dev/null || echo 0)" -gt 24 ]; then
    log_ok "PCAP generated: ${PCAP_FILE}"
    echo "PCAP_GENERATED: YES" >> "${VALIDATION}"
    return 0
  fi

  log_warn "PCAP missing or empty: ${PCAP_FILE}"
  echo "PCAP_GENERATED: NO" >> "${VALIDATION}"
  return 1
}

main() {
  prepare_artifacts
  controller_preflight

  if ! check_dependencies; then
    safe_cleanup
    log_err "Stopping due to missing dependencies"
    exit 1
  fi

  safe_cleanup

  local sdn_rc=0
  local nat_rc=0
  local pcap_rc=0

  run_sdn_smoke_test || sdn_rc=$?
  safe_cleanup

  run_nat_smoke_test_and_capture || nat_rc=$?
  safe_cleanup

  validate_pcap || pcap_rc=$?

  log_ok "Demo completed (artefacts generated)"

  if [ "${sdn_rc}" -ne 0 ] || [ "${nat_rc}" -ne 0 ] || [ "${pcap_rc}" -ne 0 ]; then
    log_warn "One or more checks failed (see artifacts/validation.txt)"
    exit 1
  fi

  exit 0
}

main "$@"
