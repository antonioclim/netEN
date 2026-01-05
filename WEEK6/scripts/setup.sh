#!/bin/bash
# ============================================================================
# setup.sh - Environment setup for Week 6 (NAT/PAT & SDN)
# Author: Revolvix&Hypotheticalandrei
# ============================================================================

set -e  # Exit on error

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Utility functions
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Banner
echo "=============================================="
echo "  Environment Setup - Week 6: NAT/PAT & SDN"
echo "=============================================="
echo ""

# Check root privileges (for Mininet)
check_privileges() {
    if [[ $EUID -eq 0 ]]; then
        warn "Running as root. Some commands will run without sudo."
        SUDO=""
    else
        SUDO="sudo"
        info "sudo will be used for privileged commands."
    fi
}

# Check operating system
check_os() {
    info "Check operating system..."
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        success "System detected: $OS $VER"
    else
        warn "Could not detect operating system"
    fi
}

# Check and install base dependencies
install_base_deps() {
    info "Checking base dependencies..."
    
    DEPS_MISSING=()
    
    # List of required packages
    PACKAGES=(
        "python3"
        "python3-pip"
        "python3-venv"
        "net-tools"
        "iproute2"
        "iptables"
        "tcpdump"
        "tshark"
        "curl"
        "wget"
        "git"
    )
    
    for pkg in "${PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            DEPS_MISSING+=("$pkg")
        fi
    done
    
    if [[ ${#DEPS_MISSING[@]} -gt 0 ]]; then
        warn "Missing packages: ${DEPS_MISSING[*]}"
        info "Installing packages..."
        $SUDO apt-get update -qq
        $SUDO apt-get install -y "${DEPS_MISSING[@]}"
        success "Packages installed"
    else
        success "All base packages are installed"
    fi
}

# Verification si installation Mininet
install_mininet() {
    info "Checking Mininet..."
    
    if command -v mn &> /dev/null; then
        MN_VER=$(mn --version 2>/dev/null || echo "unknown")
        success "Mininet installed: $MN_VER"
    else
        warn "Mininet is not installed"
        info "Installing Mininet..."
        $SUDO apt-get install -y mininet openvswitch-switch openvswitch-testcontroller
        success "Mininet installed"
    fi
    
    # Verification OVS
    if ! systemctl is-active --quiet openvswitch-switch; then
        info "Starting Open vSwitch service..."
        $SUDO systemctl start openvswitch-switch
        $SUDO systemctl enable openvswitch-switch
    fi
    success "Open vSwitch active"
}

# Configuration Python si dependnte
setup_python() {
    info "Configuring Python environment..."
    
    # Verification Python 3
    PYTHON_VER=$(python3 --version 2>&1 | cut -d' ' -f2)
    success "Python version: $PYTHON_VER"
    
    # Installing packages Python for SDN
    info "Installing Python packages for networking..."
    
    # OS-Ken (fork Ryu for SDN)
    if ! python3 -c "import os_ken" 2>/dev/null; then
        pip3 install os-ken --break-system-packages 2>/dev/null || \
        pip3 install os-ken --user
    fi
    success "os-ken installed"
    
    # Scapy for packet crafting
    if ! python3 -c "import scapy" 2>/dev/null; then
        pip3 install scapy --break-system-packages 2>/dev/null || \
        pip3 install scapy --user
    fi
    success "scapy installed"
    
    # Mininet Python API
    if ! python3 -c "from mininet.net import Mininet" 2>/dev/null; then
        warn "Mininet Python API may require manual installation"
    else
        success "Mininet Python API available"
    fi
}

# Configuration conntrack for NAT
setup_conntrack() {
    info "Configuring conntrack for NAT monitoring..."
    
    if ! command -v conntrack &> /dev/null; then
        $SUDO apt-get install -y conntrack
    fi
    success "conntrack available"
    
    # Activare module kernel for NAT
    $SUDO modprobe nf_conntrack 2>/dev/null || true
    $SUDO modprobe nf_nat 2>/dev/null || true
}

# Configuration IP forwarding (required for NAT)
setup_ip_forwarding() {
    info "Checking IP forwarding..."
    
    FORWARD=$(cat /proc/sys/net/ipv4/ip_forward)
    if [[ "$FORWARD" == "0" ]]; then
        warn "IP forwarding disabled (normal for host)"
        info "Will be enabled in Mininet namespaces"
    else
        success "IP forwarding active"
    fi
}

# Creating working directories
setup_directories() {
    info "Creating working directories..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    mkdir -p "$PROJECT_DIR/pcap"
    mkdir -p "$PROJECT_DIR/logs"
    mkdir -p "$PROJECT_DIR/output"
    
    success "Directories created: pcap/, logs/, output/"
}

# Verification finala
final_check() {
    echo ""
    echo "=============================================="
    echo "  Final Verification"
    echo "=============================================="
    
    CHECKS_PASSED=0
    CHECKS_TOTAL=0
    
    check_cmd() {
        ((++CHECKS_TOTAL))
        if command -v "$1" &> /dev/null; then
            success "$1 available"
            ((++CHECKS_PASSED))
        else
            warn "$1 missing (optional for Week 6 if using python controllers)"
            # Do not abort setup on optional tools
        fi
    }
    
    check_python_module() {
        ((++CHECKS_TOTAL))
        if python3 -c "import $1" 2>/dev/null; then
            success "Python: $1 available"
            ((++CHECKS_PASSED))
        else
            warn "Python: $1 MISSING"
        fi
    }
    
    check_cmd "python3"
    check_cmd "mn"
    check_cmd "ovs-vsctl"
    check_cmd "tcpdump"
    check_cmd "tshark"
    check_cmd "iptables"
    check_cmd "conntrack"
    
    check_python_module "os_ken"
    check_python_module "scapy"
    
    echo ""
    echo "=============================================="
    if [[ $CHECKS_PASSED -eq $CHECKS_TOTAL ]]; then
        success "All checks passed ($CHECKS_PASSED/$CHECKS_TOTAL)"
        echo -e "${GREEN}Environment is ready for Week 6!${NC}"
    else
        warn "$CHECKS_PASSED din $CHECKS_TOTAL checks passed"
        echo -e "${YELLOW}Some components may require manual configuration.${NC}"
    fi
    echo "=============================================="
}

# Functie principala
main() {
    check_privileges
    check_os
    install_base_deps
    install_mininet
    setup_python
    setup_conntrack
    setup_ip_forwarding
    setup_directories
    final_check
}

# running
main "$@"