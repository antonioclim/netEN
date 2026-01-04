#!/usr/bin/env bash
#===============================================================================
# verify.sh — Verificare completa a mediului and demo-urilor
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
# Verificari sistem
#-------------------------------------------------------------------------------

verify_system() {
    log_section "Verificari sistem"
    
    # Python
    if command -v python3 &> /dev/null; then
        local ver=$(python3 --version 2>&1 | awk '{print $2}')
        log_pass "Python $ver instalat"
    else
        log_fail "Python3 nu este instalat"
    fi
    
    # Mininet
    if command -v mn &> /dev/null; then
        log_pass "Mininet available"
    else
        log_warn "Mininet nu este available (necesita VM Linux)"
    fi
    
    # Open vSwitch
    if systemctl is-active --quiet openvswitch-switch 2>/dev/null || \
       pgrep -x ovs-vswitchd > /dev/null 2>&1; then
        log_pass "Open vSwitch activ"
    else
        log_warn "Open vSwitch nu este activ"
    fi
    
    # tcpdump
    if command -v tcpdump &> /dev/null; then
        log_pass "tcpdump available"
    else
        log_warn "tcpdump nu este instalat"
    fi
    
    # tshark
    if command -v tshark &> /dev/null; then
        log_pass "tshark available"
    else
        log_warn "tshark nu este instalat"
    fi
    
    # Module Python
    for module in ipaddress argparse json dataclasses math; do
        if python3 -c "import $module" 2>/dev/null; then
            log_pass "Modul Python '$module' available"
        else
            log_fail "Modul Python '$module' lipseste"
        fi
    done
}

#-------------------------------------------------------------------------------
# Verificari structura proiect
#-------------------------------------------------------------------------------

verify_structure() {
    log_section "Verificari structura proiect"
    
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
            log_pass "Fisier prezent: $file"
        else
            log_fail "Fisier lipsa: $file"
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
            log_pass "Director prezent: $dir"
        else
            log_warn "Director lipsa: $dir"
        fi
    done
}

#-------------------------------------------------------------------------------
# Verificari demo-uri Python
#-------------------------------------------------------------------------------

verify_python_demos() {
    log_section "Verificari demo-uri Python"
    
    cd "$PROJECT_ROOT/python/exercises"
    
    # Test CIDR analyze
    log_info "Testare ex_5_01_cidr_flsm.py analyze..."
    if python3 ex_5_01_cidr_flsm.py analyze 192.168.1.1/24 > /dev/null 2>&1; then
        log_pass "CIDR analyze functional"
    else
        log_fail "CIDR analyze esuat"
    fi
    
    # Test FLSM
    log_info "Testare ex_5_01_cidr_flsm.py flsm..."
    if python3 ex_5_01_cidr_flsm.py flsm 10.0.0.0/8 4 > /dev/null 2>&1; then
        log_pass "FLSM functional"
    else
        log_fail "FLSM esuat"
    fi
    
    # Test VLSM
    log_info "Testare ex_5_02_vlsm_ipv6.py vlsm..."
    if python3 ex_5_02_vlsm_ipv6.py vlsm 192.168.0.0/24 100 50 20 > /dev/null 2>&1; then
        log_pass "VLSM functional"
    else
        log_fail "VLSM esuat"
    fi
    
    # Test IPv6
    log_info "Testare ex_5_02_vlsm_ipv6.py ipv6..."
    if python3 ex_5_02_vlsm_ipv6.py ipv6 2001:db8::1 > /dev/null 2>&1; then
        log_pass "IPv6 compress functional"
    else
        log_fail "IPv6 compress esuat"
    fi
    
    # Test Quiz (syntax only)
    log_info "Testare ex_5_03_quiz_generator.py..."
    if python3 -c "import ex_5_03_quiz_generator" 2>/dev/null; then
        log_pass "Quiz generator importabil"
    else
        log_fail "Quiz generator are erori de sintaxa"
    fi
    
    cd - > /dev/null
}

#-------------------------------------------------------------------------------
# Verificari Mininet (daca available)
#-------------------------------------------------------------------------------

verify_mininet() {
    log_section "Verificari Mininet"
    
    if ! command -v mn &> /dev/null; then
        log_warn "Mininet nu este available, skip verificari"
        return
    fi
    
    # Verificare sintaxa topologii
    log_info "Verificare sintaxa topologii..."
    
    if python3 -m py_compile "$PROJECT_ROOT/mininet/topologies/topo_5_base.py" 2>/dev/null; then
        log_pass "topo_5_base.py sintaxa valida"
    else
        log_fail "topo_5_base.py erori sintaxa"
    fi
    
    if python3 -m py_compile "$PROJECT_ROOT/mininet/topologies/topo_5_extended.py" 2>/dev/null; then
        log_pass "topo_5_extended.py sintaxa valida"
    else
        log_fail "topo_5_extended.py erori sintaxa"
    fi
    
    # Test functional (necesita sudo)
    if sudo -n true 2>/dev/null; then
        log_info "Testare topologie de baza (necesita ~10 secunde)..."
        
        cd "$PROJECT_ROOT/mininet/topologies"
        if sudo timeout 30 python3 topo_5_base.py --test > /dev/null 2>&1; then
            log_pass "topo_5_base.py test conectivitate reusit"
        else
            log_warn "topo_5_base.py test conectivitate esuat or timeout"
        fi
        cd - > /dev/null
        
        # Cleanup dupa test
        sudo mn -c > /dev/null 2>&1 || true
    else
        log_warn "Sudo necesita parola, skip test Mininet functional"
    fi
}

#-------------------------------------------------------------------------------
# Sumar
#-------------------------------------------------------------------------------

print_summary() {
    log_section "SUMAR VERIFICARI"
    
    echo -e "${GREEN}Trecute:${NC}  $PASS"
    echo -e "${RED}Esuate:${NC}   $FAIL"
    echo -e "${YELLOW}Avertismente:${NC} $WARN"
    echo ""
    
    if [[ $FAIL -eq 0 ]]; then
        echo -e "${GREEN}✓ Mediul este pregatit for Week 5!${NC}"
        return 0
    else
        echo -e "${RED}✗ $FAIL verificari esuate. Consultati README.md for remediere.${NC}"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║            Verificare Mediu — Week 5                    ║"
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
            echo "Optiuni:"
            echo "  --quick  Doar verificari sistem"
            echo "  --full   Verificare completa (implicit)"
            echo "  --demos  Doar demo-uri Python and Mininet"
            exit 0
            ;;
        *)
            echo "Optiune necunoscuta: $mode"
            exit 1
            ;;
    esac
    
    print_summary
}

main "$@"
