#!/usr/bin/env bash
#==============================================================================
# smoke_test.sh – Verifytion artefacts demo for Week 10
#
# Verify existence and content minimum al:
#   - artifacts/demo.log
#   - artifacts/demo.pcap
#   - artifacts/validation.txt
#
# Exit codes:
#   0 - Toate verificarile trewithte
#   1 - Una or more verificari failed
#
# Computer Networks, ASE Bucharest 2025-2026
# Revolvix and HypotheticalAndrei | Licence MIT
#==============================================================================
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$ROOT_DIR/artifacts"

# Colours
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

#------------------------------------------------------------------------------
# Functii test
#------------------------------------------------------------------------------
test_pass() {
    ((TESTS_TOTAL++))
    ((TESTS_PASSED++))
    echo -e "${GREEN}[PASS]${NC} $1"
}

test_fail() {
    ((TESTS_TOTAL++))
    ((TESTS_FAILED++))
    echo -e "${RED}[FAIL]${NC} $1"
}

test_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

#------------------------------------------------------------------------------
# Verifytion existenta filee
#------------------------------------------------------------------------------
check_file_exists() {
    local file="$1"
    local name="$2"
    
    if [ -f "$file" ]; then
        local size
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
        test_pass "$name exista ($size bytes)"
        return 0
    else
        test_fail "$name lipseste"
        return 1
    fi
}

#------------------------------------------------------------------------------
# Verifytion demo.log
#------------------------------------------------------------------------------
check_demo_log() {
    local log_file="$ARTIFACTS_DIR/demo.log"
    
    echo ""
    echo "═══════════════════════════════════════════"
    echo "  Verifyre: demo.log"
    echo "═══════════════════════════════════════════"
    
    if ! check_file_exists "$log_file" "demo.log"; then
        return 1
    fi
    
    # Verifytion continut minimum
    local line_count
    line_count=$(wc -l < "$log_file" 2>/dev/null || echo "0")
    
    if [ "$line_count" -gt 10 ]; then
        test_pass "demo.log are continut substantial ($line_count linii)"
    else
        test_fail "demo.log prea scurt ($line_count linii)"
    fi
    
    # Verifytion marcaje importante
    if grep -qi "DNS" "$log_file" 2>/dev/null; then
        test_pass "demo.log contine teste DNS"
    else
        test_fail "demo.log nu contine teste DNS"
    fi
    
    if grep -qi "SSH" "$log_file" 2>/dev/null; then
        test_pass "demo.log contine teste SSH"
    else
        test_fail "demo.log nu contine teste SSH"
    fi
    
    if grep -qi "FTP" "$log_file" 2>/dev/null; then
        test_pass "demo.log contine teste FTP"
    else
        test_fail "demo.log nu contine teste FTP"
    fi
}

#------------------------------------------------------------------------------
# Verifytion demo.pcap
#------------------------------------------------------------------------------
check_demo_pcap() {
    local pcap_file="$ARTIFACTS_DIR/demo.pcap"
    
    echo ""
    echo "═══════════════════════════════════════════"
    echo "  Verifyre: demo.pcap"
    echo "═══════════════════════════════════════════"
    
    if ! check_file_exists "$pcap_file" "demo.pcap"; then
        return 1
    fi
    
    # Verifytion dimensiune
    local size
    size=$(stat -f%z "$pcap_file" 2>/dev/null || stat -c%s "$pcap_file" 2>/dev/null || echo "0")
    
    if [ "$size" -gt 24 ]; then  # Header PCAP minim = 24 bytes
        test_pass "demo.pcap are date capturate ($size bytes)"
        
        # Optional: verification tshark/tcpdump
        if command -v tshark &>/dev/null; then
            local packet_count
            packet_count=$(tshark -r "$pcap_file" -T fields -e frame.number 2>/dev/null | wc -l || echo "0")
            if [ "$packet_count" -gt 0 ]; then
                test_pass "demo.pcap contine $packet_count packete (verificat cu tshark)"
            else
                test_warn "demo.pcap pare gol (0 packete citite)"
            fi
        fi
    else
        test_warn "demo.pcap este gol sau doar header ($size bytes)"
        test_warn "Captura poate lipsi daca tshark/tcpdump nu este disponibil"
    fi
}

#------------------------------------------------------------------------------
# Verifytion validation.txt
#------------------------------------------------------------------------------
check_validation() {
    local val_file="$ARTIFACTS_DIR/validation.txt"
    
    echo ""
    echo "═══════════════════════════════════════════"
    echo "  Verifyre: validation.txt"
    echo "═══════════════════════════════════════════"
    
    if ! check_file_exists "$val_file" "validation.txt"; then
        return 1
    fi
    
    # Verifytion format
    local has_results=false
    
    if grep -q ":PASS" "$val_file" 2>/dev/null; then
        has_results=true
        local pass_count
        pass_count=$(grep -c ":PASS" "$val_file" || echo "0")
        test_pass "validation.txt contine $pass_count teste PASS"
    fi
    
    if grep -q ":FAIL" "$val_file" 2>/dev/null; then
        has_results=true
        local fail_count
        fail_count=$(grep -c ":FAIL" "$val_file" || echo "0")
        if [ "$fail_count" -gt 0 ]; then
            test_warn "validation.txt contine $fail_count teste FAIL"
        fi
    fi
    
    if ! $has_results; then
        test_fail "validation.txt nu contine rezultate de test"
    fi
    
    # Verifytion sumar
    if grep -q "TOTAL_TESTS=" "$val_file" 2>/dev/null; then
        test_pass "validation.txt contine sumar"
        
        # Afisare sumar
        echo ""
        echo "  Sumar din validation.txt:"
        grep -E "^(TOTAL_TESTS|PASSED|FAILED)=" "$val_file" | while read -r line; do
            echo "    $line"
        done
    else
        test_warn "validation.txt nu contine sumar final"
    fi
}

#------------------------------------------------------------------------------
# Verifytion structura directoare
#------------------------------------------------------------------------------
check_structure() {
    echo ""
    echo "═══════════════════════════════════════════"
    echo "  Verifyre: Structura directoare"
    echo "═══════════════════════════════════════════"
    
    local required_dirs=(
        "scripts"
        "docker"
        "python"
        "artifacts"
        "docs"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$ROOT_DIR/$dir" ]; then
            test_pass "Director $dir/ exista"
        else
            test_fail "Director $dir/ lipseste"
        fi
    done
    
    # Verifytion filee esentiale
    local required_files=(
        "scripts/setup.sh"
        "scripts/run_all.sh"
        "scripts/cleanup.sh"
        "docker/docker-compose.yml"
        "README.md"
        "Makefile"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$ROOT_DIR/$file" ]; then
            test_pass "Fisier $file exista"
        else
            test_fail "Fisier $file lipseste"
        fi
    done
}

#------------------------------------------------------------------------------
# Verifytion Docker (optional)
#------------------------------------------------------------------------------
check_docker_services() {
    echo ""
    echo "═══════════════════════════════════════════"
    echo "  Verifyre: Services Docker (optional)"
    echo "═══════════════════════════════════════════"
    
    if ! command -v docker &>/dev/null; then
        test_warn "Docker nu este instalat - verificare omisa"
        return
    fi
    
    cd "$ROOT_DIR/docker"
    
    local running
    running=$(docker compose ps --format json 2>/dev/null | grep -c '"running"' || echo "0")
    
    if [ "$running" -gt 0 ]; then
        test_pass "Services Docker active: $running"
        
        # Verifytion services specifice
        for service in web dns-server ssh-server ftp-server; do
            if docker compose ps "$service" 2>/dev/null | grep -q "running"; then
                test_pass "Serviciu $service ruleaza"
            else
                test_warn "Serviciu $service nu ruleaza"
            fi
        done
    else
        test_warn "Niciun serviciu Docker activ"
    fi
    
    cd "$ROOT_DIR"
}

#------------------------------------------------------------------------------
# Sumar final
#------------------------------------------------------------------------------
print_summary() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                           SUMAR SMOKE TEST                                    ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "  Total teste:  $TESTS_TOTAL"
    echo -e "  ${GREEN}Trecute:${NC}      $TESTS_PASSED"
    echo -e "  ${RED}Esuate:${NC}       $TESTS_FAILED"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  ✓ SMOKE TEST TRECUT - TOATE VERIFICARILE OK                                  ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
        return 0
    else
        echo -e "${RED}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║  ✗ SMOKE TEST ESUAT - $TESTS_FAILED verificari esuate${NC}"
        echo -e "${RED}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
        return 1
    fi
}

#------------------------------------------------------------------------------
# Usage
#------------------------------------------------------------------------------
usage() {
    cat << EOF
Utilizare: $0 [optiune]

Verify artefactsle generate de scripts/run_all.sh

Optiuni:
  --artifacts-only   Verify doar artefactsle (demo.log, demo.pcap, validation.txt)
  --structure-only   Verify doar structura directoarelor
  --full             Verifyre completa (implicit)
  --docker           Include verificare services Docker
  -h, --help         Afiseaza acest mesaj

Exemple:
  $0                 # Verifyre completa
  $0 --artifacts-only
  $0 --docker
EOF
}

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
    echo "║  SMOKE TEST - SAPTAMANA 10 - SERVICII DE RETEA                                ║"
    echo "║  Verifyre artefacts si structura                                            ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
    
    local check_artifacts=true
    local check_struct=true
    local check_docker=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --artifacts-only)
                check_struct=false
                ;;
            --structure-only)
                check_artifacts=false
                ;;
            --docker)
                check_docker=true
                ;;
            --full)
                check_artifacts=true
                check_struct=true
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "Optiune necunoscuta: $1"
                usage
                exit 1
                ;;
        esac
        shift
    done
    
    # Run checks
    if $check_struct; then
        check_structure
    fi
    
    if $check_artifacts; then
        check_demo_log
        check_demo_pcap
        check_validation
    fi
    
    if $check_docker; then
        check_docker_services
    fi
    
    print_summary
}

main "$@"
