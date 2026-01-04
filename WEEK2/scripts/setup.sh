#!/usr/bin/env bash
# =============================================================================
# setup.sh - Pregatirea mediului for Week 2: Socket Programming
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
NC='\033[0m' # No Color

# Directorul script-ului
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Setup Environment - Week 2: Socket Programming   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# Utility functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        log_success "$1 gasit: $(command -v "$1")"
        return 0
    else
        log_error "$1 NU este installed"
        return 1
    fi
}

# =============================================================================
# verification cerinte sistem
# =============================================================================

log_info "verification cerinte sistem..."
echo ""

MISSING_DEPS=0

# Python 3
if check_command python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "  Versiune Python: $PYTHON_VERSION"
else
    MISSING_DEPS=$((MISSING_DEPS + 1))
fi

# pip3
if check_command pip3; then
    :
else
    MISSING_DEPS=$((MISSING_DEPS + 1))
fi

# Mininet (optional dar recomandat)
if check_command mn; then
    log_success "Mininet gasit"
else
    log_warning "Mininet NU este installed (optional for simulari of network)"
    log_info "  Instalare: sudo apt-get install mininet"
fi

# tshark/Wireshark
if check_command tshark; then
    log_success "tshark gasit"
else
    log_warning "tshark NU este installed (necesar for capturi)"
    log_info "  Instalare: sudo apt-get install tshark"
fi

# tcpdump
if check_command tcpdump; then
    log_success "tcpdump gasit"
else
    log_warning "tcpdump NU este installed"
    log_info "  Instalare: sudo apt-get install tcpdump"
fi

# netcat
if check_command nc; then
    log_success "netcat (nc) gasit"
else
    log_warning "netcat NU este installed"
    log_info "  Instalare: sudo apt-get install netcat-openbsd"
fi

# lsof
if check_command lsof; then
    log_success "lsof gasit"
else
    log_warning "lsof NU este installed"
fi

echo ""

# =============================================================================
# Installing dependencies Python
# =============================================================================

log_info "Installing dependencies Python..."

REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"

if [[ -f "$REQUIREMENTS_FILE" ]]; then
    log_info "Folosesc requirements.txt from project"
    pip3 install --user -q -r "$REQUIREMENTS_FILE" 2>/dev/null || {
        log_warning "Unele packets pot necesita sudo: pip3 install -r requirements.txt"
    }
    log_success "Dependente Python installede"
else
    log_warning "requirements.txt nu a fost gasit, instalez packets esentiale"
    pip3 install --user -q scapy pyshark 2>/dev/null || true
fi

echo ""

# =============================================================================
# creation structura directories
# =============================================================================

log_info "verification/creation structura directories..."

DIRS=(
    "$PROJECT_ROOT/seminar/captures"
    "$PROJECT_ROOT/logs"
    "$PROJECT_ROOT/pcap"
)

for dir in "${DIRS[@]}"; do
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir"
        log_success "Creat: $dir"
    else
        log_info "Exista: $dir"
    fi
done

echo ""

# =============================================================================
# configuration sysctl (if este root)
# =============================================================================

if [[ $EUID -eq 0 ]]; then
    log_info "Aplicare configurari sysctl for network..."
    
    SYSCTL_CONF="$PROJECT_ROOT/configs/sysctl.conf"
    if [[ -f "$SYSCTL_CONF" ]]; then
        sysctl -p "$SYSCTL_CONF" 2>/dev/null || log_warning "Unele setari sysctl nu au putut fi aplicate"
        log_success "Configurari sysctl aplicate"
    fi
else
    log_warning "Nu runs ca root - configurarile sysctl vor fi omise"
    log_info "  for configurari of network avansate, rulati: sudo $0"
fi

echo ""

# =============================================================================
# verification ports availablee
# =============================================================================

log_info "verification ports folosite in demo-uri..."

PORTS_TO_CHECK=(8080 8081 9999 5000)
PORTS_IN_USE=0

for port in "${PORTS_TO_CHECK[@]}"; do
    if ss -tuln 2>/dev/null | grep -q ":$port "; then
        log_warning "port $port este OCUPAT"
        log_info "  process: $(lsof -i :$port 2>/dev/null | tail -1 || echo 'necunoscut')"
        PORTS_IN_USE=$((PORTS_IN_USE + 1))
    else
        log_success "port $port available"
    fi
done

echo ""

# =============================================================================
# Raport final
# =============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                        RAPORT SETUP                           ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ $MISSING_DEPS -eq 0 ]]; then
    log_success "Toate dependentele critice sunt installede"
else
    log_error "$MISSING_DEPS dependente critice lipsesc"
fi

if [[ $PORTS_IN_USE -gt 0 ]]; then
    log_warning "$PORTS_IN_USE ports necesare sunt ocupate"
else
    log_success "Toate porturile necesare sunt availablee"
fi

echo ""
echo -e "${GREEN}Setup completed!${NC}"
echo ""
echo "Pasi urmatori:"
echo "  1. make verify        - verifies configuratia"
echo "  2. make demo-tcp      - runs demo TCP"
echo "  3. make demo-udp      - runs demo UDP"
echo "  4. make mininet-cli   - Deschide CLI Mininet"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
