#!/bin/bash
CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
ERRORS=0

check() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}[OK]${NC} $1 instalat: $(command -v $1)"
    else
        echo -e "${RED}[FAIL]${NC} $1 not este instalat"
        ((ERRORS++))
    fi
}

echo -e "${CYAN}[VERIFY] Verify dependencies...${NC}"
check python3
check tcpdump
check nc

# Verify Python version
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${GREEN}[OK]${NC} Python version: $PY_VER"

# Verify Mininet
if sudo mn --test pingall &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Mininet works"
else
    echo -e "${RED}[WARN]${NC} Mininet poate necesita configurare"
fi

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}[OK] All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}[FAIL] $ERRORS probleme detectate.${NC}"
    exit 1
fi
