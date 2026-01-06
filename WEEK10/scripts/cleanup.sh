#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<EOF
Usage: ./scripts/cleanup.sh [--reset]

Options:
  --reset   Also remove the Python virtual environment (.venv) and generated TLS material

This script removes generated artefacts and stops the Docker stack if it is running.
EOF
}

RESET=0
if [[ $# -gt 0 ]]; then
  case "$1" in
    --reset) RESET=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
fi

echo "Cleaning generated files..."
rm -rf "${ROOT_DIR}/artifacts" "${ROOT_DIR}/pcap" "${ROOT_DIR}/logs" "${ROOT_DIR}/output" || true
mkdir -p "${ROOT_DIR}/artifacts" "${ROOT_DIR}/pcap" "${ROOT_DIR}/logs" "${ROOT_DIR}/output"

echo "Stopping Docker services (if running)..."
if command -v docker >/dev/null 2>&1 && command -v docker compose >/dev/null 2>&1; then
  (cd "${ROOT_DIR}/docker" && docker compose down -v >/dev/null 2>&1) || true
fi

if [[ ${RESET} -eq 1 ]]; then
  echo "Removing Python virtual environment and TLS certificates..."
  rm -rf "${ROOT_DIR}/.venv" || true
  rm -rf "${ROOT_DIR}/certs" || true
fi

echo "Cleanup complete."
