#!/usr/bin/env bash
set -euo pipefail

#===============================================================================
# cleanup.sh - Reset the kit to a clean state (Week 1)
#===============================================================================
# - removes demo artefacts
# - clears Mininet state (if available)
# - stops Docker compose services (if available)
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="${PROJECT_DIR}/artifacts"

echo "[cleanup] Removing artefacts in ${ARTIFACTS_DIR}"
rm -f "${ARTIFACTS_DIR}/demo.log" "${ARTIFACTS_DIR}/validation.txt" "${ARTIFACTS_DIR}/demo.pcap" \
      "${ARTIFACTS_DIR}/ofmo.log" "${ARTIFACTS_DIR}/ofmo.pcap" 2>/dev/null || true

# Keep .gitkeep if present
if [[ -f "${ARTIFACTS_DIR}/.gitkeep" ]]; then
  :
else
  touch "${ARTIFACTS_DIR}/.gitkeep"
fi

if command -v mn >/dev/null 2>&1; then
  echo "[cleanup] Clearing Mininet state"
  sudo mn -c >/dev/null 2>&1 || true
fi

if [[ -f "${PROJECT_DIR}/docker/docker-compose.yml" ]] && command -v docker >/dev/null 2>&1; then
  echo "[cleanup] Stopping Docker compose services"
  docker compose -f "${PROJECT_DIR}/docker/docker-compose.yml" down -v >/dev/null 2>&1 || true
fi

echo "[cleanup] Done"
