#!/usr/bin/env bash
# =============================================================================
# verify.sh - Environment verification and functionality for Week 2
# Computer Networks - ASE Bucharest, CSIE
# =============================================================================
# Revolvix&Hypotheticalandrei
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Directorul script-ului
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Contoare
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         verification Mediu - Week 2: Sockets             ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# Utility functions
# =============================================================================

test_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

test_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
}

test_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

section_header() {
    echo ""
    echo -e "${BLUE}── $1 ──${NC}"
}

# =============================================================================
# 1. verification STRUCTURA directories
# =============================================================================

section_header "1. Structura directories"

REQUIRED_DIRS=(
    "seminar/python/exercises"
    "seminar/python/templates"
    "seminar/python/utils"
    "seminar/mininet/topologies"
    "seminar/captures"
    "docs"
    "scripts"
    "logs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        test_pass "directory: $dir"
    else
        test_fail "directory lipsa: $dir"
    fi
done

# =============================================================================
# 2. verification files CRITICE
# =============================================================================

section_header "2. files Critice"

REQUIRED_FILES=(
    "README.md"
    "Makefile"
    "seminar/python/exercises/ex_2_01_tcp.py"
    "seminar/python/exercises/ex_2_02_udp.py"
    "seminar/python/templates/tcp_server_template.py"
    "seminar/python/templates/udp_server_template.py"
    "seminar/mininet/topologies/topo_2_base.py"
    "docs/curs.md"
    "docs/seminar.md"
    "docs/lab.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$PROJECT_ROOT/$file" ]]; then
        test_pass "file: $file"
    else
        test_fail "file lipsa: $file"
    fi
done

# =============================================================================
# 3. verification DEPENDENTE SISTEM
# =============================================================================

section_header "3. Dependente Sistem"

# Python 3
if command -v python3 &> /dev/null; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        test_pass "Python $PY_VER (>= 3.8)"
    else
        test_fail "Python $PY_VER (necesita >= 3.8)"
    fi
else
    test_fail "Python 3 is not installed"
fi

# pip3
if command -v pip3 &> /dev/null; then
    test_pass "pip3 available"
else
    test_fail "pip3 is not installed"
fi

# tshark
if command -v tshark &> /dev/null; then
    test_pass "tshark available"
else
    test_skip "tshark is not installed (optional)"
fi

# tcpdump
if command -v tcpdump &> /dev/null; then
    test_pass "tcpdump available"
else
    test_skip "tcpdump is not installed (optional)"
fi

# netcat
if command -v nc &> /dev/null; then
    test_pass "netcat (nc) available"
else
    test_skip "netcat is not installed (optional)"
fi

# Mininet
if command -v mn &> /dev/null; then
    test_pass "Mininet available"
else
    test_skip "Mininet is not installed (optional for simulari)"
fi

# =============================================================================
# 4. verification MODULE PYTHON
# =============================================================================

section_header "4. Module Python"

PYTHON_MODULES=(
    "socket:Sockets (builtin)"
    "threading:Threading (builtin)"
    "argparse:Argparse (builtin)"
    "json:JSON (builtin)"
    "struct:Struct (builtin)"
    "datetime:Datetime (builtin)"
)

for module_entry in "${PYTHON_MODULES[@]}"; do
    module="${module_entry%%:*}"
    name="${module_entry##*:}"
    if python3 -c "import $module" 2>/dev/null; then
        test_pass "$name"
    else
        test_fail "$name (import $module)"
    fi
done

# Module optionale
OPTIONAL_MODULES=(
    "scapy:Scapy (packet crafting)"
    "pyshark:PyShark (pcap analysis)"
)

for module_entry in "${OPTIONAL_MODULES[@]}"; do
    module="${module_entry%%:*}"
    name="${module_entry##*:}"
    if python3 -c "import $module" 2>/dev/null; then
        test_pass "$name"
    else
        test_skip "$name (optional)"
    fi
done

# =============================================================================
# 5. verification SINTAXA PYTHON
# =============================================================================

section_header "5. Sintaxa Python"

PYTHON_FILES=(
    "seminar/python/exercises/ex_2_01_tcp.py"
    "seminar/python/exercises/ex_2_02_udp.py"
    "seminar/python/templates/tcp_server_template.py"
    "seminar/python/templates/udp_server_template.py"
    "seminar/mininet/topologies/topo_2_base.py"
)

for pyfile in "${PYTHON_FILES[@]}"; do
    filepath="$PROJECT_ROOT/$pyfile"
    if [[ -f "$filepath" ]]; then
        if python3 -m py_compile "$filepath" 2>/dev/null; then
            test_pass "Sintaxa OK: $(basename "$pyfile")"
        else
            test_fail "Error sintaxa: $pyfile"
        fi
    fi
done

# =============================================================================
# 6. verification ports DISPONIBILE
# =============================================================================

section_header "6. ports Disponibile"

DEFAULT_PORTS=(8080 8081 9999 5000)

for port in "${DEFAULT_PORTS[@]}"; do
    if ! ss -tuln 2>/dev/null | grep -q ":$port "; then
        test_pass "port $port available"
    else
        test_fail "port $port OCUPAT"
        # Afiseaza ce process foloseste portul
        if command -v lsof &> /dev/null; then
            PROC=$(lsof -i :$port 2>/dev/null | tail -1 | awk '{print $1}' || echo "necunoscut")
            test_info "  └─ process: $PROC"
        fi
    fi
done

# =============================================================================
# 7. TEST FUNCTIONAL RAPID (SOCKET BASIC)
# =============================================================================

section_header "7. Test Functional Socket"

# Test rapid: cream un socket TCP and verificam ca functioneaza
SOCKET_TEST=$(python3 -c "
import socket
import sys
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 0))  # port aleator
    port = s.getsockname()[1]
    s.listen(1)
    s.close()
    print(f'OK:{port}')
except Exception as e:
    print(f'ERR:{e}')
    sys.exit(1)
" 2>&1)

if [[ "$SOCKET_TEST" == OK:* ]]; then
    test_pass "Socket TCP can be creat and bound"
else
    test_fail "Error creation socket: ${SOCKET_TEST#ERR:}"
fi

# Test UDP
UDP_TEST=$(python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', 0))
    s.close()
    print('OK')
except Exception as e:
    print(f'ERR:{e}')
" 2>&1)

if [[ "$UDP_TEST" == "OK" ]]; then
    test_pass "Socket UDP can be creat and bound"
else
    test_fail "Error creation socket UDP: ${UDP_TEST#ERR:}"
fi

# =============================================================================
# 8. verification PERMISIUNI
# =============================================================================

section_header "8. Permisiuni"

# Verificam if putem scrie in directoriesle necesare
WRITE_DIRS=("logs" "seminar/captures" "pcap")

for dir in "${WRITE_DIRS[@]}"; do
    dirpath="$PROJECT_ROOT/$dir"
    if [[ -d "$dirpath" ]]; then
        if [[ -w "$dirpath" ]]; then
            test_pass "Scriere permisa: $dir/"
        else
            test_fail "Nu pot scrie in: $dir/"
        fi
    fi
done

# verification for capturi of packets (necesita privilegii)
if [[ $EUID -eq 0 ]]; then
    test_pass "runs ca root (poate capture packets)"
else
    test_info "Nu runs ca root"
    test_info "  └─ for capturi of packets: sudo make capture"
    
    # Verificam if user-ul e in grupul wireshark
    if groups 2>/dev/null | grep -qw wireshark; then
        test_pass "User in grupul 'wireshark' (poate capture fara sudo)"
    else
        test_skip "User NU e in grupul 'wireshark'"
        test_info "  └─ Adaugare: sudo usermod -aG wireshark \$USER"
    fi
fi

# =============================================================================
# RAPORT FINAL
# =============================================================================

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}                      RAPORT verification                        ${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))

echo -e "  ${GREEN}Trecute:${NC}  $TESTS_PASSED / $TOTAL_TESTS"
echo -e "  ${RED}Esuate:${NC}   $TESTS_FAILED / $TOTAL_TESTS"
echo -e "  ${YELLOW}Omise:${NC}    $TESTS_SKIPPED / $TOTAL_TESTS"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✓ MEDIUL IS PREGATIT for LABORATOR            ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║    ✗ ATENTIE: $TESTS_FAILED teste esuate - verificati erorile          ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Sugestii:"
    echo "  1. Rulati: make setup"
    echo "  2. Verificati installationa: pip3 install -r requirements.txt"
    echo "  3. for Mininet: sudo apt-get install mininet"
    exit 1
fi
