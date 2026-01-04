#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ART_DIR="$ROOT_DIR/artifacts"
mkdir -p "$ART_DIR"

MODE="${1:-all}"

echo "[demo] Week 7 demo starting (mode: $MODE)"
echo "[demo] Writing artefacts to: $ART_DIR"

# Always clean Mininet state first to avoid conflicts
if command -v mn >/dev/null 2>&1; then
  sudo mn -c >/dev/null 2>&1 || true
fi

if [[ "$MODE" != "--docker-only" ]]; then
  echo "[demo] Running Mininet demo"
  if command -v python3 >/dev/null 2>&1; then
    sudo -E python3 mininet/scenarios/demo_week7.py \
      --artifacts "$ART_DIR" \
      --pcap "$ART_DIR/demo.pcap" \
      --log "$ART_DIR/demo.log" \
      --validation "$ART_DIR/validation.txt"
  else
    echo "[demo] python3 not found. Cannot run Mininet demo."
    exit 1
  fi
fi

# Optional analysis with tshark
if [[ -f "$ART_DIR/demo.pcap" ]] && command -v tshark >/dev/null 2>&1; then
  echo "[demo] Generating tshark summary"
  python3 python/utils/traffic_analysis.py --pcap "$ART_DIR/demo.pcap" --out "$ART_DIR/tshark_summary.txt" || true
fi

# Optional Docker demo
if [[ "$MODE" == "--docker-only" || "$MODE" == "all" ]]; then
  if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
      echo "[demo] Running optional Docker Compose demo"
      pushd docker >/dev/null
      if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up --build --abort-on-container-exit --remove-orphans || true
      else
        docker compose up --build --abort-on-container-exit --remove-orphans || true
      fi
      popd >/dev/null
    else
      echo "[demo] Docker available but not running. Skipping Docker demo."
    fi
  else
    echo "[demo] Docker not installed. Skipping Docker demo."
  fi
fi

echo "[demo] Done"
