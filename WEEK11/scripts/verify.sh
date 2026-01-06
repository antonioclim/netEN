#!/bin/bash
# =============================================================================
# verify.sh – Environment verification for Week 11
# =============================================================================
# Usage: ./verify.sh [--smoke]
# =============================================================================

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

SMOKE_TEST=false
if [[ "$1" == "--smoke" ]]; then
    SMOKE_TEST=true
fi

ERRORS=0

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Environment Verification – Week 11${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# =============================================================================
# Check function
# =============================================================================
check() {
    local name="$1"
    local cmd="$2"
    
    if eval "$cmd" &> /dev/null; then
        echo -e "${GREEN}[✓]${NC} $name"
        return 0
    else
        echo -e "${RED}[✗]${NC} $name"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

check_version() {
    local name="$1"
    local cmd="$2"
    
    local version
    version=$(eval "$cmd" 2>/dev/null | head -1)
    if [[ -n "$version" ]]; then
        echo -e "${GREEN}[✓]${NC} $name: $version"
        return 0
    else
        echo -e "${RED}[✗]${NC} $name: not installed"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# =============================================================================
# Core Tools
# =============================================================================
echo -e "${YELLOW}─── Basic tools ───${NC}"

check_version "Python" "python3 --version"
check "pip3" "command -v pip3"
check "curl" "command -v curl"
check "netcat" "command -v nc || command -v netcat"

# =============================================================================
# Network Tools
# =============================================================================
echo ""
echo -e "${YELLOW}─── Network tools ───${NC}"

check "tshark/Wireshark" "command -v tshark"
check "tcpdump" "command -v tcpdump"

# =============================================================================
# Docker
# =============================================================================
echo ""
echo -e "${YELLOW}─── Docker ───${NC}"

if check "Docker" "command -v docker"; then
    check "Docker running" "docker info"
    check_version "Docker Compose" "docker compose version"
fi

# =============================================================================
# Mininet
# =============================================================================
echo ""
echo -e "${YELLOW}─── Mininet ───${NC}"

check "Mininet" "command -v mn"
check "Open vSwitch" "command -v ovs-vsctl"

# =============================================================================
# Python Packages
# =============================================================================
echo ""
echo -e "${YELLOW}─── Python packages ───${NC}"

check "dnspython" "python3 -c 'import dns.resolver'"
check "paramiko" "python3 -c 'import paramiko'"

# =============================================================================
# Smoke Tests (optional)
# =============================================================================
if $SMOKE_TEST; then
    echo ""
    echo -e "${YELLOW}─── Smoke Tests ───${NC}"
    
    # Test Python backend script exists and is valid
    if [[ -f "python/exercises/ex_11_01_backend.py" ]]; then
        check "ex_11_01_backend.py syntax" "python3 -m py_compile python/exercises/ex_11_01_backend.py"
    fi
    
    if [[ -f "python/exercises/ex_11_02_loadbalancer.py" ]]; then
        check "ex_11_02_loadbalancer.py syntax" "python3 -m py_compile python/exercises/ex_11_02_loadbalancer.py"
    fi
    
    if [[ -f "python/exercises/ex_11_03_dns_client.py" ]]; then
        check "ex_11_03_dns_client.py syntax" "python3 -m py_compile python/exercises/ex_11_03_dns_client.py"
    fi
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}  All checks passed! ✓${NC}"
else
    echo -e "${RED}  $ERRORS checks failed.${NC}"
    echo -e "${YELLOW}  Run 'make setup' to install missing components.${NC}"
fi

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

exit $ERRORS

# Revolvix&Hypotheticalandrei
