#!/usr/bin/env bash
#===============================================================================
# verify.sh — Complete verification of environment and demos
#===============================================================================
# usage: ./scripts/verify.sh [--quick|--full|--demos]
#===============================================================================

set -euo pipefail

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Contoare
PASS=0
FAIL=0
WARN=0

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_pass() { echo -e "${GREEN}[PASS]${NC} $1"; ((PASS++)); }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; ((FAIL++)); }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; ((WARN++)); }
log_section() { echo -e "\n${CYAN}=== $1 ===${NC}\n"; }

#-------------------------------------------------------------------------------
# System checks
#-------------------------------------------------------------------------------

verify_system() {
    log_section "System checks"
    
    # Python
    if command -v python3 &> /dev/null; then
        local ver=$(python3 --version 2>&1 | awk '{print $2}')
        log_pass "Python $ver installed"
    else
        log_fail "Python3 is not installed"
    fi
    
    # Mininet
    if command -v mn &> /dev/null; then
        log_pass "Mininet available"
    else
        log_warn "Mininet is not available (requires Linux VM)"
    fi
    
    # Open vSwitch
    if systemctl is-activee --quiet openvswitch-switch 2>/dev/null || \
       pgrep -x ovs-vswitchd > /dev/null 2>&1; then
        log_pass "Open vSwitch active"
    else
        log_warn "Open vSwitch is not activee"
    fi
    
    # tcpdump
    if command -v tcpdump &> /dev/null; then
        log_pass "tcpdump available"
    else
        log_warn "tcpdump is not installed"
    fi
    
    # tshark
    if command -v tshark &> /dev/null; then
        log_pass "tshark available"
    else
        log_warn "tshark is not installed"
    fi
    
    # Module Python
    for module in ipaddress argparse json dataclasses math; do
        if python3 -c "import $module" 2>/dev/null; then
            log_pass "Python module '$module' available"
        else
            log_fail "Python module '$module' is missing"
        fi
    done
}

#-------------------------------------------------------------------------------
# Project structure checks
#-------------------------------------------------------------------------------

verify_structure() {
    log_section "Project structure checks"
    
    local required_files=(
        "Makefile"
        "README.md"
        "python/utils/net_utils.py"
        "python/exercises/ex_5_01_cidr_flsm.py"
        "python/exercises/ex_5_02_vlsm_ipv6.py"
        "python/exercises/ex_5_03_quiz_generator.py"
        "mininet/topologies/topo_5_base.py"
        "mininet/topologies/topo_5_extended.py"
        "docs/curs/curs.md"
        "docs/seminar/seminar.md"
        "docs/lab/lab.md"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$file" ]]; then
            log_pass "File present: $file"
        else
            log_fail "File missing: $file"
        fi
    done
    
    local required_dirs=(
        "python/apps"
        "scripts"
        "docker"
        "pcap"
        "solutions"
        "tests"
        "assets/html"
        "assets/images"
        "slides"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$PROJECT_ROOT/$dir" ]]; then
            log_pass "Directory present: $dir"
        else
            log_warn "Directory missing: $dir"
        fi
    done
}

#-------------------------------------------------------------------------------
# Python demos checks
#-------------------------------------------------------------------------------

verify_python_demos() {
    log_section "Python demos checks"
    
    cd "$PROJECT_ROOT/python/exercises"
    
    # Test CIDR analyze
    log_info "Testing ex_5_01_cidr_flsm.py analyze..."
    if python3 ex_5_01_cidr_flsm.py analyze 192.168.1.1/24 > /dev/null 2>&1; then
        log_pass "CIDR analyze working"
    else
        log_fail "CIDR analyze failed"
    fi
    
    # Test FLSM
    log_info "Testing ex_5_01_cidr_flsm.py flsm..."
    if python3 ex_5_01_cidr_flsm.py flsm 10.0.0.0/8 4 > /dev/null 2>&1; then
        log_pass "FLSM working"
    else
        log_fail "FLSM failed"
    fi
    
    # Test VLSM
    log_info "Testing ex_5_02_vlsm_ipv6.py vlsm..."
    if python3 ex_5_02_vlsm_ipv6.py vlsm 192.168.0.0/24 100 50 20 > /dev/null 2>&1; then
        log_pass "VLSM working"
    else
        log_fail "VLSM failed"
    fi
    
    # Test IPv6
    log_info "Testing ex_5_02_vlsm_ipv6.py ipv6..."
    if python3 ex_5_02_vlsm_ipv6.py ipv6 2001:db8::1 > /dev/null 2>&1; then
        log_pass "IPv6 compress working"
    else
        log_fail "IPv6 compress failed"
    fi
    
    # Test Quiz (syntax only)
    log_info "Testing ex_5_03_quiz_generator.py..."
    if python3 -c "import ex_5_03_quiz_generator" 2>/dev/null; then
        log_pass "Quiz generator importable"
    else
        log_fail "Quiz generator are syntax errors"
    fi
    
    cd - > /dev/null
}

#-------------------------------------------------------------------------------
# Mininet checks (daca available)
#-------------------------------------------------------------------------------

verify_mininet() {
    log_section "Mininet checks"
    
    if ! command -v mn &> /dev/null; then
        log_warn "Mininet is not available, skipping checks"
        return
    fi
    
    # Checking topology syntax
    log_info "Checking topology syntax..."
    
    if python3 -m py_compile "$PROJECT_ROOT/mininet/topologies/topo_5_base.py" 2>/dev/null; then
        log_pass "topo_5_base.py valid syntax"
    else
        log_fail "topo_5_base.py syntax errors"
    fi
    
    if python3 -m py_compile "$PROJECT_ROOT/mininet/topologies/topo_5_extended.py" 2>/dev/null; then
        log_pass "topo_5_extended.py valid syntax"
    else
        log_fail "topo_5_extended.py syntax errors"
    fi
    
    # Test working (necesita sudo)
    if sudo -n true 2>/dev/null; then
        log_info "Testing topologie de baza (requires ~10 seconds)..."
        
        cd "$PROJECT_ROOT/mininet/topologies"
        if sudo timeout 30 python3 topo_5_base.py --test > /dev/null 2>&1; then
            log_pass "topo_5_base.py connectivity test passed"
        else
            log_warn "topo_5_base.py test conectivitate failed or timeout"
        fi
        cd - > /dev/null
        
        # Cleanup after test
        sudo mn -c > /dev/null 2>&1 || true
    else
        log_warn "Sudo requires password, skipping test Mininet working"
    fi
}

#-------------------------------------------------------------------------------
# Sumar
#-------------------------------------------------------------------------------

print_summary() {
    log_section "VERIFICATION SUMMARY"
    
    echo -e "${GREEN}Passed:${NC}  $PASS"
    echo -e "${RED}Failed:${NC}   $FAIL"
    echo -e "${YELLOW}Warnings:${NC} $WARN"
    echo ""
    
    if [[ $FAIL -eq 0 ]]; then
        echo -e "${GREEN}✓ Environment is ready for Week 5!${NC}"
        return 0
    else
        echo -e "${RED}✗ $FAIL checks failed. Consult README.md for remediation.${NC}"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║            Environment Verification — Week 5                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    
    local mode="${1:---full}"
    
    case "$mode" in
        --quick)
            verify_system
            ;;
        --full)
            verify_system
            verify_structure
            verify_python_demos
            verify_mininet
            ;;
        --demos)
            verify_python_demos
            verify_mininet
            ;;
        --help|-h)
            echo "usage: $0 [--quick|--full|--demos]"
            echo ""
            echo "Options:"
            echo "  --quick  System checks only"
            echo "  --full   Complete verification (default)"
            echo "  --demos  Python and Mininet demos only"
            exit 0
            ;;
        *)
            echo "Unknown option: $mode"
            exit 1
            ;;
    esac
    
    print_summary
}

main "$@"
