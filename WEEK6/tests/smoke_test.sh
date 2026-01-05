#!/bin/bash
# ============================================================================
# smoke_test.sh - Quick automated test for starterkit validation
# Author: Revolvix&Hypotheticalandrei
#
# This script verifies that all components work correctly
# without requiring manual interaction.
# ============================================================================

set -euo pipefail

# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Functions
test_pass() {
    echo -e "  ${GREEN}✓ PASS${NC}: $1"
    ((++TESTS_PASSED))
}

test_fail() {
    echo -e "  ${RED}✗ FAIL${NC}: $1"
    ((++TESTS_FAILED))
}

test_skip() {
    echo -e "  ${YELLOW}○ SKIP${NC}: $1"
    ((++TESTS_SKIPPED))
}

run_test() {
    local name="$1"
    local cmd="$2"
    
    if eval "$cmd" 2>/dev/null; then
        test_pass "$name"
        return 0
    else
        test_fail "$name"
        return 1
    fi
}

# Banner
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Smoke Test - Week 6                       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# Test 1: Structura files
# ============================================================================
echo -e "${BLUE}[TEST 1] Checking file structure...${NC}"

run_test "README.md exists" "[[ -f '$PROJECT_DIR/README.md' ]]"
run_test "Makefile exists" "[[ -f '$PROJECT_DIR/Makefile' ]]"
run_test "topo_nat.py exists" "[[ -f '$PROJECT_DIR/seminar/mininet/topologies/topo_nat.py' ]]"
run_test "topo_sdn.py exists" "[[ -f '$PROJECT_DIR/seminar/mininet/topologies/topo_sdn.py' ]]"
run_test "sdn_policy_controller.py exists" "[[ -f '$PROJECT_DIR/seminar/python/controllers/sdn_policy_controller.py' ]]"
run_test "nat_observer.py exists" "[[ -f '$PROJECT_DIR/seminar/python/apps/nat_observer.py' ]]"
run_test "tcp_echo.py exists" "[[ -f '$PROJECT_DIR/seminar/python/apps/tcp_echo.py' ]]"
run_test "udp_echo.py exists" "[[ -f '$PROJECT_DIR/seminar/python/apps/udp_echo.py' ]]"
run_test "run_all.sh exists" "[[ -f '$PROJECT_DIR/scripts/run_all.sh' ]]"
run_test "python/utils exists" "[[ -d '$PROJECT_DIR/python/utils' ]]"
run_test "artifacts dir exists" "[[ -d '$PROJECT_DIR/artifacts' ]]"

echo ""

# ============================================================================
# Test 2: Syntax Python
# ============================================================================
echo -e "${BLUE}[TEST 2] Checking Python syntax...${NC}"

PYTHON_FILES=(
    "seminar/mininet/topologies/topo_nat.py"
    "seminar/mininet/topologies/topo_sdn.py"
    "seminar/python/controllers/sdn_policy_controller.py"
    "seminar/python/apps/nat_observer.py"
    "seminar/python/apps/tcp_echo.py"
    "seminar/python/apps/udp_echo.py"
)

for file in "${PYTHON_FILES[@]}"; do
    if [[ -f "$PROJECT_DIR/$file" ]]; then
        run_test "Syntax: $(basename $file)" "python3 -m py_compile '$PROJECT_DIR/$file'"
    else
        test_skip "Syntax: $(basename $file) (file missing)"
    fi
done

echo ""

# ============================================================================
# Test 3: Module Python imports
# ============================================================================
echo -e "${BLUE}[TEST 3] Checking Python imports...${NC}"

run_test "Import socket" "python3 -c 'import socket'"
run_test "Import argparse" "python3 -c 'import argparse'"
run_test "Import subprocess" "python3 -c 'import subprocess'"

# Optional modules
if python3 -c "import os_ken" 2>/dev/null; then
    test_pass "Import os_ken"
else
    test_skip "Import os_ken (optional)"
fi

if python3 -c "import scapy" 2>/dev/null; then
    test_pass "Import scapy"
else
    test_skip "Import scapy (optional)"
fi

if python3 -c "from mininet.net import Mininet" 2>/dev/null; then
    test_pass "Import mininet"
else
    test_skip "Import mininet (needs installation)"
fi

echo ""

# ============================================================================
# Test 4: HTML validity (optional - slides may be outline only)
# ============================================================================
echo -e "${BLUE}[TEST 4] Checking HTML/outline files...${NC}"

check_html() {
    local file="$1"
    local name="$2"
    
    if [[ -f "$file" ]]; then
        # Check for basic HTML structure
        if grep -q "<html" "$file" && grep -q "</html>" "$file"; then
            # Check for required meta
            if grep -qiE "revolvix|rezolvix" "$file"; then
                test_pass "$name (structure + branding)"
            else
                test_fail "$name (missing branding)"
            fi
        else
            test_fail "$name (invalid structure)"
        fi
    else
        test_skip "$name (outline only)"
    fi
}

# Check for outline files as a fallback
if [[ -f "$PROJECT_DIR/slides/theory.html" ]]; then
    check_html "$PROJECT_DIR/slides/theory.html" "theory.html"
elif [[ -f "$PROJECT_DIR/slides/curs_slides_outline.txt" ]]; then
    test_pass "curs_slides_outline.txt (outline present)"
else
    test_skip "theory slides (not generated)"
fi

if [[ -f "$PROJECT_DIR/slides/seminar.html" ]]; then
    check_html "$PROJECT_DIR/slides/seminar.html" "seminar.html"
elif [[ -f "$PROJECT_DIR/slides/seminar_slides_outline.txt" ]]; then
    test_pass "seminar_slides_outline.txt (outline present)"
else
    test_skip "seminar slides (not generated)"
fi

if [[ -f "$PROJECT_DIR/slides/lab.html" ]]; then
    check_html "$PROJECT_DIR/slides/lab.html" "lab.html"
elif [[ -f "$PROJECT_DIR/docs/lab.md" ]]; then
    test_pass "docs/lab.md (documentation present)"
else
    test_skip "lab slides (not generated)"
fi

echo ""

# ============================================================================
# Test 5: Scripts executability
# ============================================================================
echo -e "${BLUE}[TEST 5] Checking shell scripts...${NC}"

SHELL_SCRIPTS=(
    "scripts/setup.sh"
    "scripts/cleanup.sh"
    "scripts/run_nat_demo.sh"
    "scripts/run_sdn_demo.sh"
    "scripts/run_all.sh"
    "scripts/verify.sh"
)

for script in "${SHELL_SCRIPTS[@]}"; do
    if [[ -f "$PROJECT_DIR/$script" ]]; then
        # Check if it's a valid shell script
        if head -1 "$PROJECT_DIR/$script" | grep -Eq "^#!.*\bbash\b" ; then
            # Basic syntax check
            if bash -n "$PROJECT_DIR/$script" 2>/dev/null; then
                test_pass "$(basename $script) (syntax OK)"
            else
                test_fail "$(basename $script) (syntax error)"
            fi
        else
            test_fail "$(basename $script) (missing shebang)"
        fi
    else
        test_skip "$(basename $script) (not found)"
    fi
done

echo ""

# ============================================================================
# Test 6: Makefile targets (dry run)
# ============================================================================
echo -e "${BLUE}[TEST 6] Checking Makefile targets...${NC}"

if [[ -f "$PROJECT_DIR/Makefile" ]]; then
    # Check for required targets
    MAKE_TARGETS=("check" "setup" "clean" "nat-demo" "sdn-demo" "controller-start" "controller-stop")
    
    for target in "${MAKE_TARGETS[@]}"; do
        if grep -q "^$target:" "$PROJECT_DIR/Makefile"; then
            test_pass "Makefile target: $target"
        else
            test_fail "Makefile target: $target (missing)"
        fi
    done
else
    test_fail "Makefile not found"
fi

echo ""

# ============================================================================
# Test 7: Mininet quick test (requires root)
# ============================================================================
echo -e "${BLUE}[TEST 7] Mininet test (requires root)...${NC}"

if [[ $EUID -eq 0 ]]; then
    # Quick Mininet test
    if command -v mn &> /dev/null; then
        if timeout 15 mn --test pingall 2>/dev/null | grep -q "0% dropped"; then
            test_pass "Mininet pingall test"
        else
            # Try cleanup first
            mn -c 2>/dev/null || true
            if timeout 15 mn --test pingall 2>/dev/null | grep -q "0% dropped"; then
                test_pass "Mininet pingall test (after cleanup)"
            else
                test_fail "Mininet pingall test"
            fi
        fi
    else
        test_skip "Mininet not installed"
    fi
else
    test_skip "Mininet test (requires root)"
fi

echo ""

# ============================================================================
# Test 8: Artifacts (if run_all.sh a fost executat)
# ============================================================================
echo -e "${BLUE}[TEST 8] Checking artefacts (if present)...${NC}"

if [[ -d "$PROJECT_DIR/artifacts" ]]; then
    if [[ -f "$PROJECT_DIR/artifacts/demo.log" ]]; then
        if [[ -s "$PROJECT_DIR/artifacts/demo.log" ]]; then
            test_pass "artifacts/demo.log (present and non-empty)"
        else
            test_skip "artifacts/demo.log (empty - run scripts/run_all.sh)"
        fi
    else
        test_skip "artifacts/demo.log (not generated - run scripts/run_all.sh)"
    fi
    
    if [[ -f "$PROJECT_DIR/artifacts/demo.pcap" ]]; then
        test_pass "artifacts/demo.pcap (present)"
    else
        test_skip "artifacts/demo.pcap (not generated - run scripts/run_all.sh)"
    fi
    
    if [[ -f "$PROJECT_DIR/artifacts/validation.txt" ]]; then
        if [[ -s "$PROJECT_DIR/artifacts/validation.txt" ]]; then
            test_pass "artifacts/validation.txt (present and non-empty)"
        else
            test_skip "artifacts/validation.txt (empty - run scripts/run_all.sh)"
        fi
    else
        test_skip "artifacts/validation.txt (not generated - run scripts/run_all.sh)"
    fi
else
    test_skip "artifacts directory (not created - run scripts/run_all.sh)"
fi

echo ""

# ============================================================================
# RAPORT FINAL
# ============================================================================
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                    SMOKE TEST REPORT                      ${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}Passed:${NC}  $TESTS_PASSED"
echo -e "  ${RED}Failed:${NC}  $TESTS_FAILED"
echo -e "  ${YELLOW}Skipped:${NC} $TESTS_SKIPPED"
echo ""

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
if [[ $TOTAL -gt 0 ]]; then
    PERCENT=$((TESTS_PASSED * 100 / TOTAL))
else
    PERCENT=0
fi


# ============================================================================
# Artefact checks (must be run after the demo)
# ============================================================================
DEMO_LOG="$PROJECT_DIR/artifacts/demo.log"
VALIDATION_TXT="$PROJECT_DIR/artifacts/validation.txt"

# By default, artefacts are optional: they are generated by sudo make run-all.
# If you want strict post-demo validation, run:
#   AFTER_DEMO=1 make smoke-test

AFTER_DEMO="${AFTER_DEMO:-0}"

if [[ -f "$DEMO_LOG" ]] && [[ -s "$DEMO_LOG" ]]; then
    test_pass "artifacts/demo.log (present and non-empty)"
else
    if [[ "$AFTER_DEMO" == "1" ]]; then
        test_fail "artifacts/demo.log missing or empty (run: sudo make run-all)"
    else
        test_skip "artifacts/demo.log (not generated yet - run: sudo make run-all)"
    fi
fi

if [[ -f "$VALIDATION_TXT" ]] && grep -q "SDN_TEST:" "$VALIDATION_TXT" 2>/dev/null; then
    test_pass "artifacts/validation.txt (present)"
else
    if [[ "$AFTER_DEMO" == "1" ]]; then
        test_fail "artifacts/validation.txt missing (run: sudo make run-all)"
    else
        test_skip "artifacts/validation.txt (not generated yet - run: sudo make run-all)"
    fi
fi

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ ALL TESTS PASSED! Week 6 kit is ready.     ${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${YELLOW}══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  ⚠ $TESTS_FAILED test(s) failed ($PERCENT% passed)     ${NC}"
    echo -e "${YELLOW}══════════════════════════════════════════════════════════${NC}"
    exit 1
fi
