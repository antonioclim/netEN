#!/bin/bash
# =============================================================================
# setup.sh – Environment installation for Week 11
# =============================================================================
# Usage: ./setup.sh [--full]
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

FULL_INSTALL=false
if [[ "$1" == "--full" ]]; then
    FULL_INSTALL=true
fi

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup Week 11 – Computer Networks${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if running as root for some operations
SUDO=""
if [[ $EUID -ne 0 ]]; then
    SUDO="sudo"
fi

# =============================================================================
# 1. Python Dependencies
# =============================================================================
echo -e "${YELLOW}[1/5]${NC} Installing Python dependencies..."

if command -v pip3 &> /dev/null; then
    pip3 install --break-system-packages --quiet dnspython paramiko pyftpdlib 2>/dev/null || \
    pip3 install dnspython paramiko pyftpdlib 2>/dev/null || \
    echo -e "${YELLOW}[!]${NC} Some Python packages failed to install. Continuing..."
else
    echo -e "${RED}[!]${NC} pip3 is not installed. Install it manually."
fi

# =============================================================================
# 2. System Tools (apt-based)
# =============================================================================
echo -e "${YELLOW}[2/5]${NC} Checking system tools..."

MISSING_TOOLS=""
command -v curl &> /dev/null || MISSING_TOOLS="$MISSING_TOOLS curl"
command -v netcat &> /dev/null || command -v nc &> /dev/null || MISSING_TOOLS="$MISSING_TOOLS netcat-openbsd"
command -v tshark &> /dev/null || MISSING_TOOLS="$MISSING_TOOLS tshark"

if [[ -n "$MISSING_TOOLS" ]]; then
    echo -e "${YELLOW}[INFO]${NC} Installing:$MISSING_TOOLS"
    $SUDO apt-get update -qq
    $SUDO apt-get install -y -qq $MISSING_TOOLS 2>/dev/null || \
        echo -e "${YELLOW}[!]${NC} Some tools failed to install. Check manually."
else
    echo -e "${GREEN}[OK]${NC} All basic tools are installed."
fi

# =============================================================================
# 3. Docker (only if --full)
# =============================================================================
if $FULL_INSTALL; then
    echo -e "${YELLOW}[3/5]${NC} Checking Docker..."
    
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}[INFO]${NC} Docker is not installed. Installing..."
        curl -fsSL https://get.docker.com | $SUDO sh
        $SUDO usermod -aG docker $USER
        echo -e "${YELLOW}[!]${NC} Docker installed. Logout/login to apply permissions."
    else
        echo -e "${GREEN}[OK]${NC} Docker is installed."
    fi
    
    # Docker Compose (v2 comes with Docker)
    if docker compose version &> /dev/null; then
        echo -e "${GREEN}[OK]${NC} Docker Compose v2 is available."
    else
        echo -e "${YELLOW}[!]${NC} Docker Compose v2 is not available."
    fi
else
    echo -e "${YELLOW}[3/5]${NC} Docker: skip (run with --full for installation)"
fi

# =============================================================================
# 4. Mininet (only if --full)
# =============================================================================
if $FULL_INSTALL; then
    echo -e "${YELLOW}[4/5]${NC} Checking Mininet..."
    
    if ! command -v mn &> /dev/null; then
        echo -e "${YELLOW}[INFO]${NC} Mininet is not installed. Installing..."
        $SUDO apt-get update -qq
        $SUDO apt-get install -y -qq mininet openvswitch-switch 2>/dev/null || \
            echo -e "${YELLOW}[!]${NC} Mininet failed to install. Check manually."
    else
        echo -e "${GREEN}[OK]${NC} Mininet is installed."
    fi
else
    echo -e "${YELLOW}[4/5]${NC} Mininet: skip (run with --full for installation)"
fi

# =============================================================================
# 5. Final Check
# =============================================================================
echo -e "${YELLOW}[5/5]${NC} Final verification..."

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Run ${YELLOW}make verify${NC} to verify the installation."
echo -e "Run ${YELLOW}make help${NC} to see available commands."
echo ""

# Revolvix&Hypotheticalandrei
