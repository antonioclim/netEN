#!/usr/bin/env bash
set -euo pipefail

BACKDOOR_PORT="${BACKDOOR_PORT:-6200}"
LOG_FILE="/artifacts/vsftpd_backdoor.log"

start_stub_backdoor() {
  # Educational stub: exposes a TCP port to demonstrate detection of an
  # unexpected service. It does NOT provide a shell and does NOT execute input.
  local nc_help
  nc_help="$(nc -h 2>&1 || true)"

  local nc_listen
  if echo "${nc_help}" | grep -q -- "-q "; then
    nc_listen=(nc -l -p "${BACKDOOR_PORT}" -q 1)
  else
    nc_listen=(nc -l -p "${BACKDOOR_PORT}")
  fi

  while true; do
    {
      printf "220 Simulated backdoor (Week 13 lab)\r\n"
      printf "220 This is a SAFE stub. No command execution is implemented.\r\n"
      printf "220 Use this only to observe scanning and logging behaviour.\r\n"
    } | "${nc_listen[@]}" >>"${LOG_FILE}" 2>&1 || true
  done
}

mkdir -p /artifacts || true
touch "${LOG_FILE}" || true

start_stub_backdoor &
exec /usr/sbin/vsftpd /etc/vsftpd.conf
