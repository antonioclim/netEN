#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[setup] Week 7 setup starting in: $ROOT_DIR"

# Create a virtual environment if you prefer isolation.
# This kit also works without venv, but venv is recommended on student machines.
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv >/dev/null 2>&1 || true
fi

# Install Python requirements (optional components use these).
if command -v pip >/dev/null 2>&1; then
  python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
  python3 -m pip install -r requirements.txt >/dev/null 2>&1 || true
fi

# OS packages (Debian or Ubuntu)
if command -v apt-get >/dev/null 2>&1; then
  echo "[setup] Installing OS packages with apt-get (sudo may ask for a password)"
  sudo apt-get update -y
  sudo apt-get install -y \
    python3 python3-pip python3-venv \
    iproute2 iputils-ping net-tools \
    tcpdump tshark \
    iptables \
    mininet openvswitch-switch
else
  echo "[setup] apt-get not found. Install manually: python3, pip, mininet, openvswitch, tcpdump, tshark, iptables"
fi

echo "[setup] Done"
