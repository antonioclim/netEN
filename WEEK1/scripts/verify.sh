#!/usr/bin/env bash
set -euo pipefail

#===============================================================================
# verify.sh - Static checks for the kit (Week 1)
#===============================================================================
# Usage:
#   bash scripts/verify.sh
#   bash scripts/verify.sh --verbose
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERBOSE=0

if [[ "${1:-}" == "--verbose" ]]; then
  VERBOSE=1
fi

echo "[verify] Python compile check"
python3 -m py_compile $(find "${PROJECT_DIR}/python" "${PROJECT_DIR}/mininet" -name "*.py" -type f) >/dev/null

echo "[verify] Bash syntax check"
bash -n "${PROJECT_DIR}/scripts/setup.sh"
bash -n "${PROJECT_DIR}/scripts/run_all.sh"
bash -n "${PROJECT_DIR}/scripts/cleanup.sh"
bash -n "${PROJECT_DIR}/tests/smoke_test.sh"

if [[ -f "${PROJECT_DIR}/docker/docker-compose.yml" ]] && command -v docker >/dev/null 2>&1; then
  echo "[verify] Docker compose config check"
  docker compose -f "${PROJECT_DIR}/docker/docker-compose.yml" config -q
fi

if [[ "${VERBOSE}" -eq 1 ]]; then
  echo "[verify] Done"
fi
