#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colours
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

banner() {
  echo "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
  echo "${BLUE}  Working Environment Verification - Week 10${NC}"
  echo "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
  echo
}

pass() { echo "  ${GREEN}✓${NC} $1"; }
warn() { echo "  ${YELLOW}○${NC} $1"; }
fail() { echo "  ${RED}✗${NC} $1"; }

have() { command -v "$1" >/dev/null 2>&1; }

py() {
  if [[ -x "${ROOT_DIR}/.venv/bin/python" ]]; then
    echo "${ROOT_DIR}/.venv/bin/python"
  else
    echo "python3"
  fi
}

check_import() {
  local module="$1"
  "$(py)" -c "import ${module}" >/dev/null 2>&1
}

main() {
  cd "${ROOT_DIR}"
  banner

  local errors=0

  echo "Essential tools:"
  if have python3; then pass "Python 3: $(python3 --version 2>/dev/null)"; else fail "python3"; errors=$((errors+1)); fi
  if have openssl; then pass "openssl"; else warn "openssl (recommended for HTTPS exercise)"; fi
  if have curl; then pass "curl"; else warn "curl (recommended for HTTP tests)"; fi
  if have nc; then pass "netcat (nc)"; else warn "netcat (recommended for TCP/UDP demos)"; fi
  echo

  echo "Python environment:"
  if [[ -d .venv ]]; then
    pass ".venv present"
    if check_import requests; then pass "requests"; else fail "requests"; errors=$((errors+1)); fi
    if check_import flask; then pass "flask"; else fail "flask"; errors=$((errors+1)); fi
    if check_import paramiko; then pass "paramiko"; else warn "paramiko (required for SSH client container demo)"; fi
  else
    warn ".venv not found (run: make setup)"
  fi
  echo

  echo "Docker (optional but recommended):"
  if have docker; then
    pass "docker"
    if docker compose version >/dev/null 2>&1; then
      pass "docker compose"
    else
      warn "docker compose (install docker-compose-plugin)"
    fi
    if docker info >/dev/null 2>&1; then
      pass "Docker daemon accessible"
    else
      warn "Docker daemon not accessible (is the service running and are you in the docker group?)"
    fi
  else
    warn "docker not found"
  fi
  echo

  echo "Kit file verification:"
  for f in "Makefile" "README.md" "requirements.txt" "docker/docker-compose.yml" "scripts/run_all.sh" "tests/smoke_test.sh"; do
    if [[ -f "$f" ]]; then pass "$f"; else fail "$f"; errors=$((errors+1)); fi
  done
  echo

  if [[ $errors -eq 0 ]]; then
    echo "${GREEN}[verify] Verification complete.✔${NC}"
    exit 0
  fi

  echo "${RED}[verify] Verification failed (errors: ${errors}).${NC}"
  exit 1
}

main "$@"
