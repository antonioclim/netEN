#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[cleanup] Cleaning Week 7 environment"

# Clean Mininet state
if command -v mn >/dev/null 2>&1; then
  sudo mn -c >/dev/null 2>&1 || true
fi

# Remove Python cache artefacts
find . -name "__pycache__" -type d -print -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -print -delete 2>/dev/null || true

# Stop docker compose if present
if [[ -f "docker/docker-compose.yml" ]] && command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    pushd docker >/dev/null
    if command -v docker-compose >/dev/null 2>&1; then
      docker-compose down -v --remove-orphans >/dev/null 2>&1 || true
    else
      docker compose down -v --remove-orphans >/dev/null 2>&1 || true
    fi
    popd >/dev/null
  fi
fi

echo "[cleanup] Done"
