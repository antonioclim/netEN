#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="${ROOT_DIR}/artifacts"
ENV_FILE="${ROOT_DIR}/.env"
VENV_PY="${ROOT_DIR}/.venv/bin/python"

PYTHON="python3"
if [ -x "${VENV_PY}" ]; then
  PYTHON="${VENV_PY}"
fi

log() {
  # Plain log line with timestamp, suitable for files
  printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "${ARTIFACTS_DIR}/demo.log" >/dev/null
}

read_env() {
  local key="$1"
  if [ -f "${ENV_FILE}" ]; then
    grep -E "^${key}=" "${ENV_FILE}" | tail -n 1 | cut -d= -f2- || true
  fi
}

main() {
  mkdir -p "${ARTIFACTS_DIR}"
  : > "${ARTIFACTS_DIR}/demo.log"
  : > "${ARTIFACTS_DIR}/validation.txt"

  log "Week 13 automated run started"
  log "Python: ${PYTHON}"

  if [ ! -f "${ENV_FILE}" ]; then
    log "WARN: .env not found. Run: make env"
  fi

  local dvwa_port ftp_port ftp_backdoor_port mqtt_plain mqtt_tls
  dvwa_port="$(read_env DVWA_HOST_PORT)"
  ftp_port="$(read_env VSFTPD_HOST_PORT)"
  ftp_backdoor_port="$(read_env VSFTPD_BACKDOOR_HOST_PORT)"
  mqtt_plain="$(read_env MQTT_PLAIN_PORT)"
  mqtt_tls="$(read_env MQTT_TLS_PORT)"

  dvwa_port="${dvwa_port:-8080}"
  ftp_port="${ftp_port:-2121}"
  ftp_backdoor_port="${ftp_backdoor_port:-6200}"
  mqtt_plain="${mqtt_plain:-1883}"
  mqtt_tls="${mqtt_tls:-8883}"

  log "Using ports: DVWA=${dvwa_port}, vsftpd=${ftp_port}, vsftpd_backdoor=${ftp_backdoor_port}, MQTT=${mqtt_plain}, MQTT_TLS=${mqtt_tls}"

  # 1) Port scan
  log "Running port scan on 127.0.0.1..."
  set +e
  "${PYTHON}" "${ROOT_DIR}/python/exercises/ex_01_port_scanner.py"     --target "127.0.0.1"     --ports "21,22,80,${mqtt_plain},${mqtt_tls},${dvwa_port},${ftp_port},${ftp_backdoor_port}"     --mode scan     --json-out "${ARTIFACTS_DIR}/scan_results.json" >> "${ARTIFACTS_DIR}/demo.log" 2>&1
  scan_rc=$?
  set -e
  if [ ${scan_rc} -eq 0 ] && [ -s "${ARTIFACTS_DIR}/scan_results.json" ]; then
    log "Port scan completed"
    echo "SCAN: PASS" >> "${ARTIFACTS_DIR}/validation.txt"
  else
    log "WARN: Port scan failed (rc=${scan_rc})"
    echo "SCAN: FAIL" >> "${ARTIFACTS_DIR}/validation.txt"
  fi

  # Count open ports (best effort)
  open_ports_count="$("${PYTHON}" - <<'PY'
import json, sys, pathlib
p = pathlib.Path("artifacts/scan_results.json")
if not p.exists() or p.stat().st_size == 0:
    print(0); sys.exit(0)
js = json.loads(p.read_text())
hosts = (js.get("scan_report") or {}).get("hosts", js.get("hosts", []))
count = 0
for h in hosts:
    count += len(h.get("open_ports", []))
print(count)
PY
  )" || open_ports_count="0"
  log "Open ports detected (best effort count): ${open_ports_count}"

  # 2) MQTT plaintext demo
  log "MQTT plaintext publish demo..."
  set +e
  "${PYTHON}" "${ROOT_DIR}/python/exercises/ex_02_mqtt_client.py"     --broker "127.0.0.1"     --port "${mqtt_plain}"     --mode publish     --topic "iot/sensors/temperature"     --message '{"sensor":"temp","value":24.3}'     --count 3     --qos 0 >> "${ARTIFACTS_DIR}/demo.log" 2>&1
  mqtt_plain_rc=$?
  set -e
  if [ ${mqtt_plain_rc} -eq 0 ]; then
    log "MQTT plaintext demo: PASS"
    echo "MQTT_PLAIN: PASS" >> "${ARTIFACTS_DIR}/validation.txt"
  else
    log "WARN: MQTT plaintext demo: FAIL (rc=${mqtt_plain_rc})"
    echo "MQTT_PLAIN: FAIL" >> "${ARTIFACTS_DIR}/validation.txt"
  fi

  # 3) MQTT TLS demo
  log "MQTT TLS publish demo..."
  set +e
  "${PYTHON}" "${ROOT_DIR}/python/exercises/ex_02_mqtt_client.py"     --broker "127.0.0.1"     --port "${mqtt_tls}"     --mode publish     --topic "iot/sensors/temperature"     --message '{"sensor":"temp","value":24.3}'     --count 3     --qos 0     --tls     --cafile "${ROOT_DIR}/configs/certs/ca.crt" >> "${ARTIFACTS_DIR}/demo.log" 2>&1
  mqtt_tls_rc=$?
  set -e
  if [ ${mqtt_tls_rc} -eq 0 ]; then
    log "MQTT TLS demo: PASS"
    echo "MQTT_TLS: PASS" >> "${ARTIFACTS_DIR}/validation.txt"
  else
    log "WARN: MQTT TLS demo: FAIL (rc=${mqtt_tls_rc})"
    echo "MQTT_TLS: FAIL" >> "${ARTIFACTS_DIR}/validation.txt"
  fi

  # 4) FTP backdoor check (safe)
  log "FTP backdoor check demonstration..."
  set +e
  "${PYTHON}" "${ROOT_DIR}/python/exploits/ftp_backdoor_vsftpd.py"     --target "127.0.0.1"     --ftp-port "${ftp_port}"     --backdoor-port "${ftp_backdoor_port}"     --command "id" >> "${ARTIFACTS_DIR}/demo.log" 2>&1
  ftp_rc=$?
  set -e
  if [ ${ftp_rc} -eq 0 ] || [ ${ftp_rc} -eq 2 ]; then
    # 2 is accepted as "not vulnerable / stub detected"
    log "FTP check completed"
    echo "FTP_CHECK: PASS" >> "${ARTIFACTS_DIR}/validation.txt"
  else
    log "WARN: FTP check failed (rc=${ftp_rc})"
    echo "FTP_CHECK: FAIL" >> "${ARTIFACTS_DIR}/validation.txt"
  fi

  # 5) Vulnerability checker demo (best effort)
  log "Vulnerability checker demo (best effort)..."
  set +e
  "${PYTHON}" "${ROOT_DIR}/python/exercises/ex_04_vuln_checker.py"     --target "127.0.0.1"     --port "${dvwa_port}"     --service http >> "${ARTIFACTS_DIR}/demo.log" 2>&1
  vuln_rc=$?
  set -e
  if [ ${vuln_rc} -eq 0 ]; then
    log "Vulnerability checker: PASS"
    echo "VULN_CHECK: PASS" >> "${ARTIFACTS_DIR}/validation.txt"
  else
    log "WARN: Vulnerability checker: FAIL (rc=${vuln_rc})"
    echo "VULN_CHECK: FAIL" >> "${ARTIFACTS_DIR}/validation.txt"
  fi

  log "Week 13 automated run finished"
}

main "$@"
