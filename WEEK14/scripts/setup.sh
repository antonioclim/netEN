#!/bin/bash
# setup.sh — Installs dependencies for Starterkit W14
# Run: sudo bash scripts/setup.sh

set -e

echo "=============================================="
echo "  Setup Starterkit Week 14"
echo "=============================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "[!] This script must be run with sudo"
    exit 1
fi

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    DISTRO="unknown"
fi

echo "[*] Distribution detected: $DISTRO"

# Update package list
echo "[*] Updating package list..."
apt-get update -qq

# Install base packages
echo "[*] Installing base packages..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    net-tools \
    iproute2 \
    iputils-ping \
    netcat-openbsd \
    tcpdump \
    > /dev/null

# Install tshark (Wireshark CLI)
echo "[*] Installing tshark..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    tshark \
    > /dev/null 2>&1 || echo "[!] tshark installation may have issues (non-critical)"

# Install Mininet
echo "[*] Installing Mininet..."
if ! command -v mn &> /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        mininet \
        openvswitch-switch \
        > /dev/null
    
    # Start OVS
    systemctl enable openvswitch-switch 2>/dev/null || true
    systemctl start openvswitch-switch 2>/dev/null || true
else
    echo "    Mininet already installed."
fi

# Install apache2-utils (for ab - Apache Benchmark)
echo "[*] Installing apache2-utils (optional)..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    apache2-utils \
    > /dev/null 2>&1 || echo "    apache2-utils skipped (non-critical)"

# Verify installations
echo ""
echo "[*] Verifying installations..."

check_cmd() {
    if command -v "$1" &> /dev/null; then
        echo "    ✓ $1"
    else
        echo "    ✗ $1 (missing)"
    fi
}

check_cmd python3
check_cmd pip3
check_cmd mn
check_cmd ovs-vsctl
check_cmd tcpdump
check_cmd tshark
check_cmd curl
check_cmd nc

# Verify OVS
echo ""
echo "[*] Verifying Open vSwitch..."
if systemctl is-active --quiet openvswitch-switch; then
    echo "    ✓ openvswitch-switch active"
else
    echo "    ! openvswitch-switch inactive, attempting to start..."
    systemctl start openvswitch-switch 2>/dev/null || true
fi

echo ""
echo "=============================================="
echo "  Setup completed!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. bash tests/smoke_test.sh   # verify environment"
echo "  2. make run-demo              # run the demo"
echo ""
