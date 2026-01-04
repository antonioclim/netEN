#!/usr/bin/env bash
set -euo pipefail

#===============================================================================
# setup.sh - Prerequisite checker and optional installer (Week 1)
#===============================================================================
# This script targets Debian or Ubuntu minimal VMs.
#
# Usage:
#   bash scripts/setup.sh
#   bash scripts/setup.sh --minimal
#
# Notes:
# - If you want automatic installation, run with sudo.
# - The demo can run without Mininet and without packet capture.
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

MINIMAL=0
if [[ "${1:-}" == "--minimal" ]]; then
  MINIMAL=1
fi

have() { command -v "$1" >/dev/null 2>&1; }

echo "[setup] Project: ${PROJECT_DIR}"

missing=()

# Core tools
for cmd in python3 pip3 ip ss ping; do
  if ! have "$cmd"; then
    missing+=("$cmd")
  fi
done

# Optional tools
if ! have nc; then missing+=("nc"); fi
if ! have tcpdump; then missing+=("tcpdump"); fi

# Mininet (optional)
if [[ "$MINIMAL" -eq 0 ]]; then
  if ! have mn; then
    missing+=("mn")
  fi
fi

# Docker (optional)
if [[ -f "${PROJECT_DIR}/docker/docker-compose.yml" ]]; then
  if ! have docker; then
    echo "[setup] Docker not found (optional). Docker demo will be unavailable."
  fi
fi

if [[ "${#missing[@]}" -eq 0 ]]; then
  echo "[setup] All required commands are available."
  exit 0
fi

echo "[setup] Missing commands: ${missing[*]}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "[setup] Not running as root. Install missing packages manually or rerun with sudo."
  exit 0
fi

if ! have apt-get; then
  echo "[setup] apt-get not found. Automatic installation is supported only on Debian or Ubuntu."
  exit 0
fi

echo "[setup] Installing missing packages via apt-get..."

apt-get update -y

pkgs=()
for cmd in "${missing[@]}"; do
  case "$cmd" in
    python3) pkgs+=("python3") ;;
    pip3) pkgs+=("python3-pip" "python3-venv") ;;
    ip|ss) pkgs+=("iproute2") ;;
    ping) pkgs+=("iputils-ping") ;;
    nc) pkgs+=("netcat-openbsd") ;;
    tcpdump) pkgs+=("tcpdump") ;;
    mn) pkgs+=("mininet") ;;
    *) ;;
  esac
done

# De-duplicate packages
uniq_pkgs=()
for p in "${pkgs[@]}"; do
  if [[ ! " ${uniq_pkgs[*]} " =~ " ${p} " ]]; then
    uniq_pkgs+=("$p")
  fi
done

if [[ "${#uniq_pkgs[@]}" -gt 0 ]]; then
  apt-get install -y "${uniq_pkgs[@]}"
fi

echo "[setup] Done."
