#!/usr/bin/env bash
# =============================================================================
# smoke_test.sh - Generated Artefact Verification for Week 2
# Computer Networks - ASE Bucharest, CSIE
# =============================================================================
# Verifies that run_all.sh has produced valid artefacts.
# Return: 0 = success, 1 = failure
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$PROJECT_ROOT/artifacts"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

check_file() {
    local file="$1"
    local desc="$2"
    local min_size="${3:-0}"
    
    if [[ -f "$file" ]]; then
        local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
        if [[ "$size" -ge "$min_size" ]]; then
            echo -e "${GREEN}[PASS]${NC} $desc ($size bytes)"
            PASS=$((PASS + 1))
        else
            echo -e "${YELLOW}[WARN]${NC} $desc exists but small ($size bytes)"
            WARN=$((WARN + 1))
        fi
    else
        echo -e "${RED}[FAIL]${NC} $desc MISSING"
        FAIL=$((FAIL + 1))
    fi
}

check_content() {
    local file="$1"
    local pattern="$2"
    local desc="$3"
    
    if [[ -f "$file" ]] && grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}[PASS]${NC} $desc"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}[FAIL]${NC} $desc"
        FAIL=$((FAIL + 1))
    fi
}

echo "═══════════════════════════════════════════════════════════════"
echo " WEEK 2 - Smoke Test: Artefact Verification"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check main artefacts
echo "─── Main artefacts ───"
check_file "$ARTIFACTS_DIR/demo.log" "demo.log" 100
check_file "$ARTIFACTS_DIR/demo.pcap" "demo.pcap" 0
check_file "$ARTIFACTS_DIR/validation.txt" "validation.txt" 50

echo ""

# Check log content
echo "─── Log content ───"
if [[ -f "$ARTIFACTS_DIR/demo.log" ]]; then
    check_content "$ARTIFACTS_DIR/demo.log" "TCP" "TCP references in log"
    check_content "$ARTIFACTS_DIR/demo.log" "UDP" "UDP references in log"
    check_content "$ARTIFACTS_DIR/demo.log" "OK" "Successs markers in log"
fi

echo ""

# Check validation content
echo "─── Validation content ───"
if [[ -f "$ARTIFACTS_DIR/validation.txt" ]]; then
    check_content "$ARTIFACTS_DIR/validation.txt" "VALIDATION" "Validation result present"
fi

echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════"
echo " Results: $PASS passed, $FAIL failed, $WARN warnings"
echo "═══════════════════════════════════════════════════════════════"

if [[ $FAIL -gt 0 ]]; then
    echo -e "${RED}SMOKE TEST FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}SMOKE TEST PASSED${NC}"
    exit 0
fi
