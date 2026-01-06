#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON="${VENV_DIR}/bin/python"

banner() {
  printf "\n========================================================================\n"
  printf "  %s\n" "$1"
  printf "========================================================================\n"
}

check_cmd() {
  local name="$1"
  local cmd="$2"
  if command -v "${cmd}" >/dev/null 2>&1; then
    printf "  ✓ %s (%s)\n" "${name}" "${cmd}"
    return 0
  fi
  printf "  ✗ %s (%s)\n" "${name}" "${cmd}"
  return 1
}

check_py_import() {
  local module="$1"
  if [ -x "${PYTHON}" ]; then
    if "${PYTHON}" -c "import ${module}" >/dev/null 2>&1; then
      printf "  ✓ Python module: %s\n" "${module}"
      return 0
    fi
    printf "  ✗ Python module: %s (not importable in .venv)\n" "${module}"
    return 1
  fi
  printf "  ! Python module: %s (.venv not found, run: make setup)\n" "${module}"
  return 1
}

banner "Week 13 - Environment verification"

fail=0

printf "\nEssential tools:\n"
check_cmd "Python 3" "python3" || fail=1
check_cmd "Docker" "docker" || fail=1
if docker compose version >/dev/null 2>&1; then
  printf "  ✓ docker compose\n"
else
  printf "  ✗ docker compose\n"
  fail=1
fi

printf "\nTraffic and diagnostics:\n"
check_cmd "curl" "curl" || true
check_cmd "netcat" "nc" || true
check_cmd "tcpdump (optional)" "tcpdump" || true
check_cmd "tshark (optional)" "tshark" || true

printf "\nMininet (optional):\n"
check_cmd "mininet" "mn" || true
check_cmd "Open vSwitch" "ovs-vsctl" || true

printf "\nKit structure:\n"
[ -f "${ROOT_DIR}/Makefile" ] && printf "  ✓ Makefile\n" || { printf "  ✗ Makefile missing\n"; fail=1; }
[ -f "${ROOT_DIR}/README.md" ] && printf "  ✓ README.md\n" || { printf "  ✗ README.md missing\n"; fail=1; }
[ -d "${ROOT_DIR}/python" ] && printf "  ✓ python/\n" || { printf "  ✗ python/ missing\n"; fail=1; }
[ -d "${ROOT_DIR}/docker" ] && printf "  ✓ docker/\n" || { printf "  ✗ docker/ missing\n"; fail=1; }

printf "\nPython modules (venv):\n"
check_py_import "paho.mqtt.client" || fail=1
check_py_import "scapy.all" || true

printf "\nResult:\n"
if [ "${fail}" -eq 0 ]; then
  printf "  ✓ Verification complete\n\n"
else
  printf "  ✗ Verification failed. Run: make setup\n\n"
  exit 1
fi
