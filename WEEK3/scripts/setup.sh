#!/bin/bash
# ============================================================================
# setup.sh — Installing dependencies for Starter Kit S3
# ============================================================================
set -euo pipefail
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${CYAN}[SETUP] Verify sistem...${NC}"

# Detectare distributie
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    DISTRO="unknown"
fi

echo -e "${CYAN}[INFO] Detected distribution: $DISTRO${NC}"

# Installation packets sistem
echo -e "${CYAN}[SETUP] Installation packets sistem...${NC}"
case $DISTRO in
    ubuntu|debian)
        sudo apt-get update -qq
        sudo apt-get install -y -qq python3 python3-pip python3-venv \
            mininet openvswitch-switch \
            tcpdump tshark net-tools netcat-openbsd
        ;;
    *)
        echo -e "${YELLOW}[WARN] Install manually: python3, mininet, tcpdump${NC}"
        ;;
esac

echo -e "${GREEN}[OK] Setup complete!${NC}"
