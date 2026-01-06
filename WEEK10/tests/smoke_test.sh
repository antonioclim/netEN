#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

USE_DOCKER=0
if [[ $# -gt 0 ]]; then
  if [[ "$1" == "--docker" ]]; then
    USE_DOCKER=1
  else
    echo "Usage: $0 [--docker]"
    exit 1
  fi
fi

# Colours (console only)
if [[ -t 1 ]]; then
  ESC=$'\033'
  BLUE="${ESC}[0;34m"
  GREEN="${ESC}[0;32m"
  YELLOW="${ESC}[0;33m"
  RED="${ESC}[0;31m"
  NC="${ESC}[0m"
else
  BLUE=""; GREEN=""; YELLOW=""; RED=""; NC=""
fi

pass=0
fail=0
warn=0

hr() {
  echo "${BLUE}══════════════════════════════════════════════════════════${NC}"
}

title() {
  hr
  echo "${BLUE}$1${NC}"
  hr
}

ok() {
  echo "${GREEN}✓${NC} $1"
  pass=$((pass+1))
}

bad() {
  echo "${RED}✗${NC} $1"
  fail=$((fail+1))
}

note() {
  echo "${YELLOW}!${NC} $1"
  warn=$((warn+1))
}

choose_python() {
  if [[ -x "${ROOT_DIR}/.venv/bin/python" ]]; then
    echo "${ROOT_DIR}/.venv/bin/python"
  else
    echo "python3"
  fi
}

run() {
  local desc="$1"; shift
  if "$@" >/dev/null 2>&1; then
    ok "${desc}"
    return 0
  fi
  bad "${desc}"
  return 1
}

title "Smoke test - Week 10 kit"

cd "${ROOT_DIR}"

# --- File structure ----------------------------------------------------------
run "README.md present" test -f README.md
run "Makefile present" test -f Makefile
run "scripts/ present" test -d scripts
run "python/ present" test -d python
run "docker/docker-compose.yml present" test -f docker/docker-compose.yml

# --- Basic commands ----------------------------------------------------------
run "python3 available" command -v python3
run "openssl available" command -v openssl
run "curl available" command -v curl

# --- Python dependencies -----------------------------------------------------
PY_BIN="$(choose_python)"
if ! "${PY_BIN}" -c "import requests, flask, paramiko" >/dev/null 2>&1; then
  note "Python dependencies not importable with ${PY_BIN}. Run: make setup"
else
  ok "Python dependencies importable"
fi

# --- Exercise self-tests -----------------------------------------------------
if "${PY_BIN}" -c "import requests" >/dev/null 2>&1; then
  run "HTTPS exercise self-test" "${PY_BIN}" python/exercises/ex_10_01_https.py selftest
else
  note "Skipping HTTPS exercise self-test (requests not available)"
fi

if "${PY_BIN}" -c "import flask" >/dev/null 2>&1; then
  run "REST levels exercise self-test" "${PY_BIN}" python/exercises/ex_10_02_rest_levels.py selftest
else
  note "Skipping REST levels exercise self-test (flask not available)"
fi

# --- Optional Docker check ---------------------------------------------------
if [[ ${USE_DOCKER} -eq 1 ]]; then
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    ok "Docker available"
    # Keep this light: just verify the Compose file is runnable.
    if (cd docker && docker compose config >/dev/null 2>&1); then
      ok "docker compose config valid"
    else
      bad "docker compose config invalid"
    fi
  else
    note "Docker not available or daemon not reachable (skipping Docker checks)"
  fi
fi

hr
echo "PASS: ${pass}  WARN: ${warn}  FAIL: ${fail}"

if [[ ${fail} -ne 0 ]]; then
  exit 1
fi
exit 0
