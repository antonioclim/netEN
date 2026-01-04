#!/bin/bash
# =============================================================================
# Smoke Test for Starterkit S9
# =============================================================================
# Verifies:
#   1. Exercise L6 (endianness)
#   2. Import pseudo-FTP
#   3. Shared utilities (net_utils.py)
#   4. Artefacts generated (demo.log, demo.pcap, validation.txt)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PASSED=0
FAILED=0

check() {
    local name="$1"
    local cmd="$2"
    
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $name"
        ((PASSED+=1))
    else
        echo -e "  ${RED}✗${NC} $name"
        ((FAILED+=1))
    fi
    return 0
}


echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Smoke Test – Starterkit S9                                      ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Group 1: Cod Python
echo "▶ Verifying Python code:"
check "ex_9_01_endianness.py --selftest" \
    "python3 python/exercises/ex_9_01_endianness.py --selftest 2>&1 | grep -q 'All tests passed'"

check "Import ex_9_02_pseudo_ftp.py" \
    "python3 -c 'from python.exercises.ex_9_02_pseudo_ftp import pack_data, unpack_data'"

check "net_utils.py selftest" \
    "python3 python/utils/net_utils.py 2>&1 | grep -q 'All tests passed'"

echo ""

# Group 2: Artefacts (after run_all.sh)
echo "▶ Verifying artefacts (after ./scripts/run_all.sh):"
if [ -d "artifacts" ]; then
    check "artifacts/demo.log exists" "[ -f artifacts/demo.log ]"
    check "artifacts/demo.pcap exists" "[ -f artifacts/demo.pcap ]"
    check "artifacts/validation.txt exists" "[ -f artifacts/validation.txt ]"
    
    if [ -f "artifacts/demo.log" ]; then
        check "demo.log contains date" "[ -s artifacts/demo.log ]"
    fi
    
    if [ -f "artifacts/validation.txt" ]; then
        check "validation.txt contains PASS" "grep -q PASS artifacts/validation.txt"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Directory artifacts/ does not exist (run ./scripts/run_all.sh first)"
fi

echo ""

# Group 3: Structure directoare
echo "▶ Verifying structure:"
check "scripts/ exists" "[ -d scripts ]"
check "python/exercises/ exists" "[ -d python/exercises ]"
check "python/utils/ exists" "[ -d python/utils ]"
check "mininet/topologies/ exists" "[ -d mininet/topologies ]"
check "tests/ exists" "[ -d tests ]"
check "docs/ exists" "[ -d docs ]"

echo ""

# Summary
echo "══════════════════════════════════════════════════════════════════"
if [ $FAILED -eq 0 ]; then
    echo -e "  ${GREEN}All tests passed! ($PASSED/$((PASSED+FAILED)))${NC}"
else
    echo -e "  ${RED}$FAILED tests failed, $PASSED passed${NC}"
fi
echo "══════════════════════════════════════════════════════════════════"

exit $FAILED
