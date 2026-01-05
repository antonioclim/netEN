#!/bin/bash
# ============================================================================
# run_nat_demo.sh - Starting demonstratie NAT/PAT
# Author: Revolvix&Hypotheticalandrei
# ============================================================================

set -euo pipefail

# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
header() { echo -e "${CYAN}$1${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Banner
clear
header "╔══════════════════════════════════════════════════════════╗"
header "║      Demo NAT/PAT - Week 6                         ║"
header "║      Network Address Translation cu iptables             ║"
header "╚══════════════════════════════════════════════════════════╝"
echo ""

# Verification privilegii
if [[ $EUID -ne 0 ]]; then
    error "This script requires root privileges. Run with: sudo $0"
fi

# Functie pre-cleanup
pre_cleanup() {
    info "Cleaning previous configuration..."
    mn -c 2>/dev/null || true
    pkill -9 -f "topo_nat.py" 2>/dev/null || true
    sleep 1
    success "Environment pregatit"
}

# Verification files requirede
check_files() {
    info "Verification files..."
    
    TOPO_FILE="$PROJECT_DIR/seminar/mininet/topologies/topo_nat.py"
    if [[ ! -f "$TOPO_FILE" ]]; then
        error "Lipseste: $TOPO_FILE"
    fi
    success "Files gasite"
}

# Topology display
show_topology() {
    echo ""
    header "┌─────────────────────────────────────────────────────────┐"
    header "│                   NAT/PAT TOPOLOGY                     │"
    header "├─────────────────────────────────────────────────────────┤"
    echo "│                                                         │"
    echo "│   h1 (10.0.1.101) ─┐                                    │"
    echo "│                    ├── s1 ── rnat ── s2 ── h3           │"
    echo "│   h2 (10.0.1.102) ─┘         │             (192.168.1.103)"
    echo "│                              │                          │"
    echo "│                        MASQUERADE                       │"
    echo "│                     (192.168.1.1)                       │"
    echo "│                                                         │"
    header "├─────────────────────────────────────────────────────────┤"
    echo "│  Network privata: 10.0.1.0/24                             │"
    echo "│  Network publica: 192.168.1.0/24                          │"
    header "└─────────────────────────────────────────────────────────┘"
    echo ""
}

# Starting topology
start_topology() {
    info "Starting NAT topology..."
    
    TOPO_FILE="$PROJECT_DIR/seminar/mininet/topologies/topo_nat.py"
    
    echo ""
    header "═══════════════════════════════════════════════════════════"
    header "  MININET CLI - Useful commands:"
    header "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  📡 Test conectivitate:"
    echo "     h1 ping -c 3 192.168.1.103"
    echo "     h2 ping -c 3 192.168.1.103"
    echo ""
    echo "  🔍 Verification NAT:"
    echo "     rnat iptables -t nat -L -n -v"
    echo "     rnat conntrack -L"
    echo ""
    echo "  📊 Captura trafic:"
    echo "     rnat tcpdump -i rnat-eth0 -n icmp &"
    echo "     rnat tcpdump -i rnat-eth1 -n icmp &"
    echo ""
    echo "  🖥️ NAT Observer:"
    echo "     h3 python3 $PROJECT_DIR/seminar/python/apps/nat_observer.py server --port 8080 &"
    echo "     h1 python3 $PROJECT_DIR/seminar/python/apps/nat_observer.py client --host 192.168.1.103 --port 8080"
    echo ""
    echo "  🚪 Iesire: exit"
    echo ""
    header "═══════════════════════════════════════════════════════════"
    echo ""
    
    # Starting Mininet cu topologia
    python3 "$TOPO_FILE" --cli
}

# Functie principala
main() {
    pre_cleanup
    check_files
    show_topology
    start_topology
}

# running
main "$@"
