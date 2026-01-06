#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="${ROOT_DIR}/artifacts"
LOG_FILE="${ART_DIR}/demo.log"
VAL_FILE="${ART_DIR}/validation.txt"
PCAP_FILE="${ART_DIR}/demo.pcap"

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
    '(tcp port 8000 or tcp port 22 or tcp port 2121 or udp port 5353)' \
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
  log_info "Stopping Docker stack"
  compose down -v >/dev/null 2>&1 || true
}

main() {
  cd "${ROOT_DIR}"

  # Fresh artefacts
  rm -f "${LOG_FILE}" "${VAL_FILE}" "${PCAP_FILE}" 2>/dev/null || true
  : >"${LOG_FILE}"

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

  log_info "Bringing up Docker services (docker compose up -d --build)"
  cleanup_stack
  compose up -d --build >/dev/null

  # Wait for key services
  local stack_ok=1
  for svc in web dns-server ssh-server ftp-server; do
    log_info "Waiting for service '${svc}'"
    if wait_running_or_healthy "${svc}" 40; then
      log_ok "${svc} ready"
    else
      log_warn "${svc} did not become healthy within timeout"
      stack_ok=0
    fi
  done

  start_capture

  # Tests
  local http_ok=0 dns_ok=0 ssh_ok=0 ftp_ok=0

  log_info "HTTP test (GET http://127.0.0.1:8000/hello.txt)"
  if curl -fsS "http://127.0.0.1:8000/hello.txt" >/dev/null 2>&1; then
    http_ok=1
    log_ok "HTTP: PASS"
  else
    log_warn "HTTP: FAIL"
  fi

  log_info "DNS test (custom server on udp/5353)"
  if compose exec -T debug sh -lc "dig @dns-server -p 5353 myservice.lab.local +short | grep -qx 10.10.10.10" >/dev/null 2>&1; then
    dns_ok=1
    log_ok "DNS: PASS"
  else
    log_warn "DNS: FAIL"
  fi

  log_info "SSH test (Paramiko client container -> ssh-server)"
  if compose exec -T ssh-client python3 /app/paramiko_client.py >/dev/null 2>&1; then
    ssh_ok=1
    log_ok "SSH: PASS"
  else
    log_warn "SSH: FAIL"
  fi

  log_info "FTP test (ftplib -> localhost:2121)"
  if python3 - <<'PY'
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

  stop_capture

  # Validation report
  {
    echo "DOCKER_STACK: $([[ ${stack_ok} -eq 1 ]] && echo OK || echo DEGRADED)"
    echo "HTTP_TEST: $([[ ${http_ok} -eq 1 ]] && echo PASS || echo FAIL)"
    echo "DNS_TEST: $([[ ${dns_ok} -eq 1 ]] && echo PASS || echo FAIL)"
    echo "SSH_TEST: $([[ ${ssh_ok} -eq 1 ]] && echo PASS || echo FAIL)"
    echo "FTP_TEST: $([[ ${ftp_ok} -eq 1 ]] && echo PASS || echo FAIL)"
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

  cleanup_stack

  # Final status
  local overall=0
  if [[ ${http_ok} -eq 1 && ${dns_ok} -eq 1 && ${ssh_ok} -eq 1 && ${ftp_ok} -eq 1 ]]; then
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
