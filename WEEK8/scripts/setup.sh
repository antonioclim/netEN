#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# setup.sh - Environment configuration for Week 8
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║  Setup - Computer Networks - Week 8                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# System detection
if [ -f /etc/debian_version ]; then
    PKG_MANAGER="apt"
    INSTALL_CMD="sudo apt-get install -y"
elif [ -f /etc/redhat-release ]; then
    PKG_MANAGER="yum"
    INSTALL_CMD="sudo yum install -y"
else
    echo "[WARN] Unknown system. Install manually: curl, netcat, tcpdump"
    PKG_MANAGER="unknown"
fi

echo "[INFO] Checking Python 3..."
if command -v python3 &> /dev/null; then
    echo "  ✓ Python 3 found: $(python3 --version)"
else
    echo "  ✗ Python 3 missing!"
    if [ "$PKG_MANAGER" = "apt" ]; then
        echo "[INFO] Installing Python 3..."
        $INSTALL_CMD python3 python3-pip
    fi
fi

echo ""
echo "[INFO] Checking curl..."
if command -v curl &> /dev/null; then
    echo "  ✓ curl found"
else
    echo "  ✗ curl missing"
    if [ "$PKG_MANAGER" = "apt" ]; then
        $INSTALL_CMD curl
    fi
fi

echo ""
echo "[INFO] Checking netcat..."
if command -v nc &> /dev/null; then
    echo "  ✓ netcat found"
else
    echo "  ✗ netcat missing"
    if [ "$PKG_MANAGER" = "apt" ]; then
        $INSTALL_CMD netcat-openbsd
    fi
fi

echo ""
echo "[INFO] Checking tcpdump (optional)..."
if command -v tcpdump &> /dev/null; then
    echo "  ✓ tcpdump found"
else
    echo "  ○ tcpdump not found (optional, for captures)"
fi

# Create artifacts directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
mkdir -p "$PROJECT_DIR/artifacts"

echo ""
echo "[INFO] Setup completee!"
echo "  Run 'make verify' to check the environment"
