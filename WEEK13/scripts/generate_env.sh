#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-.env}"
DVWA_HINT="${2:-8080}"
VSFTPD_HINT="${3:-2121}"
MQTT_PLAIN_HINT="${4:-1883}"
MQTT_TLS_HINT="${5:-8883}"
VSFTPD_BACKDOOR_HINT="${6:-6200}"

is_port_free() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ! ss -ltnH | awk '{print $4}' | grep -Eq "(:|\.)${port}$"
  elif command -v lsof >/dev/null 2>&1; then
    ! lsof -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1
  else
    # Best effort fallback: assume free
    return 0
  fi
}

pick_port() {
  local start="$1"
  local p
  for p in $(seq "${start}" "$((start+50))"); do
    if is_port_free "${p}"; then
      echo "${p}"
      return 0
    fi
  done
  # Fall back to the starting port
  echo "${start}"
}

if [ -f "${ENV_FILE}" ]; then
  # Keep existing configuration for reproducibility
  exit 0
fi

DVWA_PORT="$(pick_port "${DVWA_HINT}")"
VSFTPD_PORT="$(pick_port "${VSFTPD_HINT}")"
VSFTPD_BACKDOOR_PORT="$(pick_port "${VSFTPD_BACKDOOR_HINT}")"

# MQTT ports are rarely used on desktop systems, keep the standard values
MQTT_PLAIN_PORT="${MQTT_PLAIN_HINT}"
MQTT_TLS_PORT="${MQTT_TLS_HINT}"

cat > "${ENV_FILE}" <<EOF
# Week 13 - Docker port mapping
# If a port is in use on your machine, delete this file and run: make env

DVWA_HOST_PORT=${DVWA_PORT}
VSFTPD_HOST_PORT=${VSFTPD_PORT}
VSFTPD_BACKDOOR_HOST_PORT=${VSFTPD_BACKDOOR_PORT}
MQTT_PLAIN_PORT=${MQTT_PLAIN_PORT}
MQTT_TLS_PORT=${MQTT_TLS_PORT}
EOF
