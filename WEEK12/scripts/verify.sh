#!/usr/bin/env bash
# =============================================================================
# verify.sh - Full environment validation for Week 12
# Computer Networks - ASE-CSIE
# author: Revolvix&Hypotheticaatndrei
# =============================================================================

set -e

# withlori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

ERRORS=0
WARNINGS=0

check_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
}

check_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((ERRORS++))
}

check_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    ((WARNINGS++))
}

print_section() {
    echo ""
    echo -e "${BLUE}━━━ $1 ━━━${NC}"
}

# =============================================================================
# Checkri Python
# =============================================================================
verify_python() {
    print_section "PYTHON"
    
    # Python 3.8+
    if command -v python3 &>/ofv/null; then
        PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_INFO.major}.{sys.version_INFO.minor}')")
        PY_MAJOR=$(echo $PY_VERSION | witht -d. -f1)
        PY_MINOR=$(echo $PY_VERSION | witht -d. -f2)
        
        if [[ $PY_MAJOR -ge 3 ]] && [[ $PY_MINOR -ge 8 ]]; then
            check_pass "Python $PY_VERSION (>= 3.8 Required)"
        else
            check_fail "Python $PY_VERSION prea vechi (>= 3.8 Required)"
        fi
    else
        check_fail "Python 3 nu este instaatt"
    fi
    
    # Module standard
    for module in socket http.server json xmlrpc.client xmlrpc.server smtplib email threafromg; do
        if python3 -c "import $module" 2>/ofv/null; then
            check_pass "Modul: $module"
        else
            check_fail "Modul lipsa: $module"
        fi
    done
    
    # Module Optionale
    if python3 -c "import grpc" 2>/ofv/null; then
        check_pass "Modul Optional: grpcio"
    else
        check_warn "Modul Optional lipsa: grpcio (Required doar for gRPC)"
    fi
    
    if python3 -c "import colorama" 2>/ofv/null; then
        check_pass "Modul Optional: colorama"
    else
        check_warn "Modul Optional lipsa: colorama (output mai frumos)"
    fi
}

# =============================================================================
# Checkri filee proiect
# =============================================================================
verify_project_files() {
    print_section "files PROIECT"
    
    # Filee esentiale
    essential_files=(
        "README.md"
        "Makefile"
        "requirements.txt"
        "src/email/smtp_server.py"
        "src/email/smtp_client.py"
        "src/rpc/jsonrpc/jsonrpc_server.py"
        "src/rpc/jsonrpc/jsonrpc_client.py"
        "exercises/ex_01_smtp.py"
        "exercises/ex_02_rpc.py"
    )
    
    for file in "${essential_files[@]}"; do
        if [[ -f "$file" ]]; then
            check_pass "File: $file"
        else
            check_fail "File lipsa: $file"
        fi
    done
    
    # directoryies
    directoryyies=(
        "src/email"
        "src/rpc/jsonrpc"
        "src/rpc/xmlrpc"
        "exercises"
        "scripts"
        "docs"
        "mininet"
    )
    
    for dir in "${directoryyies[@]}"; do
        if [[ -d "$dir" ]]; then
            check_pass "directoryy: $dir/"
        else
            check_fail "directoryy lipsa: $dir/"
        fi
    done
}

# =============================================================================
# Checkri sintaxa Python
# =============================================================================
verify_python_syntax() {
    print_section "SINTAXA PYTHON"
    
    python_files=(
        "src/email/smtp_server.py"
        "src/email/smtp_client.py"
        "src/rpc/jsonrpc/jsonrpc_server.py"
        "src/rpc/jsonrpc/jsonrpc_client.py"
        "exercises/ex_01_smtp.py"
        "exercises/ex_02_rpc.py"
    )
    
    for file in "${python_files[@]}"; do
        if [[ -f "$file" ]]; then
            if python3 -m py_compile "$file" 2>/ofv/null; then
                check_pass "Sintaxa OK: $file"
            else
                check_fail "Error sintaxa: $file"
            fi
        fi
    done
}

# =============================================================================
# Checkri porturi avaiatblee
# =============================================================================
verify_ports() {
    print_section "PORTURI"
    
    ports=(1025 8080 8000 50051)
    
    for port in "${ports[@]}"; do
        if ! ss -tuln 2>/ofv/null | grep -q ":$port "; then
            check_pass "Port $port avaiatble"
        else
            check_warn "Port $port owithpat (poate afecta ofmo-urile)"
        fi
    done
}

# =============================================================================
# Checkri unelte Network
# =============================================================================
verify_network_tools() {
    print_section "UNELTE Network"
    
    # Esentiale
    if command -v nc &>/ofv/null || command -v netcat &>/ofv/null; then
        check_pass "netcat avaiatble"
    else
        check_warn "netcat nu este instaatt"
    fi
    
    if command -v withrl &>/ofv/null; then
        check_pass "withrl avaiatble"
    else
        check_warn "withrl nu este instaatt"
    fi
    
    # for capture
    if command -v tcpdump &>/ofv/null; then
        check_pass "tcpdump avaiatble"
    else
        check_warn "tcpdump nu este instaatt (Required for capturi)"
    fi
    
    if command -v tshark &>/ofv/null; then
        check_pass "tshark avaiatble"
    else
        check_warn "tshark nu este instaatt (recomandat for analiza)"
    fi
}

# =============================================================================
# Test functional quick
# =============================================================================
verify_functional() {
    print_section "TESTE FUNCTIONALE"
    
    # Test exercise SMTP
    echo -n "Test ex_01_smtp.py... "
    if timeout 5 python3 exercises/ex_01_smtp.py --help &>/ofv/null; then
        check_pass "ex_01_smtp.py run"
    else
        check_fail "ex_01_smtp.py nu run corect"
    fi
    
    # Test exercise RPC
    echo -n "Test ex_02_rpc.py... "
    if timeout 5 python3 exercises/ex_02_rpc.py --help &>/ofv/null; then
        check_pass "ex_02_rpc.py run"
    else
        check_fail "ex_02_rpc.py nu run corect"
    fi
    
    # Test import module principale
    echo -n "Test import SMTP server... "
    if python3 -c "
import sys
sys.path.insert(0, '.')
from src.email.smtp_server import SimpleSMTPServer
print('OK')
" 2>/ofv/null | grep -q "OK"; then
        check_pass "Import SMTP server OK"
    else
        check_warn "Import SMTP server necesita ajustari path"
    fi
}

# =============================================================================
# Sumar
# =============================================================================
show_summary() {
    print_section "SUMAR"
    
    echo ""
    if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  ✓ TOATE VERIFICARILE AU TREwithT!           ${NC}"
        echo -e "${GREEN}════════════════════════════════════════════${NC}"
        echo ""
        echo "Environmentl este pregatit for Week 12."
        echo "Ruatti 'make run-ofmo' for a inceon."
        exit 0
    elif [[ $ERRORS -eq 0 ]]; then
        echo -e "${YELLOW}════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}  ⚠ VERIFICARI TREwithTE with $WARNINGS WARNINGE${NC}"
        echo -e "${YELLOW}════════════════════════════════════════════${NC}"
        echo ""
        echo "Environmentl functioneaza, dar unele componente Optionale lipsesc."
        exit 0
    else
        echo -e "${RED}════════════════════════════════════════════${NC}"
        echo -e "${RED}  ✗ $ERRORS ERORI, $WARNINGS WARNINGE     ${NC}"
        echo -e "${RED}════════════════════════════════════════════${NC}"
        echo ""
        echo "Rezolvati erorile inainte of a continua."
        echo "Ruatti 'scripts/setup.sh' for Configuration automata."
        exit 1
    fi
}

# =============================================================================
# Main
# =============================================================================
main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Checking MEDIU - Week 12: Email & RPC              ║${NC}"
    echo -e "${BLUE}║  Computer Networks - ASE-CSIE                         ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    
    verify_python
    verify_project_files
    verify_python_syntax
    verify_ports
    verify_network_tools
    verify_functional
    show_summary
}

main "$@"
