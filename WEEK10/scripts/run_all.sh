#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="${ROOT_DIR}/artifacts"
LOG_FILE="${ART_DIR}/demo.log"
VAL_FILE="${ART_DIR}/validation.txt"
PCAP_FILE="${ART_DIR}/demo.pcap"

# Additional logs (always created, even on failure)
DOCKER_STATUS_LOG="${ART_DIR}/docker_status.log"
HTTP_TEST_LOG="${ART_DIR}/http_test.log"
DNS_TEST_LOG="${ART_DIR}/dns_test.log"
SSH_TEST_LOG="${ART_DIR}/ssh_test.log"
FTP_TEST_LOG="${ART_DIR}/ftp_test.log"
HTTPS_SELFTEST_LOG="${ART_DIR}/https_selftest.log"
REST_SELFTEST_LOG="${ART_DIR}/rest_selftest.log"

mkdir -p "${ART_DIR}"

# Console colours (log file always plain text)
if [[ -t 1 ]]; then
  ESC=$'\033'
  GREEN="${ESC}[0;32m"
  YELLOW="${ESC}[0;33m"
  RED="${ESC}[0;31m"
  NC="${ESC}[0m"
else
  GREEN=""; YELLOW=""; RED=""; NC=""
fi

log() {
  local level="$1"; shift
  local msg="$*"
  local ts
  ts="$(date +'%Y-%m-%d %H:%M:%S')"
  echo "[${ts}] [${level}] ${msg}" | tee -a "${LOG_FILE}"
}

log_info() { log "INFO" "$*"; }
log_ok() { log "OK" "$*"; }
log_warn() { log "WARN" "$*"; }
log_err() { log "ERROR" "$*"; }

compose() {
  (cd "${ROOT_DIR}/docker" && docker compose "$@")
}

have() { command -v "$1" >/dev/null 2>&1; }

wait_running_or_healthy() {
  local service="$1"
  local timeout_s="$2"
  local start
  start="$(date +%s)"

  while true; do
    local id
    id="$(compose ps -q "${service}" 2>/dev/null || true)"
    if [[ -n "${id}" ]]; then
      local state health
      state="$(docker inspect -f '{{.State.Status}}' "${id}" 2>/dev/null || true)"
      health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "${id}" 2>/dev/null || true)"

      if [[ "${state}" == "running" ]]; then
        if [[ -z "${health}" || "${health}" == "healthy" ]]; then
          return 0
        fi
      fi
    fi

    local now
    now="$(date +%s)"
    if (( now - start >= timeout_s )); then
      return 1
    fi
    sleep 1
  done
}

start_capture() {
  # Captures traffic for the duration of the demo.
  # Requires root (or a capability-enabled tcpdump).
  rm -f "${PCAP_FILE}" || true

  if ! have tcpdump; then
    log_warn "tcpdump not found. Creating an empty pcap placeholder."
    : > "${PCAP_FILE}"
    echo "0" >"${ART_DIR}/pcap_pid" || true
    return 0
  fi

  if [[ "${EUID}" -ne 0 ]]; then
    log_warn "Not running as root. Creating an empty pcap placeholder (run with sudo for capture)."
    : > "${PCAP_FILE}"
    echo "0" >"${ART_DIR}/pcap_pid" || true
    return 0
  fi

  log_info "Starting tcpdump capture: ${PCAP_FILE}"
  tcpdump -i any -w "${PCAP_FILE}" \
    '(tcp port 8000 or tcp port 8443 or tcp port 5000 or tcp port 22 or tcp port 2222 or tcp port 2121 or udp port 5353)' \
    >/dev/null 2>&1 &
  echo $! >"${ART_DIR}/pcap_pid"
}

stop_capture() {
  local pid
  pid="$(cat "${ART_DIR}/pcap_pid" 2>/dev/null || echo 0)"
  if [[ "${pid}" != "0" ]]; then
    kill "${pid}" >/dev/null 2>&1 || true
    wait "${pid}" >/dev/null 2>&1 || true
  fi

  rm -f "${ART_DIR}/pcap_pid" || true

  if [[ -f "${PCAP_FILE}" ]]; then
    local size
    size="$(stat -c%s "${PCAP_FILE}" 2>/dev/null || echo 0)"
    if [[ "${size}" -gt 0 ]]; then
      log_ok "pcap generated (${size} bytes)"
    else
      log_warn "pcap file is empty (this is expected if capture was not permitted)"
    fi
  fi
}

cleanup_stack() {
  if [[ "${STACK_STARTED:-0}" -eq 1 && "${STACK_CLEANED:-0}" -eq 0 ]]; then
    log_info "Stopping Docker stack"
    compose down -v >/dev/null 2>&1 || true
    STACK_CLEANED=1
  fi
}

main() {
  cd "${ROOT_DIR}"

  STACK_STARTED=0
  STACK_CLEANED=0

  # Fresh artefacts
  rm -f "${LOG_FILE}" "${VAL_FILE}" "${PCAP_FILE}" 2>/dev/null || true
  : >"${LOG_FILE}"

  : >"${DOCKER_STATUS_LOG}"
  : >"${HTTP_TEST_LOG}"
  : >"${DNS_TEST_LOG}"
  : >"${SSH_TEST_LOG}"
  : >"${FTP_TEST_LOG}"

  log_ok "artifacts/ directory prepared"

  if ! have docker; then
    log_err "Docker is not installed. Cannot run the full Week 10 demo."
    echo "DOCKER_AVAILABLE: NO" >"${VAL_FILE}"
    exit 1
  fi

  if ! docker info >/dev/null 2>&1; then
    log_err "Docker daemon is not accessible. Is the service running and is your user in the docker group?"
    echo "DOCKER_AVAILABLE: NO" >"${VAL_FILE}"
    exit 1
  fi

  log_info "Bringing up Docker services (docker compose build + up)"
  # Clean any previous state (networks, volumes)
  log_info "Cleaning previous Docker state"
  compose down -v >/dev/null 2>&1 || true
  # Build all images required for the automated demo, including the short-lived
  # SSH client container used in the SSH test.
  compose build web dns-server ssh-server ftp-server debug ssh-client >/dev/null
  compose up -d web dns-server ssh-server ftp-server debug >/dev/null
  STACK_STARTED=1

  # Wait for key services
  local stack_ok=1
  for svc in web dns-server ssh-server ftp-server debug; do
    log_info "Waiting for service '${svc}'"
    if wait_running_or_healthy "${svc}" 40; then
      log_ok "${svc} ready"
    else
      log_warn "${svc} did not become healthy within timeout"
      stack_ok=0
    fi
  done

  # Save a status snapshot for debugging
  {
    echo "=== docker compose ps ==="
    compose ps || true
    echo
    echo "=== docker compose images ==="
    compose images || true
  } >>"${DOCKER_STATUS_LOG}" 2>&1 || true

  start_capture

  # Tests
  local http_ok=0 dns_ok=0 ssh_ok=0 ftp_ok=0

  log_info "HTTP test (GET http://127.0.0.1:8000/hello.txt)"
  if curl -fsS "http://127.0.0.1:8000/hello.txt" >"${HTTP_TEST_LOG}" 2>&1; then
    http_ok=1
    log_ok "HTTP: PASS"
  else
    log_warn "HTTP: FAIL"
  fi

  log_info "DNS test (custom server on udp/5353)"
  if compose exec -T debug sh -lc "dig @dns-server -p 5353 myservice.lab.local +short" >"${DNS_TEST_LOG}" 2>&1 && grep -qx "10.10.10.10" "${DNS_TEST_LOG}"; then
    dns_ok=1
    log_ok "DNS: PASS"
  else
    log_warn "DNS: FAIL"
  fi

  log_info "SSH test (Paramiko client container -> ssh-server)"
  # Use `docker compose run` instead of `exec` so that the SSH client does not
  # need to run as a long-lived container.
  if compose run --rm --no-deps --build -T ssh-client python3 /app/paramiko_client.py >"${SSH_TEST_LOG}" 2>&1; then
    ssh_ok=1
    log_ok "SSH: PASS"
  else
    log_warn "SSH: FAIL"
    log_warn "SSH test output (last 20 lines):"
    tail -n 20 "${SSH_TEST_LOG}" | while IFS= read -r line; do log_warn "  ${line}"; done
  fi

  log_info "FTP test (ftplib -> localhost:2121)"
  if python3 - >"${FTP_TEST_LOG}" 2>&1 <<'PY'
import ftplib
try:
    ftp = ftplib.FTP()
    ftp.connect("127.0.0.1", 2121, timeout=6)
    ftp.login("labftp", "labftp")
    ftp.nlst()
    ftp.quit()
    print("OK")
except Exception as e:
    print("FAIL", e)
    raise
PY
  then
    ftp_ok=1
    log_ok "FTP: PASS"
  else
    log_warn "FTP: FAIL"
  fi

  # ---------------------------------------------------------------------------
  # HTTPS and REST maturity selftests (local Python)
  # ---------------------------------------------------------------------------
  local https_ok=0
  local rest_ok=0
  local https_status="SKIP"
  local rest_status="SKIP"
  local venv_py="${ROOT_DIR}/.venv/bin/python3"

  if [[ -x "${venv_py}" ]]; then
    if [[ -f "${ROOT_DIR}/python/exercises/ex_10_01_https.py" ]]; then
      log_info "HTTPS selftest (local TLS server on 127.0.0.1:8443)"
      if "${venv_py}" "${ROOT_DIR}/python/exercises/ex_10_01_https.py" selftest >"${HTTPS_SELFTEST_LOG}" 2>&1; then
        https_ok=1
        https_status="PASS"
        log_ok "HTTPS selftest: PASS"
      else
        https_status="FAIL"
        log_warn "HTTPS selftest: FAIL"
        log_warn "HTTPS selftest output (last 20 lines):"
        tail -n 20 "${HTTPS_SELFTEST_LOG}" | while IFS= read -r line; do log_warn "  ${line}"; done
      fi
    else
      log_warn "HTTPS selftest skipped (missing python/exercises/ex_10_01_https.py)"
      echo "SKIPPED (missing script)" >"${HTTPS_SELFTEST_LOG}"
    fi

    if [[ -f "${ROOT_DIR}/python/exercises/ex_10_02_rest_levels.py" ]]; then
      log_info "REST maturity selftest (local Flask API on 127.0.0.1:5000)"
      if "${venv_py}" "${ROOT_DIR}/python/exercises/ex_10_02_rest_levels.py" selftest >"${REST_SELFTEST_LOG}" 2>&1; then
        rest_ok=1
        rest_status="PASS"
        log_ok "REST selftest: PASS"
      else
        rest_status="FAIL"
        log_warn "REST selftest: FAIL"
        log_warn "REST selftest output (last 20 lines):"
        tail -n 20 "${REST_SELFTEST_LOG}" | while IFS= read -r line; do log_warn "  ${line}"; done
      fi
    else
      log_warn "REST selftest skipped (missing python/exercises/ex_10_02_rest_levels.py)"
      echo "SKIPPED (missing script)" >"${REST_SELFTEST_LOG}"
    fi
  else
    log_warn "Python virtual environment not found (.venv). Run 'make setup' then re-run this demo."
    https_status="FAIL"
    rest_status="FAIL"
    echo "FAILED (missing .venv). Run make setup." >"${HTTPS_SELFTEST_LOG}"
    echo "FAILED (missing .venv). Run make setup." >"${REST_SELFTEST_LOG}"
  fi

  stop_capture

  # Validation report
  {
    echo "DOCKER_STACK: $([[ ${stack_ok} -eq 1 ]] && echo OK || echo DEGRADED)"
    echo "HTTP_TEST: $([[ ${http_ok} -eq 1 ]] && echo PASS || echo FAIL)"
    echo "DNS_TEST: $([[ ${dns_ok} -eq 1 ]] && echo PASS || echo FAIL)"
    echo "SSH_TEST: $([[ ${ssh_ok} -eq 1 ]] && echo PASS || echo FAIL)"
    echo "FTP_TEST: $([[ ${ftp_ok} -eq 1 ]] && echo PASS || echo FAIL)"
    echo "HTTPS_SELFTEST: ${https_status}"
    echo "REST_SELFTEST: ${rest_status}"
    if [[ -f "${PCAP_FILE}" ]]; then
      if [[ "$(stat -c%s "${PCAP_FILE}" 2>/dev/null || echo 0)" -gt 0 ]]; then
        echo "PCAP_GENERATED: YES"
      else
        echo "PCAP_GENERATED: EMPTY"
      fi
    else
      echo "PCAP_GENERATED: NO"
    fi
  } >"${VAL_FILE}"

  log_ok "Validation written: ${VAL_FILE}"

  # Final status
  local overall=0
  if [[ ${stack_ok} -eq 1 && ${http_ok} -eq 1 && ${dns_ok} -eq 1 && ${ssh_ok} -eq 1 && ${ftp_ok} -eq 1 && ${https_ok} -eq 1 && ${rest_ok} -eq 1 ]]; then
    overall=1
  fi

  if [[ ${overall} -eq 1 ]]; then
    echo "${GREEN}✓ Demo completed successfully. See artifacts/demo.log and artifacts/validation.txt${NC}"
    exit 0
  fi

  echo "${YELLOW}! Demo completed with warnings. See artifacts/demo.log and artifacts/validation.txt${NC}"
  exit 0
}

trap 'stop_capture; cleanup_stack' EXIT
main "$@"
