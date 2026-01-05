#!/bin/bash
set -euo pipefail
# Environment verification for Starterkit S9 (Week 9)

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "═══ Environment Verification (Week 9) ═══"
PASSED=0
FAILED=0

check() {
    # Usage: check "<command>" "<description>"
    if eval "$1" &>/dev/null; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED+=1))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED+=1))
    fi
}

check "python3 --version" "Python 3 is available"
check "python3 -c 'import socket'" "Python: socket module available"
check "python3 -c 'import struct'" "Python: struct module available"
check "python3 -c 'import gzip'" "Python: gzip module available"

check "test -d server-files" "Directory server-files/ exists (run: make setup)"
check "test -f server-files/hello.txt" "File server-files/hello.txt exists (run: make setup)"
check "test -f python/exercises/ex_9_01_endianness.py" "Exercise 9.01 exists"
check "test -f python/exercises/ex_9_02_pseudo_ftp.py" "Exercise 9.02 exists"

echo ""
echo "═══ Summary ═══"
echo "Passed: $PASSED"
echo "Failed: $FAILED"

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}✓ Environment is correctly configured.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Run 'make setup' and try again.${NC}"
    exit 1
fi
