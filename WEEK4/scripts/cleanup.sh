#!/usr/bin/env bash
# ==============================================================================
# cleanup.sh - Reset Week 4 starter kit to a clean state
# ==============================================================================
# Usage
#   ./scripts/cleanup.sh          # stop demo processes and remove artefacts
#   ./scripts/cleanup.sh --full   # also remove .venv and docker containers
# ==============================================================================

set -euo pipefail

FULL=false
if [ "${1:-}" = "--full" ] || [ "${1:-}" = "-f" ]; then
  FULL=true
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "============================================================"
echo "Week 4 cleanup"
echo "============================================================"

echo "[1/5] Stopping Python demo processes (best effort)"
pkill -f "text_proto_server" 2>/dev/null || true
pkill -f "binary_proto_server" 2>/dev/null || true
pkill -f "udp_sensor_server" 2>/dev/null || true
pkill -f "scenario_.*_demo.py" 2>/dev/null || true

echo "[2/5] Stopping tcpdump if running (best effort)"
pkill -f "tcpdump -i lo" 2>/dev/null || true

echo "[3/5] Mininet cleanup (if available)"
if command -v mn >/dev/null 2>&1; then
  sudo -n mn -c >/dev/null 2>&1 || mn -c >/dev/null 2>&1 || true
  echo "  [OK] mn -c executed (or not required)"
else
  echo "  [SKIP] mn not installed"
fi

echo "[4/5] Docker cleanup (if compose is present)"
if [ -f docker/docker-compose.yml ] && command -v docker >/dev/null 2>&1; then
  # Use the plugin form if available, otherwise fall back to docker-compose
  if docker compose version >/dev/null 2>&1; then
    docker compose -f docker/docker-compose.yml down -v >/dev/null 2>&1 || true
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose -f docker/docker-compose.yml down -v >/dev/null 2>&1 || true
  fi
  echo "  [OK] Docker compose down (best effort)"
else
  echo "  [SKIP] Docker or compose file not present"
fi

echo "[5/5] Removing generated artefacts"
rm -f artifacts/demo.log artifacts/demo.pcap artifacts/validation.txt 2>/dev/null || true

if [ "$FULL" = true ]; then
  rm -rf .venv 2>/dev/null || true
  echo "  [OK] Removed .venv (full cleanup)"
fi

echo "[OK] Cleanup complete."
