#!/bin/bash
set -euo pipefail
# Verification mediu for Starterkit S9

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "═══ Verification Mediu S9 ═══"
PASS=0
FAIL=0

check() {
    if $1 &>/dev/null; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAIL++))
    fi
}

check "python3 --version" "Python3 installed"
check "python3 -c 'import socket'" "Socket module available"
check "python3 -c 'import struct'" "Struct module available"
check "python3 -c 'import gzip'" "Gzip module available"
check "test -d server-files" "Directory server-files exists"
check "test -f server-files/hello.txt" "File hello.txt exists"
check "test -f python/exercises/ex_9_01_endianness.py" "Exercise 1 exists"
check "test -f python/exercises/ex_9_02_pseudo_ftp.py" "Exercise 2 exists"

echo ""
echo "═══ Result ═══"
echo "Passed: $PASS, Failed: $FAIL"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ Environment is correctly configured!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some verifications failed. Run 'make setup'.${NC}"
    exit 1
fi
