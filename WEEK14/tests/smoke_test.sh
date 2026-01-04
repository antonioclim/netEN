#!/bin/bash
# smoke_test.sh — Quick environment tests for Starterkit W14
# Run: bash tests/smoke_test.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo "  Smoke Tests W14"
echo "=============================================="
echo ""

PASS=0
FAIL=0

# Function for test
test_check() {
    local name=$1
    local cmd=$2
    
    if eval "$cmd" > /dev/null 2>&1; then
        echo "  ✓ $name"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $name"
        FAIL=$((FAIL + 1))
    fi
}

# File structure tests
echo "[*] Checking file structure..."
test_check "README.md exists" "[ -f '$ROOT_DIR/README.md' ]"
test_check "Makefile exists" "[ -f '$ROOT_DIR/Makefile' ]"
test_check "requirements.txt exists" "[ -f '$ROOT_DIR/requirements.txt' ]"
test_check "setup.sh exists" "[ -f '$ROOT_DIR/scripts/setup.sh' ]"
test_check "run_all.sh exists" "[ -f '$ROOT_DIR/scripts/run_all.sh' ]"
test_check "cleanup.sh exists" "[ -f '$ROOT_DIR/scripts/cleanup.sh' ]"
test_check "topo_14_recap.py exists" "[ -f '$ROOT_DIR/mininet/topologies/topo_14_recap.py' ]"
test_check "backend_server.py exists" "[ -f '$ROOT_DIR/python/apps/backend_server.py' ]"
test_check "lb_proxy.py exists" "[ -f '$ROOT_DIR/python/apps/lb_proxy.py' ]"
test_check "run_demo.py exists" "[ -f '$ROOT_DIR/python/apps/run_demo.py' ]"
test_check "ex_14_03.py exists" "[ -f '$ROOT_DIR/python/exercises/ex_14_03.py' ]"
test_check "scenario_14_tasks.md exists" "[ -f '$ROOT_DIR/mininet/scenarios/scenario_14_tasks.md' ]"
test_check "sysctl.conf exists" "[ -f '$ROOT_DIR/configs/sysctl.conf' ]"

# Python tests
echo ""
echo "[*] Checking Python..."
test_check "Python 3 available" "command -v python3"
test_check "Python >= 3.8" "python3 -c 'import sys; exit(0 if sys.version_info >= (3,8) else 1)'"

# System dependency tests
echo ""
echo "[*] Checking system dependencies..."
test_check "mininet (mn) available" "command -v mn"
test_check "ovs-vsctl available" "command -v ovs-vsctl"
test_check "tcpdump available" "command -v tcpdump"
test_check "ip available" "command -v ip"
test_check "ss available" "command -v ss"

# Optional tests
echo ""
echo "[*] Checking optional dependencies..."
if command -v tshark > /dev/null 2>&1; then
    echo "  ✓ tshark available"
    PASS=$((PASS + 1))
else
    echo "  ○ tshark not available (optional)"
fi

if command -v curl > /dev/null 2>&1; then
    echo "  ✓ curl available"
    PASS=$((PASS + 1))
else
    echo "  ○ curl not available (optional)"
fi

# Python syntax test
echo ""
echo "[*] Checking Python syntax..."
for pyfile in "$ROOT_DIR"/python/apps/*.py; do
    if [ -f "$pyfile" ]; then
        name=$(basename "$pyfile")
        test_check "Syntax: $name" "python3 -m py_compile '$pyfile'"
    fi
done

# Test Mininet import (requires root for some functions)
echo ""
echo "[*] Checking Mininet import..."
if python3 -c "from mininet.topo import Topo; print('OK')" 2>/dev/null; then
    echo "  ✓ Mininet import OK"
    PASS=$((PASS + 1))
else
    echo "  ✗ Mininet import FAIL"
    FAIL=$((FAIL + 1))
fi

# Summary
echo ""
echo "=============================================="
echo "  Result: $PASS passed, $FAIL failed"
echo "=============================================="

if [ $FAIL -eq 0 ]; then
    echo ""
    echo "All tests passed! ✓"
    echo ""
    echo "Next steps:"
    echo "  make run-demo    # run the complete demo"
    echo ""
    exit 0
else
    echo ""
    echo "Some tests failed. Run 'sudo bash scripts/setup.sh'"
    echo ""
    exit 1
fi
