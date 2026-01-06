#!/usr/bin/env bash
set -euo pipefail

# Week 10 - Setup helper
# Creates a local Python virtual environment and installs the required packages.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- Colours (console only) -------------------------------------------------
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

log() { printf "%b\n" "$*"; }
info() { log "${BLUE}[INFO]${NC} $*"; }
ok() { log "${GREEN}[OK]${NC} $*"; }
warn() { log "${YELLOW}[WARN]${NC} $*"; }
err() { log "${RED}[ERROR]${NC} $*"; }

header() {
  log "${BLUE}=================================================================${NC}"
  log "${BLUE}  Setup - Computer Networks - Week 10${NC}"
  log "${BLUE}  HTTP, HTTPS, REST and Network Services (DNS, SSH and FTP)${NC}"
  log "${BLUE}=================================================================${NC}"
}

need_cmd() {
  local c="$1"
  if ! command -v "$c" >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

main() {
  cd "$ROOT_DIR"
  header

  info "Project root: $ROOT_DIR"

  # --- Basic tools ----------------------------------------------------------
  info "Checking essential commands..."
  local missing=0
  for c in python3 pip3 openssl curl; do
    if need_cmd "$c"; then
      ok "$c found"
    else
      err "$c not found"
      missing=$((missing+1))
    fi
  done

  if (( missing > 0 )); then
    err "Missing essential tools. Install them and re-run setup."
    err "On Ubuntu you can usually run: sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv openssl curl"
    exit 1
  fi

  # --- Virtual environment --------------------------------------------------
  info "Setting up Python virtual environment (.venv)..."
  if [[ ! -d .venv ]]; then
    python3 -m venv .venv
    ok "Created .venv"
  else
    ok ".venv already exists"
  fi

  # Activate for this script
  # shellcheck disable=SC1091
  source .venv/bin/activate

  python -m pip install --upgrade pip >/dev/null
  info "Installing Python dependencies (requirements.txt)..."
  python -m pip install -r requirements.txt >/dev/null
  ok "Python dependencies installed"

  # --- Directory structure --------------------------------------------------
  info "Creating working directories (if missing)..."
  mkdir -p artifacts logs output pcap certs
  ok "Directories ready: artifacts/, logs/, output/, pcap/"

  # --- TLS certificate for the HTTPS exercise -------------------------------
  info "Preparing a self-signed certificate for the HTTPS exercise..."
  if [[ ! -s certs/server.crt || ! -s certs/server.key ]]; then
    python python/exercises/ex_10_01_https.py generate-cert --out-dir certs >/dev/null
    ok "Certificate created: certs/server.crt and certs/server.key"
  else
    ok "Certificate already present (certs/)"
  fi

  log ""
  ok "Setup complete."
  log "Next steps:"
  log "  1) make verify"
  log "  2) make run-all"
  log "  3) make smoke-test"
}

main "$@"
