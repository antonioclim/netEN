#!/usr/bin/env bash
# ==============================================================================
# setup.sh - Environment setup for Week 4 starter kit
# ==============================================================================
# Goals
# - Validate prerequisites for a CLI-only minimal VM
# - Create local folders used by the demo
# - Optionally create a local virtual environment and install Python requirements
#
# Usage
#   ./scripts/setup.sh           # create .venv and install requirements (safe, reversible)
#   ./scripts/setup.sh --check   # checks only, no changes
#
# Week 4 defaults
# - Ports: 5400 (TEXT), 5401 (BINARY), 5402 (UDP)
# - Mininet subnet (if used): 10.0.4.0/24
# ==============================================================================

set -euo pipefail

CHECK_ONLY=false
if [ "${1:-}" = "--check" ]; then
  CHECK_ONLY=true
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "============================================================"
echo "Week 4 setup"
echo "============================================================"
echo "Ports: TEXT=5400, BINARY=5401, UDP=5402"
echo "Mininet subnet (if used): 10.0.4.0/24"
echo

# ------------------------------------------------------------------------------
# 1) Basic tools
# ------------------------------------------------------------------------------
missing=0

need_cmd() {
  local c="$1"
  if ! command -v "$c" >/dev/null 2>&1; then
    echo "  [MISSING] $c"
    missing=$((missing+1))
  else
    echo "  [OK] $c -> $(command -v "$c")"
  fi
}

echo "[1/4] Checking required tools"
need_cmd python3
need_cmd bash

echo
echo "[2/4] Checking optional tools (demo still works without capture)"
need_cmd tcpdump || true
need_cmd tshark || true
need_cmd docker || true
need_cmd mininet || true
need_cmd mn || true

echo
python3 - <<'PY'
import sys
print(f"[OK] Python version: {sys.version.split()[0]}")
PY

# ------------------------------------------------------------------------------
# 2) Create folders used by scripts
# ------------------------------------------------------------------------------
echo
echo "[3/4] Ensuring local folders exist"
mkdir -p artifacts logs
echo "  [OK] artifacts/ and logs/"

# ------------------------------------------------------------------------------
# 3) Python environment (reversible)
# ------------------------------------------------------------------------------
echo
echo "[4/4] Python dependencies"
if [ "$CHECK_ONLY" = true ]; then
  echo "  [CHECK] Skipping virtual environment creation and pip install"
else
  if [ ! -d ".venv" ]; then
    echo "  Creating .venv (local, reversible)"
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python3 -m pip install --upgrade pip >/dev/null
  if [ -f requirements.txt ]; then
    python3 -m pip install -r requirements.txt >/dev/null
    echo "  [OK] Installed requirements.txt into .venv"
  else
    echo "  [WARN] requirements.txt not found, nothing to install"
  fi
fi

echo
if [ "$missing" -gt 0 ]; then
  echo "[WARN] Missing $missing tool(s). See the list above."
  echo "       The core Python demo should still run, but some features may be skipped."
else
  echo "[OK] Setup checks complete."
fi
