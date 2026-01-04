#!/usr/bin/env bash
# ============================================================================
# smoke_test.sh — Quick validation tests for Week 3
# ============================================================================
#
# Usage:
#   ./tests/smoke_test.sh            # Run all tests
#   ./tests/smoke_test.sh syntax     # Python syntax checks only
#   ./tests/smoke_test.sh imports    # Import checks only
#   ./tests/smoke_test.sh --verbose  # Verbose output
#
# This script validates:
#   1) Python compilation (py_compile)
#   2) Imports for local modules
#   3) CLI help for runnable scripts
#   4) Presence and minimal content of expected artefacts
#
# Exit codes:
#   0 - success
#   1 - failure
# ============================================================================
set -euo pipefail
# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
SKIPPED=0

# ─── Helper functions ───────────────────────────────────────────────────────

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED+=1))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED+=1))
}

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
    ((SKIPPED+=1))
}

# ─── Configuration ──────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
EXAMPLES_DIR="$ROOT_DIR/python/examples"
TEMPLATES_DIR="$ROOT_DIR/python/templates"
UTILS_DIR="$ROOT_DIR/python/utils"

VERBOSE=false
TEST_TYPE="${1:-all}"

if [[ "${1:-}" == "--verbose" ]] || [[ "${2:-}" == "--verbose" ]]; then
    VERBOSE=true
fi

# ─── Banner ───────────────────────────────────────────────────────────────

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     SMOKE TESTS — Starterkit S3 (Socket Programming)           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

cd "$ROOT_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# TEST 1: Verify syntax Python
# ═══════════════════════════════════════════════════════════════════════════

test_syntax() {
    echo ""
    echo -e "${CYAN}═══ TEST: Python Syntax ═══${NC}"
    echo ""
    
    local files=(
        "$EXAMPLES_DIR"/*.py
        "$TEMPLATES_DIR"/*.py
        "$UTILS_DIR"/*.py
    )
    
    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            filename=$(basename "$file")
            log_test "Verify syntax: $filename"
            
            if python3 -m py_compile "$file" 2>/dev/null; then
                log_pass "$filename - syntax OK"
            else
                log_fail "$filename - syntax errors"
                if $VERBOSE; then
                    python3 -m py_compile "$file" 2>&1 || true
                fi
            fi
        fi
    done
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST 2: Verify imports
# ═══════════════════════════════════════════════════════════════════════════

test_imports() {
    echo ""
    echo -e "${CYAN}═══ TEST: Python Imports ═══${NC}"
    echo ""
    
    # Test import socket (standard library)
    log_test "Import: socket"
    if python3 -c "import socket" 2>/dev/null; then
        log_pass "socket - available"
    else
        log_fail "socket - missing"
    fi
    
    # Test import struct (standard library)
    log_test "Import: struct"
    if python3 -c "import struct" 2>/dev/null; then
        log_pass "struct - available"
    else
        log_fail "struct - missing"
    fi
    
    # Test import threading (standard library)
    log_test "Import: threading"
    if python3 -c "import threading" 2>/dev/null; then
        log_pass "threading - available"
    else
        log_fail "threading - missing"
    fi
    
    # Test import net_utils (local module)
    log_test "Import: net_utils (local module)"
    if PYTHONPATH="$ROOT_DIR/python" python3 -c "from utils.net_utils import *" 2>/dev/null; then
        log_pass "net_utils - available"
    else
        log_fail "net_utils - import error"
        if $VERBOSE; then
            PYTHONPATH="$ROOT_DIR/python" python3 -c "from utils.net_utils import *" 2>&1 || true
        fi
    fi
    
    # Test import scapy (optional)
    log_test "Import: scapy (optional)"
    if python3 -c "from scapy.all import IP, ICMP" 2>/dev/null; then
        log_pass "scapy - available"
    else
        log_skip "scapy - not e instalat (optional)"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST 3: Verify --help
# ═══════════════════════════════════════════════════════════════════════════

test_help() {
    echo ""
    echo -e "${CYAN}═══ TEST: --help Argument ═══${NC}"
    echo ""
    
    local examples=(
        "ex01_udp_broadcast.py"
        "ex02_udp_multicast.py"
        "ex03_tcp_tunnel.py"
        "ex04_echo_server.py"
        "ex05_tcp_multiclient.py"
        "ex06_tcp_framing.py"
        "ex07_udp_session_ack.py"
    )
    
    for example in "${examples[@]}"; do
        if [[ -f "$EXAMPLES_DIR/$example" ]]; then
            log_test "--help: $example"
            
            if timeout 5 python3 "$EXAMPLES_DIR/$example" --help >/dev/null 2>&1; then
                log_pass "$example --help works"
            else
                log_fail "$example --help failed"
            fi
        fi
    done
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST 4: Quick demo broadcast (localhost)
# ═══════════════════════════════════════════════════════════════════════════

test_broadcast_demo() {
    echo ""
    echo -e "${CYAN}═══ TEST: Demo Broadcast (localhost) ═══${NC}"
    echo ""
    
    log_test "Starting receiver on :5007..."
    timeout 5 python3 "$EXAMPLES_DIR/ex01_udp_broadcast.py" recv \
        --port 5007 --count 1 &
    RECV_PID=$!
    sleep 0.5
    
    log_test "Sending broadcast message..."
    if timeout 5 python3 "$EXAMPLES_DIR/ex01_udp_broadcast.py" send \
        --dst 127.255.255.255 --port 5007 --message "SMOKE_TEST" --count 1 2>/dev/null; then
        log_pass "Broadcast send successful"
    else
        log_fail "Broadcast send failed"
    fi
    
    # Asteptam receiver-ul
    wait $RECV_PID 2>/dev/null || true
    
    log_pass "Demo broadcast completed"
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST 5: Quick demo echo server
# ═══════════════════════════════════════════════════════════════════════════

test_echo_demo() {
    echo ""
    echo -e "${CYAN}═══ TEST: Demo Echo Server ═══${NC}"
    echo ""
    
    log_test "Starting echo server on :3333..."
    timeout 10 python3 "$EXAMPLES_DIR/ex04_echo_server.py" \
        --listen 127.0.0.1:3333 &
    SERVER_PID=$!
    sleep 0.5
    
    log_test "Sending test message..."
    RESPONSE=$(echo "HELLO_SMOKE" | nc -w 2 127.0.0.1 3333 2>/dev/null || echo "")
    
    if [[ "$RESPONSE" == "HELLO_SMOKE" ]] || [[ "$RESPONSE" == *"HELLO"* ]]; then
        log_pass "Echo server raspunde corect"
    else
        log_fail "Echo server not responding correctly (received: '$RESPONSE')"
    fi
    
    kill $SERVER_PID 2>/dev/null || true
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST 6: Verify Artifacts (after run_all.sh)
# ═══════════════════════════════════════════════════════════════════════════

test_artifacts() {
    echo ""
    echo -e "${CYAN}═══ TEST: Verify Artifacts ═══${NC}"
    echo ""
    
    local artifacts_dir="$ROOT_DIR/artifacts"
    
    # Verify demo.log
    log_test "Artefact: demo.log"
    if [[ -f "$artifacts_dir/demo.log" ]] && [[ -s "$artifacts_dir/demo.log" ]]; then
        log_pass "demo.log exists and is not empty"
    elif [[ -f "$artifacts_dir/demo.log" ]]; then
        log_skip "demo.log exists but is empty (run scripts/run_all.sh)"
    else
        log_skip "demo.log does not exist (run scripts/run_all.sh)"
    fi
    
    # Verify demo.pcap
    log_test "Artefact: demo.pcap"
    if [[ -f "$artifacts_dir/demo.pcap" ]] && [[ -s "$artifacts_dir/demo.pcap" ]]; then
        log_pass "demo.pcap exists and contains data"
    elif [[ -f "$artifacts_dir/demo.pcap" ]]; then
        log_skip "demo.pcap exists but is empty (may need traffic)"
    else
        log_skip "demo.pcap does not exist (run scripts/run_all.sh)"
    fi
    
    # Verify validation.txt
    log_test "Artefact: validation.txt"
    if [[ -f "$artifacts_dir/validation.txt" ]] && [[ -s "$artifacts_dir/validation.txt" ]]; then
        log_pass "validation.txt exista"
        if grep -q "OVERALL_STATUS=SUCCESS" "$artifacts_dir/validation.txt" 2>/dev/null; then
            log_pass "validation.txt indicates SUCCESS"
        elif grep -q "OVERALL_STATUS" "$artifacts_dir/validation.txt" 2>/dev/null; then
            log_skip "validation.txt indicates partial status"
        fi
    else
        log_skip "validation.txt does not exist (run scripts/run_all.sh)"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# EXECUTIE TESTS
# ═══════════════════════════════════════════════════════════════════════════

case "$TEST_TYPE" in
    syntax)
        test_syntax
        ;;
    imports)
        test_imports
        ;;
    help)
        test_help
        ;;
    demo)
        test_broadcast_demo
        test_echo_demo
        ;;
    artifacts)
        test_artifacts
        ;;
    all)
        test_syntax
        test_imports
        test_help
        test_broadcast_demo
        test_echo_demo
        test_artifacts
        ;;
    *)
        echo "Unknown type: $TEST_TYPE"
        echo "Optiuni: syntax, imports, help, demo, artifacts, all"
        exit 1
        ;;
esac

# ═══════════════════════════════════════════════════════════════════════════
# SUMAR
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${BOLD}TESTS SUMMARY${NC}"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo -e "  ${GREEN}PASSED:${NC}  $PASSED"
echo -e "  ${RED}FAILED:${NC}  $FAILED"
echo -e "  ${YELLOW}SKIPPED:${NC} $SKIPPED"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}=== ALL TESTS PASSED ===${NC}"
    exit 0
else
    echo -e "${RED}═══ SOME TESTS FAILED ═══${NC}"
    exit 1
fi
