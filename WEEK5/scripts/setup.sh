#!/usr/bin/env bash
set -euo pipefail
#===============================================================================
# setup.sh — Environment Configuration for Week 5
#===============================================================================
# Usage: ./scripts/setup.sh [--full|--minimal|--check]
#
# Options:
#   --full     Install all dependencies (requires sudo)
#   --minimal  Only verify and configure (no installations)
#   --check    Only check environment status
#===============================================================================

set -euo pipefail

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Colour

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

#-------------------------------------------------------------------------------
# Utility Functions
#-------------------------------------------------------------------------------

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERR]${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        log_success "$1 available"
        return 0
    else
        log_error "$1 missing"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# Checks
#-------------------------------------------------------------------------------

check_environment() {
    log_info "Checking working environment..."
    echo ""
    
    local errors=0
    
    # Python
    if check_command python3; then
        local py_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if [[ $(echo "$py_version >= 3.10" | bc -l 2>/dev/null || echo 0) -eq 1 ]] || \
           [[ "$py_version" > "3.9" ]]; then
            log_success "Python $py_version (>= 3.10)"
        else
            log_warning "Python $py_version (recommended >= 3.10)"
        fi
    else
        ((errors++))
    fi
    
    # Mininet
    if check_command mn; then
        log_success "Mininet installed"
    else
        log_warning "Mininet not installed (requires VM or container)"
        ((errors++))
    fi
    
    # Open vSwitch
    if systemctl is-active --quiet openvswitch-switch 2>/dev/null; then
        log_success "Open vSwitch active"
    elif pgrep -x ovs-vswitchd > /dev/null 2>&1; then
        log_success "Open vSwitch running"
    else
        log_warning "Open vSwitch not active"
    fi
    
    # tcpdump
    check_command tcpdump || ((errors++))
    
    # ip command
    check_command ip || ((errors++))
    
    # Python module ipaddress
    if python3 -c "import ipaddress" 2>/dev/null; then
        log_success "Python ipaddress module available"
    else
        log_error "ipaddress module missing"
        ((errors++))
    fi
    
    # Check sudo permissions
    if sudo -n true 2>/dev/null; then
        log_success "Sudo permissions available"
    else
        log_warning "Sudo requires password (normal for most systems)"
    fi
    
    echo ""
    if [[ $errors -eq 0 ]]; then
        log_success "All checks passed!"
        return 0
    else
        log_error "$errors checks failed"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# Full Installation
#-------------------------------------------------------------------------------

install_full() {
    log_info "Installing all dependencies..."
    echo ""
    
    # Check that we have sudo
    if ! sudo -v; then
        log_error "Requires sudo permissions for full installation"
        exit 1
    fi
    
    # Update package lists
    log_info "Updating package lists..."
    sudo apt-get update -qq
    
    # Install system packages
    log_info "Installing system packages..."
    sudo apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        mininet \
        openvswitch-switch \
        tcpdump \
        wireshark-common \
        tshark \
        net-tools \
        iputils-ping \
        iproute2 \
        iperf3
    
    # Start Open vSwitch
    log_info "Starting Open vSwitch..."
    sudo systemctl enable openvswitch-switch
    sudo systemctl start openvswitch-switch
    
    # Permissions for Wireshark/tcpdump (optional)
    log_info "Configuring packet capture permissions..."
    sudo usermod -aG wireshark "$USER" 2>/dev/null || true
    
    # Install Python dependencies (from requirements.txt if it exists)
    if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
        log_info "Installing Python dependencies..."
        pip3 install -r "$PROJECT_ROOT/requirements.txt" --break-system-packages --quiet
    fi
    
    log_success "Full installation complete!"
    echo ""
    log_info "NOTE: Restart terminal to activate new groups (wireshark)"
}

#-------------------------------------------------------------------------------
# Minimal Configuration
#-------------------------------------------------------------------------------

setup_minimal() {
    log_info "Minimal configuration..."
    echo ""
    
    # Set executable permissions on scripts
    chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
    
    # Set permissions on Mininet topologies
    chmod +x "$PROJECT_ROOT/mininet/topologies/"*.py 2>/dev/null || true
    
    # Create missing directories
    mkdir -p "$PROJECT_ROOT/pcap"
    mkdir -p "$PROJECT_ROOT/solutions"
    
    log_success "Minimal configuration complete!"
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║       Week 5 Starterkit Setup — IP Addressing                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    local mode="${1:---check}"
    
    case "$mode" in
        --full)
            install_full
            check_environment
            ;;
        --minimal)
            setup_minimal
            check_environment
            ;;
        --check)
            check_environment
            ;;
        --help|-h)
            echo "Usage: $0 [--full|--minimal|--check]"
            echo ""
            echo "Options:"
            echo "  --full     Install all dependencies (requires sudo)"
            echo "  --minimal  Only verify and configure (no installations)"
            echo "  --check    Only check environment status (default)"
            ;;
        *)
            log_error "Unknown option: $mode"
            echo "Usage: $0 [--full|--minimal|--check]"
            exit 1
            ;;
    esac
}

main "$@"
